"""
main.execute_main_logic 非 Windows 分支测试
"""

import unittest
from unittest.mock import patch
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


class TestMainExecuteNonWin(unittest.TestCase):
    @patch('main.time.sleep', return_value=None)
    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd'))
    @patch('sys.platform', 'linux')
    def test_non_win_called_process_error(self, _mock_run, _mock_sleep):
        # 不抛异常即可，内部应捕获
        main.execute_main_logic([1], 'json/win11.json', 'dist/main_logic_processing.exe')


if __name__ == '__main__':
    unittest.main(verbosity=2)
