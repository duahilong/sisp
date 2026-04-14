"""
call_ghost.py 分支覆盖测试
"""

import unittest
from unittest.mock import Mock, patch
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from call_ghost import call_ghost


class TestCallGhostBranches(unittest.TestCase):
    @patch('call_ghost.validate_windows_folder', return_value=False)
    @patch('call_ghost.subprocess.Popen')
    @patch('call_ghost.os.path.exists', return_value=True)
    def test_validation_failed_after_ghost_success(self, _mock_exists, mock_popen, _mock_validate):
        process = Mock()
        process.communicate.return_value = ("", "")
        process.returncode = 0
        mock_popen.return_value = process

        self.assertFalse(call_ghost(2, 'ghost64.exe', 'image.GHO', 'F'))

    @patch('call_ghost.subprocess.Popen')
    @patch('call_ghost.os.path.exists', return_value=True)
    def test_non_zero_return_code(self, _mock_exists, mock_popen):
        process = Mock()
        process.communicate.return_value = ("", "error")
        process.returncode = 1
        mock_popen.return_value = process

        self.assertFalse(call_ghost(2, 'ghost64.exe', 'image.GHO', 'F'))

    @patch('call_ghost.subprocess.Popen')
    @patch('call_ghost.os.path.exists', return_value=True)
    def test_timeout_kills_process(self, _mock_exists, mock_popen):
        process = Mock()
        process.communicate.side_effect = subprocess.TimeoutExpired('ghost', 1200)
        process.returncode = None
        mock_popen.return_value = process

        self.assertFalse(call_ghost(2, 'ghost64.exe', 'image.GHO', 'F'))
        process.kill.assert_called_once()

    @patch('call_ghost.subprocess.Popen', side_effect=FileNotFoundError('ghost missing'))
    @patch('call_ghost.os.path.exists', return_value=True)
    def test_popen_file_not_found(self, _mock_exists, _mock_popen):
        self.assertFalse(call_ghost(2, 'ghost64.exe', 'image.GHO', 'F'))

    @patch('call_ghost.validate_windows_folder', return_value=True)
    @patch('call_ghost.subprocess.Popen')
    @patch('call_ghost.os.path.exists', return_value=True)
    def test_disk_number_string_conversion(self, _mock_exists, mock_popen, _mock_validate):
        process = Mock()
        process.communicate.return_value = ("", "")
        process.returncode = 0
        mock_popen.return_value = process

        self.assertTrue(call_ghost('2', 'ghost64.exe', 'image.GHO', 'F'))
        cmd = mock_popen.call_args[0][0]
        self.assertIn('dst=2:2', cmd[1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
