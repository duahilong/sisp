"""
call_copy.py 测试模块
使用 Mock 模拟文件操作，不涉及真实磁盘操作
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from call_copy import verify_disk_letter, copy_software_folder


class TestVerifyDiskLetter(unittest.TestCase):
    """测试 verify_disk_letter 函数"""

    @patch('call_copy.get_disk_manager')
    def test_drive_letter_found(self, mock_get_manager):
        """测试找到盘符"""
        mock_disk_info = Mock()
        mock_disk_info.drive_letters = "G, H"
        
        mock_manager = Mock()
        mock_manager.get_disk_by_index.return_value = mock_disk_info
        mock_get_manager.return_value = mock_manager
        
        result = verify_disk_letter(1)
        
        self.assertEqual(result, 'G')

    @patch('call_copy.get_disk_manager')
    def test_fallback_to_e_drive(self, mock_get_manager):
        """测试回退到 E 盘符"""
        mock_disk_info = Mock()
        mock_disk_info.drive_letters = "H"
        
        mock_manager = Mock()
        mock_manager.get_disk_by_index.return_value = mock_disk_info
        mock_get_manager.return_value = mock_manager
        
        result = verify_disk_letter(1)
        
        self.assertEqual(result, 'H')

    @patch('call_copy.get_disk_manager')
    def test_disk_info_not_found(self, mock_get_manager):
        """测试磁盘信息未找到"""
        mock_manager = Mock()
        mock_manager.get_disk_by_index.return_value = None
        mock_get_manager.return_value = mock_manager
        
        result = verify_disk_letter(1)
        
        self.assertIsNone(result)


class TestCopySoftwareFolder(unittest.TestCase):
    """测试 copy_software_folder 函数"""

    def test_source_not_exists(self):
        """测试源文件夹不存在"""
        result = copy_software_folder(1, "C:\\NonExistent")
        
        self.assertIn("错误", result)
        self.assertIn("不存在", result)

    def test_source_is_not_directory(self):
        """测试源不是文件夹"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        try:
            result = copy_software_folder(1, temp_path)
            self.assertIn("错误", result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @patch('call_copy.verify_disk_letter')
    @patch('call_copy.os.path.exists')
    @patch('call_copy.shutil.copytree')
    @patch('call_copy.os.listdir')
    def test_copy_success(self, mock_listdir, mock_copytree, mock_exists, mock_verify):
        """测试复制成功"""
        mock_verify.return_value = "G"
        mock_exists.return_value = False
        mock_listdir.return_value = ["app1", "app2"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = copy_software_folder(1, temp_dir)
        
        self.assertIn(":", result)  # 检查是否包含盘符

    @patch('call_copy.verify_disk_letter')
    def test_verify_failed(self, mock_verify):
        """测试验证失败"""
        mock_verify.return_value = None
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = copy_software_folder(1, temp_dir)
        
        self.assertIn("错误", result)

    @patch('call_copy.verify_disk_letter')
    @patch('call_copy.os.path.exists')
    @patch('call_copy.shutil.rmtree')
    @patch('call_copy.shutil.copytree')
    @patch('call_copy.os.listdir')
    def test_overwrite_existing(self, mock_listdir, mock_copytree, mock_rmtree, mock_exists, mock_verify):
        """测试覆盖已存在的文件夹"""
        mock_verify.return_value = "G"
        mock_exists.side_effect = lambda x: True if "目标" in str(x) else False
        mock_listdir.return_value = ["app1"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = copy_software_folder(1, temp_dir)
        
        mock_rmtree.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
