"""
main_logic_processing.py 单元分支测试
"""

import unittest
from unittest.mock import Mock, patch
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main_logic_processing as mlp


class TestMainLogicUnits(unittest.TestCase):
    def test_parse_capacity_invalid_type(self):
        with self.assertRaises(ValueError):
            mlp.parse_capacity_gb(123)

    @patch('main_logic_processing.get_disk_manager')
    def test_resolve_c_size_no_disk_info(self, mock_get_mgr):
        mgr = Mock()
        mgr.get_disk_by_index.return_value = None
        mock_get_mgr.return_value = mgr
        self.assertEqual(mlp.resolve_c_size(1, 153600, {'enable_dynamic_c_size': True}), 153600)

    @patch('main_logic_processing.get_disk_manager', side_effect=RuntimeError('boom'))
    def test_resolve_c_size_exception_fallback(self, _mock_mgr):
        self.assertEqual(mlp.resolve_c_size(1, 153600, {'enable_dynamic_c_size': True}), 153600)

    def test_windows_disk_to_ghost_invalid(self):
        with self.assertRaises(ValueError):
            mlp.windows_disk_to_ghost_disk(-1)

    def test_setup_json_config_without_json_arg(self):
        args = argparse.Namespace(json=None)
        self.assertEqual(mlp.setup_json_config(args), {})

    @patch('main_logic_processing.get_disk_manager')
    def test_validate_protected_disk_hit_excluded(self, mock_get_mgr):
        mgr = Mock()
        mgr.get_disk_by_index.return_value = Mock(name='DiskX')
        mgr.get_disk_by_index.return_value.name = 'DiskX'
        mock_get_mgr.return_value = mgr
        self.assertFalse(mlp.validate_protected_disk(1, {'excluded_disk_names': ['DiskX']}))

    @patch('main_logic_processing.get_disk_manager', side_effect=RuntimeError('wmi'))
    def test_validate_protected_disk_runtime_error(self, _mock_get_mgr):
        with self.assertRaises(RuntimeError):
            mlp.validate_protected_disk(1, {'excluded_disk_names': []})

    def test_custom_parser_exit_path(self):
        parser = mlp.CustomArgumentParser(prog='x')
        with patch('main_logic_processing.pause_if_interactive'), patch('main_logic_processing.sys.exit', side_effect=SystemExit(2)):
            with self.assertRaises(SystemExit):
                parser.error('bad')


if __name__ == '__main__':
    unittest.main(verbosity=2)
