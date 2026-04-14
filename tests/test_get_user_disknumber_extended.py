"""
get_user_disknumber.py 交互与保护分支测试
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_user_disknumber import interactive_input, validate_all_disks_protection


class TestUserInputExtended(unittest.TestCase):
    @patch('builtins.input', side_effect=['0'])
    def test_interactive_exit(self, _mock_input):
        self.assertIsNone(interactive_input())

    @patch('builtins.input', side_effect=['abc', '1'])
    def test_interactive_retry_then_success(self, _mock_input):
        self.assertEqual(interactive_input(), [1])

    @patch('get_user_disknumber.validate_protected_disk')
    def test_validate_all_disks_protection_filters(self, mock_validate):
        mock_validate.side_effect = [True, False, True]
        self.assertEqual(validate_all_disks_protection([1, 2, 3], {}), [1, 3])


if __name__ == '__main__':
    unittest.main(verbosity=2)
