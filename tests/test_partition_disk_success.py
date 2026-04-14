"""
partition_disk.py 成功路径覆盖测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from partition_disk import initialize_disk_to_partitioning_D, initialize_disk_to_partitioning_E


class TestPartitionDiskSuccess(unittest.TestCase):
    @patch('partition_disk._verify_partition_created', return_value=(True, 'ok'))
    @patch('partition_disk.execute_diskpart_command', return_value=True)
    @patch('partition_disk.get_disk_manager')
    @patch('partition_disk.is_admin', return_value=True)
    def test_d_partition_success(self, _mock_admin, mock_get_mgr, _mock_exec, _mock_verify):
        mgr = Mock()
        disk = Mock()
        disk.capacity = '800 GB'
        mgr.get_disk_by_index.return_value = disk
        mock_get_mgr.return_value = mgr
        self.assertTrue(initialize_disk_to_partitioning_D(1, 'G', 100, 153600))

    @patch('partition_disk._verify_partition_created', return_value=(False, 'bad'))
    @patch('partition_disk.execute_diskpart_command', return_value=True)
    @patch('partition_disk.get_disk_manager')
    @patch('partition_disk.is_admin', return_value=True)
    def test_d_partition_verify_fail(self, _mock_admin, mock_get_mgr, _mock_exec, _mock_verify):
        mgr = Mock()
        disk = Mock()
        disk.capacity = '800 GB'
        mgr.get_disk_by_index.return_value = disk
        mock_get_mgr.return_value = mgr
        self.assertFalse(initialize_disk_to_partitioning_D(1, 'G', 100, 153600))

    @patch('partition_disk._verify_partition_created', return_value=(True, 'ok'))
    @patch('partition_disk.execute_diskpart_command', return_value=True)
    @patch('partition_disk.is_admin', return_value=True)
    def test_e_partition_success(self, _mock_admin, _mock_exec, _mock_verify):
        self.assertTrue(initialize_disk_to_partitioning_E(1, 'H'))

    @patch('partition_disk._verify_partition_created', return_value=(False, 'bad'))
    @patch('partition_disk.execute_diskpart_command', return_value=True)
    @patch('partition_disk.is_admin', return_value=True)
    def test_e_partition_verify_fail(self, _mock_admin, _mock_exec, _mock_verify):
        self.assertFalse(initialize_disk_to_partitioning_E(1, 'H'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
