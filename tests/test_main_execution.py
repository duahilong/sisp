"""
main.py 执行流程测试（针对子进程返回码处理改动）
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import execute_main_logic


class TestMainExecution(unittest.TestCase):
    @patch("main.time.sleep", return_value=None)
    @patch("subprocess.Popen")
    def test_execute_main_logic_reports_nonzero_exit_code(self, mock_popen, _mock_sleep):
        """子进程非0退出码应输出失败信息。"""
        mock_process = Mock()
        mock_process.returncode = 5
        mock_process.wait.return_value = None
        mock_popen.return_value = mock_process

        with patch("builtins.print") as mock_print:
            execute_main_logic([1], "json/win11.json", "dist/main_logic_processing.exe")

        printed = "\n".join(str(call) for call in mock_print.call_args_list)
        self.assertIn("退出码: 5", printed)

    @patch("main.time.sleep", return_value=None)
    @patch("subprocess.Popen", side_effect=FileNotFoundError)
    def test_execute_main_logic_handles_missing_executable(self, _mock_popen, _mock_sleep):
        """子进程可执行文件缺失应输出错误信息。"""
        with patch("builtins.print") as mock_print:
            execute_main_logic([1], "json/win11.json", "dist/not_found.exe")

        printed = "\n".join(str(call) for call in mock_print.call_args_list)
        self.assertIn("找不到程序", printed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
