"""
call_bcdboot.py 测试模块
使用 Mock 模拟 BCDboot 调用，不涉及真实磁盘操作
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from call_bcdboot import repair_boot_loader


class TestRepairBootLoaderMocked(unittest.TestCase):
    """使用 Mock 测试 repair_boot_loader 函数"""

    @patch('call_bcdboot.subprocess.run')
    @patch('call_bcdboot.os.path.exists')
    @patch('call_bcdboot.os.path.isdir')
    @patch('call_bcdboot.os.listdir')
    def test_bcdboot_success(self, mock_listdir, mock_isdir, mock_exists, mock_run):
        """测试 BCDboot 修复成功"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Boot files successfully created.",
            stderr=""
        )
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["Microsoft", "Boot"]
        
        result = repair_boot_loader("bcdboot.exe", "S", "F")
        
        self.assertTrue(result)

    @patch('call_bcdboot.subprocess.run')
    @patch('call_bcdboot.os.path.exists')
    @patch('call_bcdboot.os.path.isdir')
    def test_bcdboot_failure(self, mock_isdir, mock_exists, mock_run):
        """测试 BCDboot 修复失败"""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: Access denied"
        )
        
        result = repair_boot_loader("bcdboot.exe", "S", "F")
        
        self.assertFalse(result)

    @patch('call_bcdboot.subprocess.run')
    @patch('call_bcdboot.os.path.exists')
    @patch('call_bcdboot.os.path.isdir')
    def test_efi_folder_not_exists(self, mock_isdir, mock_exists, mock_run):
        """测试 EFI 文件夹不存在"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Boot files successfully created.",
            stderr=""
        )
        mock_isdir.return_value = True
        mock_exists.side_effect = [True, False]
        
        result = repair_boot_loader("bcdboot.exe", "S", "F")
        
        self.assertFalse(result)

    @patch('call_bcdboot.subprocess.run')
    @patch('call_bcdboot.os.path.exists')
    @patch('call_bcdboot.os.path.isdir')
    @patch('call_bcdboot.os.listdir')
    def test_efi_folder_empty(self, mock_listdir, mock_isdir, mock_exists, mock_run):
        """测试 EFI 文件夹为空"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Boot files successfully created.",
            stderr=""
        )
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = []
        
        result = repair_boot_loader("bcdboot.exe", "S", "F")
        
        self.assertFalse(result)

    @patch('call_bcdboot.subprocess.run')
    @patch('call_bcdboot.os.path.exists')
    @patch('call_bcdboot.os.path.isdir')
    @patch('call_bcdboot.os.listdir')
    def test_command_construction(self, mock_listdir, mock_isdir, mock_exists, mock_run):
        """测试命令参数正确传递"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["Microsoft"]
        
        repair_boot_loader("D:\\Tools\\bcdboot.exe", "E", "C")
        
        call_args = mock_run.call_args[0][0]
        self.assertIn('D:\\Tools\\bcdboot.exe', call_args)
        self.assertIn('C:\\Windows', call_args)
        self.assertIn('/s', call_args)
        self.assertIn('E:', call_args)
        self.assertIn('/f', call_args)
        self.assertIn('UEFI', call_args)


if __name__ == '__main__':
    unittest.main(verbosity=2)
