"""
call_ghost.py 测试模块
使用 Mock 模拟 Ghost 调用，不涉及真实磁盘操作
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from call_ghost import validate_windows_folder


class TestValidateWindowsFolder(unittest.TestCase):
    """测试 validate_windows_folder 函数"""

    def test_letter_without_colon(self):
        """测试不带冒号的盘符"""
        result = validate_windows_folder("C")
        self.assertIsInstance(result, bool)

    def test_letter_with_colon(self):
        """测试带冒号的盘符"""
        result = validate_windows_folder("C:")
        self.assertIsInstance(result, bool)

    @patch('call_ghost.os.path.exists')
    @patch('call_ghost.os.path.isdir')
    def test_windows_folder_not_exists(self, mock_isdir, mock_exists):
        """测试 Windows 文件夹不存在"""
        mock_exists.return_value = False
        mock_isdir.return_value = False
        
        result = validate_windows_folder("X")
        self.assertFalse(result)

    @patch('call_ghost.os.path.exists')
    @patch('call_ghost.os.path.isdir')
    @patch('call_ghost.os.listdir')
    def test_windows_folder_exists_but_empty(self, mock_listdir, mock_isdir, mock_exists):
        """测试 Windows 文件夹存在但为空"""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = []
        
        result = validate_windows_folder("X")
        self.assertFalse(result)

    @patch('call_ghost.os.path.exists')
    @patch('call_ghost.os.path.isdir')
    @patch('call_ghost.os.listdir')
    def test_windows_folder_exists_and_not_empty(self, mock_listdir, mock_isdir, mock_exists):
        """测试 Windows 文件夹存在且非空"""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["System32", "SysWOW64"]
        
        result = validate_windows_folder("X")
        self.assertTrue(result)

    @patch('call_ghost.os.path.exists')
    @patch('call_ghost.os.path.isdir')
    def test_permission_error(self, mock_isdir, mock_exists):
        """测试权限错误"""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_isdir.side_effect = PermissionError("Access denied")
        
        result = validate_windows_folder("X")
        self.assertFalse(result)


class TestCallGhostMocked(unittest.TestCase):
    """使用 Mock 测试 call_ghost 函数"""

    @patch('call_ghost.subprocess.Popen')
    @patch('call_ghost.os.path.exists')
    def test_ghost_command_construction(self, mock_exists, mock_popen):
        """测试 Ghost 命令构建"""
        from call_ghost import call_ghost
        
        mock_exists.side_effect = lambda x: True if x.endswith('.exe') or x.endswith('.GHO') else False
        
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        with patch('call_ghost.validate_windows_folder', return_value=True):
            result = call_ghost(1, "ghost64.exe", "image.GHO", "F")
        
        self.assertTrue(result)
        mock_popen.assert_called_once()
        command_args = mock_popen.call_args[0][0]
        self.assertIn("dst=1:2", command_args[1])

    @patch('call_ghost.os.path.exists')
    def test_ghost_exe_not_found(self, mock_exists):
        """测试 Ghost 可执行文件不存在"""
        from call_ghost import call_ghost
        
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError):
            call_ghost(1, "ghost64.exe", "image.GHO", "F")

    @patch('call_ghost.os.path.exists')
    def test_gho_file_not_found(self, mock_exists):
        """测试 GHO 镜像文件不存在"""
        from call_ghost import call_ghost
        
        def exists_side_effect(path):
            if path.endswith('.exe'):
                return True
            return False
        
        mock_exists.side_effect = exists_side_effect
        
        with self.assertRaises(FileNotFoundError):
            call_ghost(1, "ghost64.exe", "image.GHO", "F")

    def test_empty_parameters(self):
        """测试空参数"""
        from call_ghost import call_ghost
        
        with self.assertRaises(ValueError):
            call_ghost(1, "", "image.GHO", "F")
        
        with self.assertRaises(ValueError):
            call_ghost(1, "ghost64.exe", "", "F")

    def test_invalid_disk_number_type(self):
        """测试无效的磁盘编号类型"""
        from call_ghost import call_ghost
        
        with self.assertRaises(ValueError):
            call_ghost([1, 2], "ghost64.exe", "image.GHO", "F")


if __name__ == '__main__':
    unittest.main(verbosity=2)
