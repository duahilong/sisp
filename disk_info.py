import wmi
from tabulate import tabulate
from typing import List, Optional, Dict, Any
import subprocess


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
    
    def get_disk_info(self) -> Optional[List[DiskInfo]]:
        """
        获取所有磁盘的详细信息。
        
        Returns:
            List[DiskInfo]: 磁盘信息列表，如果获取失败则返回None
        """
        try:
            disks = self.wmi_connection.Win32_DiskDrive()
            if not disks:
                return None
            
            logical_disk_map = self._build_logical_disk_map()
            sorted_disks = sorted(disks, key=lambda disk: disk.Index)
            
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
            result = subprocess.run([
                'powershell', '-Command', 
                f'Get-Disk -Number {disk_index} | Select-Object -ExpandProperty PartitionStyle'
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                style = result.stdout.strip()
                if style in ["GPT", "MBR", "RAW"]:
                    return style
        except Exception:
            pass
        
        return "Unknown"
    
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


# 移除直接执行功能，避免重复输出
# 请使用 main.py 来运行程序
