import wmi
from tabulate import tabulate
from typing import List, Optional, Dict, Any
import subprocess
import time
import shlex

# subprocess命令模板常量
_PARTITION_STYLE_COMMAND_TEMPLATE = [
    'powershell', '-Command', 
    'Get-Disk -Number {disk_index} | Select-Object -ExpandProperty PartitionStyle'
]

# PowerShell执行常量
_POWERSHELL_TIMEOUT = 2
_PARTITION_STYLE_PATTERN = {"GPT", "MBR", "RAW"}


class DiskInfo:
    """磁盘信息类，用于存储单个磁盘的详细信息。"""
    
    def __init__(self, index: int, name: str, capacity: str, drive_letters: str, partition_style: str):
        self.index = index
        self.name = name
        self.capacity = capacity
        self.drive_letters = drive_letters
        self.partition_style = partition_style
    
    def to_list(self) -> List[Any]:
        """转换为列表格式，用于表格显示。"""
        return [self.index, self.name, self.capacity, self.drive_letters, self.partition_style]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于JSON序列化。"""
        return {
            'index': self.index,
            'name': self.name,
            'capacity': self.capacity,
            'drive_letters': self.drive_letters,
            'partition_style': self.partition_style
        }
    
    def __repr__(self) -> str:
        return f"DiskInfo(index={self.index}, name='{self.name}', capacity='{self.capacity}', drive_letters='{self.drive_letters}', partition_style='{self.partition_style}')"


class DiskManager:
    """磁盘管理器类，提供磁盘信息查询功能。"""
    
    def __init__(self):
        self.wmi_connection = wmi.WMI()
        # 缓存相关变量
        self._cached_disks = None
        self._cached_logical_map = None
        self._cached_partition_styles = {}
        self._cache_timestamp = 0
        self._cache_ttl = 30  # 缓存有效期（秒）
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效。"""
        return (self._cached_disks is not None and 
                self._cached_logical_map is not None and
                time.time() - self._cache_timestamp < self._cache_ttl)
    
    def _update_cache(self, disks, logical_map: Dict[int, List[str]]) -> None:
        """更新缓存数据。"""
        self._cached_disks = disks
        self._cached_logical_map = logical_map
        self._cache_timestamp = time.time()
    
    def get_disk_info(self) -> Optional[List[DiskInfo]]:
        """
        获取所有磁盘的详细信息。
        
        Returns:
            List[DiskInfo]: 磁盘信息列表，如果获取失败则返回None
        """
        try:
            # 检查缓存是否有效
            if self._is_cache_valid():
                # 使用缓存数据构建DiskInfo列表
                disk_info_list = []
                for disk in self._cached_disks:
                    disk_info = self._parse_disk_info_from_cache(disk)
                    if disk_info:
                        disk_info_list.append(disk_info)
                return disk_info_list
            
            # 缓存无效，重新查询
            disks = self.wmi_connection.Win32_DiskDrive()
            if not disks:
                return None
            
            logical_disk_map = self._build_logical_disk_map()
            sorted_disks = sorted(disks, key=lambda disk: disk.Index)
            
            # 更新缓存
            self._update_cache(sorted_disks, logical_disk_map)
            
            disk_info_list = []
            for disk in sorted_disks:
                disk_info = self._parse_disk_info(disk, logical_disk_map)
                if disk_info:
                    disk_info_list.append(disk_info)
            
            return disk_info_list
            
        except Exception as e:
            raise RuntimeError(f"获取磁盘信息失败: {e}")
    
    def get_disk_by_index(self, disk_index: int) -> Optional[DiskInfo]:
        """
        获取指定索引的磁盘信息。
        
        Args:
            disk_index: 磁盘索引号
            
        Returns:
            DiskInfo: 指定索引的磁盘信息，如果未找到则返回None
        """
        try:
            # 优先从缓存获取，缓存无效时重新查询
            if self._is_cache_valid():
                for disk in self._cached_disks:
                    if disk.Index == disk_index:
                        return self._parse_disk_info_from_cache(disk)
                return None  # 缓存中存在但未找到指定磁盘
            
            # 缓存无效，重新查询
            disks = self.wmi_connection.Win32_DiskDrive()
            if not disks:
                return None
            
            logical_disk_map = self._build_logical_disk_map()
            
            # 查找指定索引的磁盘
            target_disk = None
            for disk in disks:
                if disk.Index == disk_index:
                    target_disk = disk
                    break
            
            if target_disk:
                return self._parse_disk_info(target_disk, logical_disk_map)
            
            return None
            
        except Exception as e:
            raise RuntimeError(f"获取磁盘索引 {disk_index} 的信息失败: {e}")
    
    def get_disk_info_raw(self) -> Optional[List[List[Any]]]:
        """
        获取原始的磁盘信息列表格式（向后兼容）。
        
        Returns:
            List[List[Any]]: 磁盘信息二维列表，如果获取失败则返回None
        """
        disk_info_list = self.get_disk_info()
        if disk_info_list:
            return [disk.to_list() for disk in disk_info_list]
        return None
    
    def _build_logical_disk_map(self) -> Dict[int, List[str]]:
        """构建逻辑磁盘到物理磁盘的映射关系。"""
        logical_disk_map = {}
        logical_disks = self.wmi_connection.Win32_LogicalDisk()
        
        for logical in logical_disks:
            drive_letter = logical.Caption.replace(":", "")
            if not drive_letter:
                continue
                
            try:
                for partition in logical.associators(wmi_result_class="Win32_DiskPartition"):
                    for disk in partition.associators(wmi_result_class="Win32_DiskDrive"):
                        logical_disk_map.setdefault(disk.Index, []).append(drive_letter)
            except Exception as e:
                # 静默处理关联错误，避免影响主要功能
                continue
        
        return logical_disk_map
    
    def _get_partition_style(self, disk_index: int) -> str:
        """获取指定磁盘的分区表格式。"""
        try:
            # 使用模板构建命令，避免字符串拼接
            command_parts = _PARTITION_STYLE_COMMAND_TEMPLATE.copy()
            command_parts[2] = command_parts[2].format(disk_index=disk_index)
            
            result = subprocess.run(
                command_parts,
                capture_output=True, 
                text=True, 
                timeout=_POWERSHELL_TIMEOUT
            )
            
            if result.returncode == 0:
                style = result.stdout.strip()
                if style in _PARTITION_STYLE_PATTERN:
                    # 将结果缓存起来
                    self._cached_partition_styles[disk_index] = style
                    return style
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError, ValueError) as e:
            # 更精确的异常处理，避免吞没其他意外错误
            pass
        
        # 检查缓存中是否有此磁盘的分区样式
        if disk_index in self._cached_partition_styles:
            return self._cached_partition_styles[disk_index]
        
        return "Unknown"
    
    def _parse_disk_info_from_cache(self, disk) -> Optional[DiskInfo]:
        """从缓存中解析单个磁盘的信息（使用缓存的分区样式）。"""
        try:
            disk_index = disk.Index
            disk_name = disk.Caption
            total_size_gb = round(float(disk.Size) / (1024 ** 3), 2)
            capacity = f"{total_size_gb:.2f} GB"
            
            # 从缓存获取分区样式，缓存中没有时调用实际查询
            if disk_index in self._cached_partition_styles:
                partition_style = self._cached_partition_styles[disk_index]
            else:
                partition_style = self._get_partition_style(disk_index)
            
            drive_info = self._cached_logical_map.get(disk_index, [])
            drive_letters = ", ".join(sorted(list(set(drive_info)))) if drive_info else "Unknown"
            
            return DiskInfo(disk_index, disk_name, capacity, drive_letters, partition_style)
            
        except Exception as e:
            # 单个磁盘解析失败不影响其他磁盘
            return None
    
    def _parse_disk_info(self, disk, logical_disk_map: Dict[int, List[str]]) -> Optional[DiskInfo]:
        """解析单个磁盘的信息。"""
        try:
            disk_index = disk.Index
            disk_name = disk.Caption
            total_size_gb = round(float(disk.Size) / (1024 ** 3), 2)
            capacity = f"{total_size_gb:.2f} GB"
            
            partition_style = self._get_partition_style(disk_index)
            
            drive_info = logical_disk_map.get(disk_index, [])
            drive_letters = ", ".join(sorted(list(set(drive_info)))) if drive_info else "Unknown"
            
            return DiskInfo(disk_index, disk_name, capacity, drive_letters, partition_style)
            
        except Exception as e:
            # 单个磁盘解析失败不影响其他磁盘
            return None


def get_disk_info() -> Optional[List[List[Any]]]:
    """
    获取磁盘信息的兼容函数（保持原有接口）。
    
    Returns:
        List[List[Any]]: 磁盘信息二维列表，格式为：[索引, 名称, 容量, 驱动器盘符, 分区表格式]
    """
    manager = DiskManager()
    return manager.get_disk_info_raw()


def print_disk_info(data: List[List[Any]]) -> None:
    """
    打印磁盘信息表格（保持原有输出格式）。
    
    Args:
        data: 磁盘信息二维列表
    """
    if not data:
        print("未找到任何磁盘。")
        return

    headers = ["Index", "Drive Name", "Capacity", "Drive Letter", "Partition Style"]
    maxcolwidths = [8, 60, 20, 15, 25]

    print(tabulate(data, headers=headers, tablefmt="simple_grid", 
                   maxcolwidths=maxcolwidths, colalign=("center", "left", "left", "left", "left")))


