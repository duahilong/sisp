"""
call_copy.py 测试模块
使用 Mock 模拟文件操作，不涉及真实磁盘操作
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from call_copy import (
    verify_disk_letter,
    copy_software_folder,
    _sync_file_attributes,
    _copy_hidden_attributes_recursive,
)


class TestVerifyDiskLetter(unittest.TestCase):
    """测试 verify_disk_letter 函数"""

    @patch('call_copy.get_disk_manager')
    def test_drive_letter_found(self, mock_get_manager):
        mock_disk_info = Mock()
        mock_disk_info.drive_letters = "G, H"

        mock_manager = Mock()
        mock_manager.get_disk_by_index.return_value = mock_disk_info
        mock_get_manager.return_value = mock_manager

        self.assertEqual(verify_disk_letter(1), 'G')

    @patch('call_copy.get_disk_manager')
    def test_fallback_to_e_drive(self, mock_get_manager):
        mock_disk_info = Mock()
        mock_disk_info.drive_letters = "H"

        mock_manager = Mock()
        mock_manager.get_disk_by_index.return_value = mock_disk_info
        mock_get_manager.return_value = mock_manager

        self.assertEqual(verify_disk_letter(1), 'H')

    @patch('call_copy.get_disk_manager')
    def test_disk_info_not_found(self, mock_get_manager):
        mock_manager = Mock()
        mock_manager.get_disk_by_index.return_value = None
        mock_get_manager.return_value = mock_manager

        self.assertIsNone(verify_disk_letter(1))


class TestCopySoftwareFolder(unittest.TestCase):
    """测试 copy_software_folder 函数"""

    def test_source_not_exists(self):
        result = copy_software_folder(1, "C:\\NonExistent")
        self.assertFalse(result["success"])
        self.assertEqual(result["code"], "source_not_found")

    def test_source_is_not_directory(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            result = copy_software_folder(1, temp_path)
            self.assertFalse(result["success"])
            self.assertEqual(result["code"], "source_not_directory")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @patch('call_copy.verify_disk_letter')
    @patch('call_copy.os.path.exists')
    @patch('call_copy.os.path.isdir')
    @patch('call_copy.shutil.rmtree')
    @patch('call_copy.shutil.copytree')
    @patch('call_copy._copy_hidden_attributes_recursive')
    @patch('call_copy.os.listdir')
    def test_copy_success(self, mock_listdir, mock_sync_attrs, mock_copytree, mock_rmtree, mock_isdir, mock_exists, mock_verify):
        mock_verify.return_value = "G"
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["app1", "app2"]

        with tempfile.TemporaryDirectory() as temp_dir:
            result = copy_software_folder(1, temp_dir)

        self.assertTrue(result["success"])
        self.assertEqual(result["code"], "ok")
        mock_sync_attrs.assert_called_once()

    @patch('call_copy.verify_disk_letter')
    def test_verify_failed(self, mock_verify):
        mock_verify.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            result = copy_software_folder(1, temp_dir)

        self.assertFalse(result["success"])
        self.assertEqual(result["code"], "target_drive_not_found")


class TestAttributeSync(unittest.TestCase):
    """小型属性同步测试"""

    @patch('call_copy._set_windows_file_attributes')
    @patch('call_copy._get_windows_file_attributes')
    def test_sync_all_attributes(self, mock_get_attrs, mock_set_attrs):
        mock_get_attrs.return_value = 0x27

        _sync_file_attributes('src.txt', 'dst.txt')

        mock_set_attrs.assert_called_once_with('dst.txt', 0x27)

    @patch('call_copy.os.path.exists')
    @patch('call_copy.os.walk')
    @patch('call_copy._sync_file_attributes')
    def test_recursive_sync_for_root_and_children(self, mock_sync, mock_walk, mock_exists):
        mock_walk.return_value = [
            ('src', ['d1'], ['f1.txt']),
            ('src\\d1', [], ['f2.txt']),
        ]
        mock_exists.return_value = True

        _copy_hidden_attributes_recursive('src', 'dst')

        self.assertGreaterEqual(mock_sync.call_count, 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
