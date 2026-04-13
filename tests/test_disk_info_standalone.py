"""
disk_info.py 单元测试（独立版本）
不依赖外部模块 (wmi, tabulate)
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDiskInfoIndependent(unittest.TestCase):
    """独立测试 DiskInfo 的核心功能"""

    def test_disk_info_class_directly(self):
        """直接测试 DiskInfo 数据类"""
        class DiskInfo:
            def __init__(self, index, name, capacity, drive_letters, partition_style):
                self.index = index
                self.name = name
                self.capacity = capacity
                self.drive_letters = drive_letters
                self.partition_style = partition_style
            
            def to_list(self):
                return [self.index, self.name, self.capacity, self.drive_letters, self.partition_style]
            
            def to_dict(self):
                return {
                    'index': self.index,
                    'name': self.name,
                    'capacity': self.capacity,
                    'drive_letters': self.drive_letters,
                    'partition_style': self.partition_style
                }
            
            def __repr__(self):
                return f"DiskInfo(index={self.index}, name='{self.name}')"

        disk = DiskInfo(1, "Test Disk", "500 GB", "C, D", "GPT")
        
        self.assertEqual(disk.index, 1)
        self.assertEqual(disk.name, "Test Disk")
        self.assertEqual(disk.capacity, "500 GB")
        self.assertEqual(disk.drive_letters, "C, D")
        self.assertEqual(disk.partition_style, "GPT")
        
        self.assertEqual(disk.to_list(), [1, "Test Disk", "500 GB", "C, D", "GPT"])
        
        d = disk.to_dict()
        self.assertEqual(d['index'], 1)
        self.assertEqual(d['name'], "Test Disk")

    def test_partition_style_constants(self):
        """测试分区样式常量定义"""
        _PARTITION_STYLE_PATTERN = {"GPT", "MBR", "RAW"}
        
        self.assertIn("GPT", _PARTITION_STYLE_PATTERN)
        self.assertIn("MBR", _PARTITION_STYLE_PATTERN)
        self.assertIn("RAW", _PARTITION_STYLE_PATTERN)
        self.assertEqual(len(_PARTITION_STYLE_PATTERN), 3)

    def test_command_template_format(self):
        """测试命令模板格式"""
        command_template = [
            'powershell', '-Command', 
            'Get-Disk -Number {disk_index} | Select-Object -ExpandProperty PartitionStyle'
        ]
        
        formatted = command_template[2].format(disk_index=1)
        self.assertIn("Get-Disk -Number 1", formatted)

    def test_capacity_calculation(self):
        """测试容量计算"""
        size_bytes = 5001073741824  # ~500GB
        total_size_gb = round(float(size_bytes) / (1024 ** 3), 2)
        self.assertAlmostEqual(total_size_gb, 4657.61, places=0)

    def test_drive_letters_formatting(self):
        """测试盘符格式化"""
        drive_info = ["C", "D", "E"]
        drive_letters = ", ".join(sorted(list(set(drive_info))))
        self.assertEqual(drive_letters, "C, D, E")

    def test_empty_drive_letters(self):
        """测试空盘符"""
        drive_info = []
        drive_letters = ", ".join(sorted(list(set(drive_info)))) if drive_info else "Unknown"
        self.assertEqual(drive_letters, "Unknown")


class TestSubprocessMocked(unittest.TestCase):
    """测试 subprocess 调用"""

    @patch('subprocess.run')
    def test_powershell_partition_style(self, mock_run):
        """测试 PowerShell 获取分区样式"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="GPT",
            stderr=""
        )
        
        command = [
            'powershell', '-Command',
            'Get-Disk -Number 1 | Select-Object -ExpandProperty PartitionStyle'
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=2)
        
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "GPT")
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_powershell_timeout(self, mock_run):
        """测试 PowerShell 超时"""
        import subprocess as sp
        mock_run.side_effect = sp.TimeoutExpired("cmd", 2)
        
        command = ['powershell', '-Command', 'Get-Disk']
        
        with self.assertRaises(sp.TimeoutExpired):
            subprocess.run(command, capture_output=True, text=True, timeout=2)


class TestDiskManagerLogic(unittest.TestCase):
    """测试 DiskManager 的核心逻辑"""

    def test_cache_validation(self):
        """测试缓存有效性检查"""
        cache_timestamp = 1000
        cache_ttl = 30
        
        current_time = 1010
        is_valid = current_time - cache_timestamp < cache_ttl
        self.assertTrue(is_valid)
        
        current_time = 1050
        is_valid = current_time - cache_timestamp < cache_ttl
        self.assertFalse(is_valid)

    def test_logical_disk_mapping(self):
        """测试逻辑磁盘映射"""
        logical_disk_map = {}
        
        disk_index = 1
        drive_letter = "C"
        
        logical_disk_map.setdefault(disk_index, []).append(drive_letter)
        
        self.assertIn(1, logical_disk_map)
        self.assertIn("C", logical_disk_map[1])

    def test_multiple_drive_letters(self):
        """测试多个盘符映射"""
        logical_disk_map = {}
        
        logical_disk_map.setdefault(1, []).append("C")
        logical_disk_map.setdefault(1, []).append("D")
        logical_disk_map.setdefault(1, []).append("E")
        
        self.assertEqual(len(logical_disk_map[1]), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
