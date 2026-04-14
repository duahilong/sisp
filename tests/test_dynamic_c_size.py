"""
main_logic_processing.py 动态 c_size 测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_logic_processing import get_dynamic_c_size, parse_capacity_gb, resolve_c_size


class TestDynamicCSize(unittest.TestCase):
    def test_get_dynamic_c_size_rules(self):
        self.assertEqual(get_dynamic_c_size(599.9), 153600)
        self.assertEqual(get_dynamic_c_size(600), 204800)
        self.assertEqual(get_dynamic_c_size(1199.9), 204800)
        self.assertEqual(get_dynamic_c_size(1200), 307200)

    def test_parse_capacity_gb(self):
        self.assertAlmostEqual(parse_capacity_gb("500 GB"), 500.0)
        self.assertAlmostEqual(parse_capacity_gb("1024.50 GB"), 1024.5)

    @patch('main_logic_processing.get_disk_manager')
    def test_resolve_c_size_enabled(self, mock_get_disk_manager):
        mock_disk = Mock()
        mock_disk.capacity = "700 GB"
        mock_mgr = Mock()
        mock_mgr.get_disk_by_index.return_value = mock_disk
        mock_get_disk_manager.return_value = mock_mgr

        result = resolve_c_size(1, 153600, {"enable_dynamic_c_size": True})
        self.assertEqual(result, 204800)

    def test_resolve_c_size_disabled(self):
        result = resolve_c_size(1, 153600, {"enable_dynamic_c_size": False})
        self.assertEqual(result, 153600)


if __name__ == '__main__':
    unittest.main(verbosity=2)
