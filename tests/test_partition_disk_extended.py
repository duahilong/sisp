"""
partition_disk.py 扩展分支测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from partition_disk import initialize_disk_to_partitioning_D, initialize_disk_to_partitioning_E


class TestPartitionDiskExtended(unittest.TestCase):
    @patch('partition_disk.is_admin', return_value=False)
    def test_d_partition_requires_admin(self, _mock_admin):
        self.assertFalse(initialize_disk_to_partitioning_D(1, 'G', 100, 153600))

    @patch('partition_disk.is_admin', return_value=True)
    def test_d_partition_missing_params_returns_false(self, _mock_admin):
        self.assertFalse(initialize_disk_to_partitioning_D(1, None, 100, 153600))

    @patch('partition_disk.is_admin', return_value=True)
    def test_d_partition_invalid_sizes(self, _mock_admin):
        self.assertFalse(initialize_disk_to_partitioning_D(1, 'G', 0, 153600))

    @patch('partition_disk.is_admin', return_value=True)
    @patch('partition_disk.get_disk_manager')
    def test_d_partition_no_disk_info(self, mock_get_mgr, _mock_admin):
        mgr = Mock()
        mgr.get_disk_by_index.return_value = None
        mock_get_mgr.return_value = mgr
        self.assertFalse(initialize_disk_to_partitioning_D(1, 'G', 100, 153600))

    @patch('partition_disk.is_admin', return_value=True)
    @patch('partition_disk.get_disk_manager')
    def test_d_partition_invalid_calculated_size(self, mock_get_mgr, _mock_admin):
        mgr = Mock()
        disk = Mock()
        disk.capacity = '100 GB'
        mgr.get_disk_by_index.return_value = disk
        mock_get_mgr.return_value = mgr
        self.assertFalse(initialize_disk_to_partitioning_D(1, 'G', 1000, 200000))

    @patch('partition_disk.is_admin', return_value=False)
    def test_e_partition_requires_admin(self, _mock_admin):
        self.assertFalse(initialize_disk_to_partitioning_E(1, 'H'))

    @patch('partition_disk.is_admin', return_value=True)
    def test_e_partition_missing_letter(self, _mock_admin):
        self.assertFalse(initialize_disk_to_partitioning_E(1, None))

    @patch('partition_disk.is_admin', return_value=True)
    @patch('partition_disk.execute_diskpart_command', return_value=False)
    def test_e_partition_execute_fail(self, _mock_exec, _mock_admin):
        self.assertFalse(initialize_disk_to_partitioning_E(1, 'H'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
