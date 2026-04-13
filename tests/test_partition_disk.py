"""
partition_disk.py 测试模块
使用 Mock 模拟 DiskPart 调用，不涉及真实磁盘操作
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from partition_disk import (
    is_admin,
    _validate_partition_letter,
)


class TestIsAdmin(unittest.TestCase):
    """测试 is_admin 函数"""

    def test_is_admin_returns_bool(self):
        """测试 is_admin 返回布尔值"""
        result = is_admin()
        self.assertIsInstance(result, bool)


class TestValidatePartitionLetter(unittest.TestCase):
    """测试 _validate_partition_letter 函数"""

    def test_valid_uppercase_letter(self):
        """测试有效的大写字母"""
        _validate_partition_letter('C', 'C分区盘符')
        _validate_partition_letter('Z', 'Z分区盘符')

    def test_invalid_type(self):
        """测试无效类型"""
        with self.assertRaises(ValueError):
            _validate_partition_letter(123, '测试盘符')
        
        with self.assertRaises(ValueError):
            _validate_partition_letter('CD', '测试盘符')

    def test_lowercase_letter(self):
        """测试小写字母"""
        with self.assertRaises(ValueError):
            _validate_partition_letter('c', '测试盘符')

    def test_special_characters(self):
        """测试特殊字符"""
        with self.assertRaises(ValueError):
            _validate_partition_letter('1', '测试盘符')


class TestInitializeDiskToGPTMocked(unittest.TestCase):
    """使用 Mock 测试 initialize_disk_to_gpt 函数"""

    @patch('partition_disk.is_admin')
    @patch('partition_disk.get_disk_manager')
    @patch('partition_disk.execute_diskpart_command')
    def test_gpt_initialization_success(self, mock_exec, mock_get_manager, mock_admin):
        """测试 GPT 初始化成功"""
        from partition_disk import initialize_disk_to_gpt
        
        mock_admin.return_value = True
        
        mock_disk_info = Mock()
        mock_disk_info.capacity = "500.00 GB"
        
        mock_manager = Mock()
        mock_manager.get_disk_by_index.return_value = mock_disk_info
        mock_manager._get_partition_style.return_value = "GPT"
        mock_get_manager.return_value = mock_manager
        
        mock_exec.return_value = True
        
        result = initialize_disk_to_gpt(1, 100, 'E')
        
        self.assertTrue(result)

    @patch('partition_disk.is_admin')
    def test_requires_admin(self, mock_admin):
        """测试需要管理员权限"""
        from partition_disk import initialize_disk_to_gpt
        
        mock_admin.return_value = False
        
        result = initialize_disk_to_gpt(1, 100, 'E')
        
        self.assertFalse(result)


class TestInitializeDiskToPartitioningCMocked(unittest.TestCase):
    """使用 Mock 测试 initialize_disk_to_partitioning_C 函数"""

    @patch('partition_disk.is_admin')
    @patch('partition_disk.get_disk_manager')
    @patch('partition_disk.execute_diskpart_command')
    def test_c_partition_success(self, mock_exec, mock_get_manager, mock_admin):
        """测试 C 分区创建成功"""
        from partition_disk import initialize_disk_to_partitioning_C
        
        mock_admin.return_value = True
        
        mock_disk_info = Mock()
        mock_disk_info.drive_letters = "F"
        
        mock_manager = Mock()
        mock_manager.get_disk_by_index.return_value = mock_disk_info
        mock_get_manager.return_value = mock_manager
        
        mock_exec.return_value = True
        
        result = initialize_disk_to_partitioning_C(1, 1536, 'F')
        
        self.assertTrue(result)

    @patch('partition_disk.is_admin')
    def test_c_partition_invalid_size(self, mock_admin):
        """测试 C 分区无效大小"""
        from partition_disk import initialize_disk_to_partitioning_C
        
        mock_admin.return_value = True
        
        result = initialize_disk_to_partitioning_C(1, -100, 'F')
        
        self.assertFalse(result)

    @patch('partition_disk.is_admin')
    def test_c_partition_requires_admin(self, mock_admin):
        """测试 C 分区需要管理员权限"""
        from partition_disk import initialize_disk_to_partitioning_C
        
        mock_admin.return_value = False
        
        result = initialize_disk_to_partitioning_C(1, 1536, 'F')
        
        self.assertFalse(result)


class TestExecuteDiskpartCommandMocked(unittest.TestCase):
    """测试 execute_diskpart_command 函数"""

    @patch('partition_disk.subprocess.run')
    @patch('partition_disk.tempfile.NamedTemporaryFile')
    @patch('partition_disk.os.unlink')
    def test_execute_success(self, mock_unlink, mock_tempfile, mock_run):
        """测试命令执行成功"""
        from partition_disk import execute_diskpart_command
        
        mock_file = Mock()
        mock_file.name = 'temp_script.txt'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        mock_run.return_value = Mock(returncode=0)
        
        result = execute_diskpart_command(["select disk 1", "clean"])
        
        self.assertTrue(result)

    @patch('partition_disk.subprocess.run')
    @patch('partition_disk.tempfile.NamedTemporaryFile')
    @patch('partition_disk.os.unlink')
    def test_execute_failure(self, mock_unlink, mock_tempfile, mock_run):
        """测试命令执行失败"""
        from partition_disk import execute_diskpart_command
        
        mock_file = Mock()
        mock_file.name = 'temp_script.txt'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        mock_run.return_value = Mock(returncode=1)
        
        result = execute_diskpart_command(["select disk 1", "invalid_command"])
        
        self.assertFalse(result)

    @patch('partition_disk.subprocess.run')
    @patch('partition_disk.tempfile.NamedTemporaryFile')
    @patch('partition_disk.os.unlink')
    def test_capture_output(self, mock_unlink, mock_tempfile, mock_run):
        """测试捕获输出"""
        from partition_disk import execute_diskpart_command
        
        mock_file = Mock()
        mock_file.name = 'temp_script.txt'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout="DiskPart succeeded.",
            stderr=""
        )
        
        result = execute_diskpart_command(["list disk"], capture_output=True)
        
        self.assertIsInstance(result, str)
        self.assertIn("DiskPart", result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
