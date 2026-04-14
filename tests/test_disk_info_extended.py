"""
disk_info.py 额外覆盖测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.modules['wmi'] = Mock()

from disk_info import DiskManager


class TestDiskInfoExtended(unittest.TestCase):
    def test_cache_validity_toggle(self):
        mgr = DiskManager()
        self.assertFalse(mgr._is_cache_valid())

        mgr._cached_disks = [Mock()]
        mgr._cached_logical_map = {}
        mgr._cache_timestamp = __import__('time').time()
        self.assertTrue(mgr._is_cache_valid())

    @patch('disk_info.subprocess.run')
    def test_partition_style_cached_fallback(self, mock_run):
        mgr = DiskManager()
        mgr._cached_partition_styles[1] = 'GPT'
        mock_run.return_value = Mock(returncode=1, stdout='', stderr='err')
        self.assertEqual(mgr._get_partition_style(1), 'GPT')

    @patch('disk_info.subprocess.run', side_effect=__import__('subprocess').SubprocessError('boom'))
    def test_partition_style_unknown_on_exception(self, _mock_run):
        mgr = DiskManager()
        self.assertEqual(mgr._get_partition_style(1), 'Unknown')

    @patch('disk_info.DiskManager._build_logical_disk_map', return_value={1: ['C']})
    @patch('disk_info.DiskManager._parse_disk_info')
    def test_get_disk_info_query_path(self, mock_parse, _mock_map):
        mock_parse.return_value = Mock()
        mgr = DiskManager()
        disk = Mock()
        disk.Index = 1
        mgr.wmi_connection.Win32_DiskDrive.return_value = [disk]

        data = mgr.get_disk_info()
        self.assertEqual(len(data), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
