"""
get_user_disknumber.py 深入分支测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import get_user_disknumber as gud


class TestGetUserDisknumberMore(unittest.TestCase):
    @patch('get_user_disknumber.get_disk_manager')
    def test_parse_all_no_disks(self, mock_get_mgr):
        mgr = Mock()
        mgr.get_disk_info.return_value = []
        mock_get_mgr.return_value = mgr
        with self.assertRaises(ValueError):
            gud.parse_disk_input('a')

    @patch('get_user_disknumber.get_disk_manager', side_effect=RuntimeError('wmi fail'))
    def test_parse_all_manager_exception(self, _mock_mgr):
        with self.assertRaises(ValueError):
            gud.parse_disk_input('all')

    def test_validate_protected_disk_invalid_inputs(self):
        with self.assertRaises(ValueError):
            gud.validate_protected_disk(0, {})
        with self.assertRaises(ValueError):
            gud.validate_protected_disk(1, {'excluded_disk_names': 'bad'})

    @patch('get_user_disknumber.get_disk_manager')
    def test_validate_protected_disk_no_disk_info(self, mock_get_mgr):
        mgr = Mock()
        mgr.get_disk_by_index.return_value = None
        mock_get_mgr.return_value = mgr
        with self.assertRaises(RuntimeError):
            gud.validate_protected_disk(1, {'excluded_disk_names': []})

    @patch('get_user_disknumber.validate_all_disks_protection', return_value=[1])
    @patch('get_user_disknumber.validate_disk_input', return_value=[1])
    def test_input_user_cli_mode(self, _mock_validate_input, _mock_validate_protection):
        self.assertEqual(gud.input_user(1, {}), [1])

    @patch('get_user_disknumber.interactive_input', return_value=None)
    def test_input_user_interactive_none(self, _mock_interactive):
        self.assertIsNone(gud.input_user(None, {}))


if __name__ == '__main__':
    unittest.main(verbosity=2)
