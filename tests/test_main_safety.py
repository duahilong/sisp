"""
main.py 安全性回归测试
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


class TestMainSafety(unittest.TestCase):
    @patch("main.input")
    def test_pause_non_interactive_should_not_call_input(self, mock_input):
        fake_stdin = Mock()
        fake_stdin.isatty.return_value = False

        with patch("main.sys.stdin", fake_stdin):
            main.pause_if_interactive()

        mock_input.assert_not_called()

    def test_annotations_resolvable(self):
        """确保 Any 已正确导入，注解访问不会触发 NameError。"""
        ann = main.setup_json_config.__annotations__
        self.assertIn("return", ann)


if __name__ == "__main__":
    unittest.main(verbosity=2)
