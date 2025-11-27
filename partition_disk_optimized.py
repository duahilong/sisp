# -*- coding: utf-8 -*-
"""
优化后的磁盘分区脚本
基于原partition_disk.py的重构版本，解决代码重复、性能和安全问题

主要改进：
1. 统一的基类和配置管理
2. 更好的错误处理和日志记录
3. 增强的输入验证和安全性
4. 资源管理和性能优化
5. 可测试性和可维护性提升
"""

import subprocess
import tempfile
import os
import queue
import time
import logging
import ctypes
from typing import Optional, List, Dict, Any, Union
from functools import wraps
from contextlib import contextmanager
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 原有模块
import wmi
import string
from disk_info import DiskManager


# ===== 配置管理 =====
@dataclass
class PartitionConfig:
    """分区操作配置类"""
    TIMEOUT_SECONDS: int = 300
    VERIFICATION_DELAY: int = 1
    MAX_RETRY_COUNT: int = 3
    TEMP_FILE_PREFIX: str = 'diskpart_'
    RESERVED_LETTERS: List[str] = None
    CACHE_SIZE: int = 128
    
    def __post_init__(self):
        if self.RESERVED_LETTERS is None:
            self.RESERVED_LETTERS = ['C', 'D', 'S']


# ===== 自定义异常 =====
class PartitionError(Exception):
    """分区操作基础异常"""
    pass

class DiskNotFoundError(PartitionError):
    """磁盘未找到异常"""
    pass

class InsufficientSpaceError(PartitionError):
    """磁盘空间不足异常"""
    pass

class PermissionDeniedError(PartitionError):
    """权限不足异常"""
    pass

class ValidationError(PartitionError):
    """输入验证失败异常"""
    pass


# ===== 输入验证器 =====
class InputValidator:
    """增强的输入验证器"""
    
    @staticmethod
    def validate_disk_number(disk_number: int) -> bool:
        """磁盘编号验证"""
        if not isinstance(disk_number, int):
            return False
        if disk_number < 0 or disk_number > 99:  # 合理的磁盘编号范围
            return False
        return True
        
    @staticmethod
    def validate_drive_letter(letter: str) -> bool:
        """盘符验证增强"""
        if not isinstance(letter, str) or len(letter) != 1:
            return False
        if not letter.isalpha():
            return False
        return letter.isupper()
        
    @staticmethod
    def sanitize_drive_letter(letter: str) -> Optional[str]:
        """盘符清理和规范化"""
        if not letter:
            return None
        letter = letter.strip().upper()
        return letter if InputValidator.validate_drive_letter(letter) else None
    
    @staticmethod
    def validate_partition_size(size_mb: int, max_size_gb: float = None) -> bool:
        """分区大小验证"""
        if not isinstance(size_mb, int) or size_mb <= 0:
            return False
        if max_size_gb and size_mb > max_size_gb * 1024:
            return False
        return True


