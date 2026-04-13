"""
disk_info.py 测试模块
使用 Mock 模拟 WMI 调用，不涉及真实磁盘操作
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock wmi module before importing disk_info
sys.modules['wmi'] = Mock()


class TestDiskInfo(unittest.TestCase):
    """测试 DiskInfo 类"""

    def setUp(self):
        """导入并创建测试数据"""
        from disk_info import DiskInfo
        self.DiskInfo = DiskInfo

    def test_disk_info_creation(self):
        """测试 DiskInfo 对象创建"""
        disk = self.DiskInfo(
            index=1,
            name="Test Disk",
            capacity="500.00 GB",
            drive_letters="C, D",
            partition_style="GPT"
        )
        self.assertEqual(disk.index, 1)
        self.assertEqual(disk.name, "Test Disk")
        self.assertEqual(disk.capacity, "500.00 GB")
        self.assertEqual(disk.drive_letters, "C, D")
        self.assertEqual(disk.partition_style, "GPT")

    def test_to_list(self):
        """测试 to_list 方法"""
        disk = self.DiskInfo(1, "Test", "500 GB", "C", "GPT")
        result = disk.to_list()
        self.assertEqual(result, [1, "Test", "500 GB", "C", "GPT"])

    def test_to_dict(self):
        """测试 to_dict 方法"""
        disk = self.DiskInfo(1, "Test", "500 GB", "C", "GPT")
        result = disk.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['index'], 1)
        self.assertEqual(result['name'], "Test")
        self.assertEqual(result['capacity'], "500 GB")
        self.assertEqual(result['drive_letters'], "C")
        self.assertEqual(result['partition_style'], "GPT")

    def test_repr(self):
        """测试 __repr__ 方法"""
        disk = self.DiskInfo(1, "Test", "500 GB", "C", "GPT")
        repr_str = repr(disk)
        self.assertIn("DiskInfo", repr_str)
        self.assertIn("index=1", repr_str)


class TestDiskManagerMocked(unittest.TestCase):
    """使用 Mock 测试 DiskManager 类"""

    @patch('disk_info.wmi.WMI')
    @patch('disk_info.subprocess.run')
    def test_get_disk_by_index_mock(self, mock_run, mock_wmi):
        """测试 get_disk_by_index 方法（使用 Mock）"""
        from disk_info import DiskManager
        
        mock_disk = Mock()
        mock_disk.Index = 1
        mock_disk.Caption = "Test Disk"
        mock_disk.Size = 5001073741824  # ~500GB
        
        mock_wmi_instance = Mock()
        mock_wmi_instance.Win32_DiskDrive.return_value = [mock_disk]
        mock_wmi_instance.Win32_LogicalDisk.return_value = []
        mock_wmi.return_value = mock_wmi_instance
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout="GPT",
            stderr=""
        )
        
        manager = DiskManager()
        manager.wmi_connection = mock_wmi_instance
        
        result = manager._get_partition_style(1)
        self.assertEqual(result, "GPT")

    @patch('disk_info.subprocess.run')
    def test_get_partition_style_mock(self, mock_run):
        """测试 _get_partition_style 方法（使用 Mock）"""
        from disk_info import DiskManager
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout="GPT",
            stderr=""
        )
        
        manager = DiskManager()
        result = manager._get_partition_style(1)
        
        self.assertEqual(result, "GPT")
        mock_run.assert_called_once()

    @patch('disk_info.subprocess.run')
    def test_get_partition_style_mbr(self, mock_run):
        """测试获取 MBR 分区样式"""
        from disk_info import DiskManager
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout="MBR",
            stderr=""
        )
        
        manager = DiskManager()
        result = manager._get_partition_style(2)
        
        self.assertEqual(result, "MBR")

    @patch('disk_info.subprocess.run')
    def test_get_partition_style_timeout(self, mock_run):
        """测试分区样式获取超时"""
        from disk_info import DiskManager
        import subprocess
        
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 2)
        
        manager = DiskManager()
        result = manager._get_partition_style(1)
        
        self.assertEqual(result, "Unknown")


class TestPrintDiskInfo(unittest.TestCase):
    """测试 print_disk_info 函数"""

    def test_print_with_data(self):
        """测试打印有数据的磁盘信息"""
        from disk_info import print_disk_info
        
        data = [
            [1, "Disk 1", "500 GB", "C", "GPT"],
            [2, "Disk 2", "1000 GB", "D, E", "MBR"],
        ]
        
        try:
            print_disk_info(data)
        except Exception as e:
            self.fail(f"print_disk_info 抛出异常: {e}")

    def test_print_empty_data(self):
        """测试打印空数据"""
        from disk_info import print_disk_info
        
        try:
            print_disk_info([])
            print_disk_info(None)
        except Exception as e:
            self.fail(f"print_disk_info 抛出异常: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
