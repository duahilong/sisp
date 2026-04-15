"""
get_user_disknumber 交互异常分支补充测试
"""

import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import get_user_disknumber as gud


class TestGetUserInteractiveErrors(unittest.TestCase):
    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_interactive_keyboard_interrupt(self, _mock_input):
        self.assertIsNone(gud.interactive_input())

    @patch('builtins.input', side_effect=[Exception('boom'), '0'])
    def test_interactive_generic_exception_then_exit(self, _mock_input):
        self.assertIsNone(gud.interactive_input())


if __name__ == '__main__':
    unittest.main(verbosity=2)