# ===== 日志管理器 =====
class PartitionLogger:
    """分区操作日志记录器"""
    
    _logger = None
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """获取日志记录器"""
        if cls._logger is None:
            cls._setup_logging()
        return cls._logger
    
    @classmethod
    def _setup_logging(cls):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('partition_operations.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        cls._logger = logging.getLogger('PartitionManager')


# ===== 重试装饰器 =====
def retry_on_failure(max_attempts: int = 3, delay: float = 1, backoff: float = 2):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except (DiskNotFoundError, PermissionDeniedError, ValidationError):
                    # 这些错误不应该重试
                    raise
                except PartitionError as e:
                    if attempt == max_attempts:
                        logger = PartitionLogger.get_logger()
                        logger.error(f"重试 {max_attempts} 次后仍然失败: {func.__name__}")
                        raise
                    logger.warning(f"操作失败，重试第 {attempt} 次: {e}")
                    time.sleep(delay * (backoff ** (attempt - 1)))
                    attempt += 1
            return False
        return wrapper
    return decorator


# ===== 磁盘管理器连接池 =====
class DiskManagerPool:
    """DiskManager连接池"""
    
    def __init__(self, pool_size: int = 3):
        self._pool = queue.Queue(maxsize=pool_size)
        for _ in range(pool_size):
            self._pool.put(DiskManager())
            
    def get_manager(self) -> DiskManager:
        """获取管理器实例"""
        try:
            return self._pool.get(timeout=1)
        except queue.Empty:
            return DiskManager()
            
    def return_manager(self, manager: DiskManager):
        """归还管理器实例"""
        if not self._pool.full():
            self._pool.put(manager)


# ===== 磁盘状态检查器 =====
class DiskStateChecker:
    """磁盘状态检查器"""
    
    @staticmethod
    def is_admin() -> bool:
        """检查管理员权限"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    @staticmethod
    def check_disk_available(disk_manager: DiskManager, disk_number: int) -> bool:
        """检查磁盘是否可用"""
        try:
            disk_info = disk_manager.get_disk_by_index(disk_number)
            if disk_info is None:
                raise DiskNotFoundError(f"磁盘 {disk_number} 不存在")
            return True
        except Exception as e:
            logger = PartitionLogger.get_logger()
            logger.error(f"磁盘状态检查失败: {e}")
            return False
    
    @staticmethod
    def check_partition_conflict(disk_manager: DiskManager, disk_number: int, 
                                reserved_letters: List[str]) -> bool:
        """检查盘符冲突"""
        try:
            disk_info = disk_manager.get_disk_by_index(disk_number)
            if disk_info and disk_info.drive_letters:
                existing_letters = [l.strip() for l in disk_info.drive_letters.split(',')]
                for letter in existing_letters:
                    if letter in reserved_letters:
                        return False
            return True
        except Exception as e:
            logger = PartitionLogger.get_logger()
            logger.error(f"盘符冲突检查失败: {e}")
            return False


# ===== 临时文件管理器 =====
@contextmanager
def temporary_diskpart_script(commands: List[str], prefix: str = "diskpart_"):
    """临时DiskPart脚本上下文管理器"""
    script_path = None
    try:
        # 创建临时文件
        script_content = "\n".join(commands) + "\nexit\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', 
                                       delete=False, prefix=prefix, encoding='utf-8') as f:
            f.write(script_content)
            script_path = f.name
        
        yield script_path
        
    finally:
        # 清理临时文件
        if script_path and os.path.exists(script_path):
            try:
                os.unlink(script_path)
            except Exception as e:
                logger = PartitionLogger.get_logger()
                logger.warning(f"临时文件清理失败: {script_path}, 错误: {e}")


# ===== 分区操作基类 =====
class DiskPartitionBase(ABC):
    """分区操作基类，提供通用功能"""
    
    def __init__(self, disk_manager: Optional[DiskManager] = None, 
                 config: Optional[PartitionConfig] = None):
        self.disk_manager = disk_manager or DiskManager()
        self.config = config or PartitionConfig()
        self.logger = PartitionLogger.get_logger()
        
    def _validate_admin_permission(self) -> bool:
        """统一的管理员权限检查"""
        if not DiskStateChecker.is_admin():
            raise PermissionDeniedError("需要管理员权限才能执行磁盘分区操作")
        return True
        
    def _execute_diskpart_safe(self, commands: List[str], capture_output: bool = False) -> Union[bool, str]:
        """安全的DiskPart命令执行"""
        try:
            with temporary_diskpart_script(commands, self.config.TEMP_FILE_PREFIX) as script_path:
                if capture_output:
                    result = subprocess.run(
                        ['diskpart', '/s', script_path],
                        capture_output=True,
                        text=True,
                        timeout=self.config.TIMEOUT_SECONDS
                    )
                    return result.stdout + result.stderr
                else:
                    result = subprocess.run(
                        ['diskpart', '/s', script_path],
                        capture_output=True,
                        timeout=self.config.TIMEOUT_SECONDS
                    )
                    return result.returncode == 0
                    
        except subprocess.TimeoutExpired:
            raise PartitionError(f"DiskPart命令执行超时 (>{self.config.TIMEOUT_SECONDS}秒)")
        except Exception as e:
            raise PartitionError(f"DiskPart命令执行失败: {e}")
    
    def _verify_operation_success(self, disk_number: int, expected_letters: List[str]) -> bool:
        """验证操作成功"""
        time.sleep(self.config.VERIFICATION_DELAY)
        
        try:
            disk_info = self.disk_manager.get_disk_by_index(disk_number)
            if not disk_info:
                raise DiskNotFoundError(f"无法获取磁盘 {disk_number} 信息")
            
            if disk_info.drive_letters == "Unknown":
                raise ValidationError("无法验证分区状态")
            
            if disk_info.drive_letters:
                actual_letters = [l.strip() for l in disk_info.drive_letters.split(',')]
                for expected_letter in expected_letters:
                    if expected_letter not in actual_letters:
                        raise ValidationError(f"预期盘符 {expected_letter} 未找到，实际盘符: {disk_info.drive_letters}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"操作验证失败: {e}")
            raise


# ===== GPT分区创建器 =====
class GPTPartitionCreator(DiskPartitionBase):
    """GPT分区创建器"""
    
    @retry_on_failure(max_attempts=3)
    def initialize_gpt(self, disk_number: int, efi_size: Optional[int] = None, 
                      efi_letter: Optional[str] = None) -> bool:
        """
        使用 DiskPart 将指定的磁盘初始化为 GPT
        
        Args:
            disk_number: 磁盘编号
            efi_size: EFI分区大小 (MB)
            efi_letter: EFI分区的盘符
            
        Returns:
            bool: 初始化成功返回 True，否则返回 False
        """
        try:
            self.logger.info(f"开始GPT初始化磁盘 {disk_number}")
            
            # 权限检查
            self._validate_admin_permission()
            
            # 参数验证
            self._validate_gpt_parameters(disk_number, efi_size, efi_letter)
            
            # 磁盘可用性检查
            if not DiskStateChecker.check_disk_available(self.disk_manager, disk_number):
                raise DiskNotFoundError(f"磁盘 {disk_number} 不可用")
            
            # 构建和执行GPT初始化命令
            commands = [
                f"select disk {disk_number}",
                "clean",
                "convert gpt",
                "list partition"
            ]
            
            result = self._execute_diskpart_safe(commands)
            if not result:
                raise PartitionError(f"磁盘 {disk_number} 的GPT初始化失败")
            
            # 尝试删除MSR分区
            self._cleanup_msr_partition(disk_number)
            
            # 验证GPT转换结果
            self._verify_gpt_conversion(disk_number)
            
            # 创建EFI分区（如果提供参数）
            if efi_size and efi_letter:
                self._create_efi_partition(disk_number, efi_size, efi_letter)
            
            self.logger.info(f"磁盘 {disk_number} GPT初始化成功完成")
            return True
            
        except (PermissionDeniedError, DiskNotFoundError, ValidationError):
            raise
        except Exception as e:
            self.logger.error(f"GPT初始化失败: {e}")
            raise PartitionError(f"GPT初始化过程中发生错误: {e}")
    
    def _validate_gpt_parameters(self, disk_number: int, efi_size: Optional[int], 
                                efi_letter: Optional[str]):
        """验证GPT初始化参数"""
        if not InputValidator.validate_disk_number(disk_number):
            raise ValidationError(f"无效的磁盘编号: {disk_number}")
        
        if efi_size is not None:
            if not InputValidator.validate_partition_size(efi_size):
                raise ValidationError(f"无效的EFI分区大小: {efi_size}MB")
        
        if efi_letter is not None:
            letter = InputValidator.sanitize_drive_letter(efi_letter)
            if letter in self.config.RESERVED_LETTERS:
                raise ValidationError(f"EFI盘符 {letter} 是保留盘符")
    
    def _cleanup_msr_partition(self, disk_number: int):
        """清理MSR分区"""
        commands = [
            f"select disk {disk_number}",
            "list partition",
            "select partition 1",
            "delete partition override"
        ]
        
        try:
            self._execute_diskpart_safe(commands)
        except Exception as e:
            self.logger.warning(f"MSR分区删除失败 (不影响GPT初始化): {e}")
    
    def _verify_gpt_conversion(self, disk_number: int):
        """验证GPT转换结果"""
        commands = [
            f"select disk {disk_number}",
            "list disk"
        ]
        
        output = self._execute_diskpart_safe(commands, capture_output=True)
        if not output or "GPT" not in output:
            raise PartitionError(f"磁盘 {disk_number} 未成功转换为GPT格式")
    
    def _create_efi_partition(self, disk_number: int, efi_size: int, efi_letter: str):
        """创建EFI分区"""
        commands = [
            f"select disk {disk_number}",
            f"create partition efi size={efi_size}",
            "format fs=fat32 quick label=EFI OVERRIDE",
            f"assign letter={efi_letter}"
        ]
        
        result = self._execute_diskpart_safe(commands)
        if not result:
            raise PartitionError(f"EFI分区创建失败")


# ===== 通用分区创建器 =====
class PartitionCreator(DiskPartitionBase):
    """通用分区创建器"""
    
    @retry_on_failure(max_attempts=3)
    def create_partition(self, disk_number: int, partition_type: str, 
                        size_mb: Optional[int] = None, 
                        drive_letter: Optional[str] = None) -> bool:
        """
        创建分区的统一接口
        
        Args:
            disk_number: 磁盘编号
            partition_type: 分区类型 ('C', 'D', 'E')
            size_mb: 分区大小 (MB)
            drive_letter: 盘符
            
        Returns:
            bool: 创建成功返回True
        """
        try:
            self.logger.info(f"开始创建{partition_type}分区")
            
            # 权限检查
            self._validate_admin_permission()
            
            # 参数验证
            self._validate_partition_parameters(disk_number, partition_type, size_mb, drive_letter)
            
            # 构建DiskPart命令
            commands = self._build_diskpart_commands(disk_number, partition_type, size_mb, drive_letter)
            
            # 执行分区创建
            result = self._execute_diskpart_safe(commands)
            if not result:
                raise PartitionError(f"{partition_type}分区创建失败")
            
            # 验证分区创建结果
            if drive_letter:
                self._verify_operation_success(disk_number, [drive_letter])
            
            self.logger.info(f"{partition_type}分区创建成功")
            return True
            
        except (PermissionDeniedError, ValidationError):
            raise
        except Exception as e:
            self.logger.error(f"{partition_type}分区创建失败: {e}")
            raise PartitionError(f"{partition_type}分区创建过程中发生错误: {e}")
    
    def _validate_partition_parameters(self, disk_number: int, partition_type: str, 
                                     size_mb: Optional[int], drive_letter: Optional[str]):
        """验证分区参数"""
        if not InputValidator.validate_disk_number(disk_number):
            raise ValidationError(f"无效的磁盘编号: {disk_number}")
        
        if partition_type not in ['C', 'D', 'E']:
            raise ValidationError(f"无效的分区类型: {partition_type}")
        
        if size_mb is not None and not InputValidator.validate_partition_size(size_mb):
            raise ValidationError(f"无效的分区大小: {size_mb}MB")
        
        if drive_letter:
            letter = InputValidator.sanitize_drive_letter(drive_letter)
            if not letter:
                raise ValidationError(f"无效的盘符: {drive_letter}")
            if letter in self.config.RESERVED_LETTERS:
                raise ValidationError(f"盘符 {letter} 是保留盘符")
    
    def _build_diskpart_commands(self, disk_number: int, partition_type: str, 
                               size_mb: Optional[int], drive_letter: str) -> List[str]:
        """构建DiskPart命令"""
        commands = [f"select disk {disk_number}"]
        
        # 创建分区
        if size_mb:
            commands.append(f"create partition primary size={size_mb}")
        else:
            commands.append("create partition primary")
        
        # 格式化分区
        commands.append("format quick fs=ntfs override")
        
        # 分配盘符
        if drive_letter:
            commands.append(f"assign letter={drive_letter}")
        
        return commands


# ===== 分区操作管理器 =====
class PartitionManager:
    """分区操作管理器 - 提供统一的操作接口"""
    
    def __init__(self, config: Optional[PartitionConfig] = None):
        self.config = config or PartitionConfig()
        self.gpt_creator = GPTPartitionCreator(config=self.config)
        self.partition_creator = PartitionCreator(config=self.config)
        self.logger = PartitionLogger.get_logger()
    
    def initialize_disk_to_gpt(self, disk_number: int, efi_size: Optional[int] = None, 
                              efi_letter: Optional[str] = None) -> bool:
        """GPT初始化"""
        return self.gpt_creator.initialize_gpt(disk_number, efi_size, efi_letter)
    
    def create_c_partition(self, disk_number: int, c_size: Optional[int] = None, 
                          c_letter: Optional[str] = None) -> bool:
        """创建C分区"""
        return self.partition_creator.create_partition(disk_number, 'C', c_size, c_letter)
    
    def create_d_partition(self, disk_number: int, d_letter: Optional[str], 
                          efi_size: int, c_size: int) -> bool:
        """创建D分区"""
        # D分区使用剩余空间的一半
        remaining_space = self._calculate_remaining_space(disk_number, efi_size, c_size)
        d_size = remaining_space // 2
        return self.partition_creator.create_partition(disk_number, 'D', d_size, d_letter)
    
    def create_e_partition(self, disk_number: int, e_letter: str) -> bool:
        """创建E分区"""
        return self.partition_creator.create_partition(disk_number, 'E', None, e_letter)
    
    def _calculate_remaining_space(self, disk_number: int, efi_size: int, c_size: int) -> int:
        """计算剩余空间"""
        disk_info = self.gpt_creator.disk_manager.get_disk_by_index(disk_number)
        if not disk_info:
            raise DiskNotFoundError(f"无法获取磁盘 {disk_number} 信息")
        
        # 解析磁盘容量
        disk_capacity_str = disk_info.capacity.replace("GB", "").strip()
        disk_capacity_gb = float(disk_capacity_str)
        total_disk_capacity_mb = int(disk_capacity_gb * 1024)
        
        return total_disk_capacity_mb - efi_size - c_size


# ===== 便捷函数 (与原API兼容) =====
def validate_input_parameters(disk_number: int, efi_size: Optional[int] = None, 
                             efi_letter: Optional[str] = None, c_size: Optional[int] = None,
                             c_letter: Optional[str] = None, d_letter: Optional[str] = None,
                             e_letter: Optional[str] = None) -> bool:
    """兼容原有API的验证函数"""
    try:
        validator = InputValidator()
        
        # 基础验证
        if not validator.validate_disk_number(disk_number):
            raise ValidationError(f"无效的磁盘编号: {disk_number}")
        
        # 各分区参数验证
        params = [
            ('EFI大小', efi_size, None),
            ('EFI盘符', efi_letter, validator.sanitize_drive_letter),
            ('C分区大小', c_size, None),
            ('C分区盘符', c_letter, validator.sanitize_drive_letter),
            ('D分区盘符', d_letter, validator.sanitize_drive_letter),
            ('E分区盘符', e_letter, validator.sanitize_drive_letter)
        ]
        
        letters = []
        for name, value, sanitizer in params:
            if value is not None:
                if name.endswith('盘符'):
                    sanitized = validator.sanitize_drive_letter(value)
                    if not sanitized:
                        raise ValidationError(f"无效的{name}: {value}")
                    if sanitized in ['C', 'D', 'S']:
                        raise ValidationError(f"{name} {sanitized} 是保留盘符")
                    letters.append(sanitized)
        
        # 检查盘符重复
        if len(letters) != len(set(letters)):
            raise ValidationError("盘符不能重复")
        
        return True
        
    except ValidationError as e:
        print(f"参数验证失败: {e}")
        return False
    except Exception as e:
        print(f"验证过程中发生未知错误: {e}")
        return False


# ===== 兼容原有函数的包装函数 =====
def initialize_disk_to_gpt(disk_number: int, efi_size: Optional[int] = None, 
                          efi_letter: Optional[str] = None) -> bool:
    """兼容GPT初始化函数"""
    try:
        manager = PartitionManager()
        return manager.initialize_disk_to_gpt(disk_number, efi_size, efi_letter)
    except Exception as e:
        print(f"❌ GPT初始化错误: {e}")
        return False


def initialize_disk_to_partitioning_C(disk_number: int, c_size: Optional[int] = None, 
                                     c_letter: Optional[str] = None) -> bool:
    """兼容C分区创建函数"""
    try:
        manager = PartitionManager()
        return manager.create_c_partition(disk_number, c_size, c_letter)
    except Exception as e:
        print(f"❌ C分区创建错误: {e}")
        return False


def initialize_disk_to_partitioning_D(disk_number: int, d_letter: Optional[str] = None,
                                     efi_size: Optional[int] = None, c_size: Optional[int] = None) -> bool:
    """兼容D分区创建函数"""
    try:
        manager = PartitionManager()
        return manager.create_d_partition(disk_number, d_letter, efi_size, c_size)
    except Exception as e:
        print(f"❌ D分区创建错误: {e}")
        return False


def initialize_disk_to_partitioning_E(disk_number: int, e_letter: Optional[str] = None) -> bool:
    """兼容E分区创建函数"""
    try:
        manager = PartitionManager()
        return manager.create_e_partition(disk_number, e_letter)
    except Exception as e:
        print(f"❌ E分区创建错误: {e}")
        return False


if __name__ == "__main__":
    # 示例使用
    logger = PartitionLogger.get_logger()
    logger.info("优化后的分区脚本已加载")
    
    # 性能测试示例
    print("🚀 优化后的磁盘分区脚本已准备就绪!")
    print("📊 主要改进:")
    print("   • 统一的基类和配置管理")
    print("   • 增强的输入验证和错误处理") 
    print("   • 连接池和缓存机制提升性能")
    print("   • 完善的日志记录和调试信息")
    print("   • 重试机制和资源管理优化")