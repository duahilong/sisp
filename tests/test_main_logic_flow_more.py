"""
main_logic_processing.py 流程分支补充测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_logic_processing import all_disk_partitions


def _letters(_disk, letter_type):
    return {'efi': 'E', 'c': 'F', 'd': 'G', 'e': 'H'}[letter_type]


class TestMainLogicFlowMore(unittest.TestCase):
    @patch('main_logic_processing.get_disk_letter', side_effect=_letters)
    @patch('main_logic_processing.get_disk_manager')
    def test_all_partitions_no_disk_info(self, mock_get_mgr, _mock_letters):
        mgr = Mock()
        mgr.get_disk_by_index.return_value = None
        mock_get_mgr.return_value = mgr
        self.assertFalse(all_disk_partitions(1, 100, 153600))

    @patch('main_logic_processing.get_disk_letter', side_effect=_letters)
    @patch('main_logic_processing.get_disk_manager')
    @patch('main_logic_processing.initialize_disk_to_gpt', return_value=False)
    @patch('main_logic_processing.initialize_disk_to_partitioning_C')
    def test_stop_when_gpt_failed(self, mock_c, _mock_gpt, mock_get_mgr, _mock_letters):
        mgr = Mock()
        disk = Mock()
        disk.capacity = '800 GB'
        mgr.get_disk_by_index.return_value = disk
        mock_get_mgr.return_value = mgr
        self.assertFalse(all_disk_partitions(1, 100, 153600))
        mock_c.assert_not_called()

    @patch('main_logic_processing.get_disk_letter', side_effect=_letters)
    @patch('main_logic_processing.get_disk_manager')
    @patch('main_logic_processing.initialize_disk_to_gpt', return_value=True)
    @patch('main_logic_processing.initialize_disk_to_partitioning_C', return_value=True)
    @patch('main_logic_processing.initialize_disk_to_partitioning_D', return_value=True)
    @patch('main_logic_processing.initialize_disk_to_partitioning_E', return_value=False)
    def test_stop_when_e_failed(self, _mock_e, _mock_d, _mock_c, _mock_gpt, mock_get_mgr, _mock_letters):
        mgr = Mock()
        disk = Mock()
        disk.capacity = '800 GB'
        mgr.get_disk_by_index.return_value = disk
        mock_get_mgr.return_value = mgr
        self.assertFalse(all_disk_partitions(1, 100, 153600))


if __name__ == '__main__':
    unittest.main(verbosity=2)
