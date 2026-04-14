"""
disk_info.py 进一步覆盖测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.modules['wmi'] = Mock()

from disk_info import DiskManager


class TestDiskInfoMore(unittest.TestCase):
    def test_build_logical_disk_map(self):
        mgr = DiskManager()
        logical = Mock()
        logical.Caption = 'C:'
        partition = Mock()
        disk = Mock()
        disk.Index = 1
        partition.associators.return_value = [disk]
        logical.associators.return_value = [partition]
        mgr.wmi_connection.Win32_LogicalDisk.return_value = [logical]

        mapping = mgr._build_logical_disk_map()
        self.assertIn(1, mapping)
        self.assertIn('C', mapping[1])

    @patch('disk_info.DiskManager._get_partition_style', return_value='GPT')
    def test_parse_disk_info(self, _mock_style):
        mgr = DiskManager()
        disk = Mock()
        disk.Index = 1
        disk.Caption = 'Disk1'
        disk.Size = 1024 * 1024 * 1024 * 100
        info = mgr._parse_disk_info(disk, {1: ['C', 'D']})
        self.assertEqual(info.index, 1)
        self.assertEqual(info.partition_style, 'GPT')

    @patch('disk_info.DiskManager._get_partition_style', return_value='MBR')
    def test_parse_disk_info_from_cache(self, _mock_style):
        mgr = DiskManager()
        disk = Mock()
        disk.Index = 1
        disk.Caption = 'Disk1'
        disk.Size = 1024 * 1024 * 1024 * 100
        mgr._cached_logical_map = {1: ['E']}
        info = mgr._parse_disk_info_from_cache(disk)
        self.assertEqual(info.drive_letters, 'E')

    def test_get_disk_by_index_cache_path(self):
        mgr = DiskManager()
        disk = Mock()
        disk.Index = 1
        disk.Caption = 'Disk1'
        disk.Size = 1024 * 1024 * 1024 * 100
        mgr._cached_disks = [disk]
        mgr._cached_logical_map = {1: ['C']}
        mgr._cache_timestamp = __import__('time').time()
        result = mgr.get_disk_by_index(1)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
