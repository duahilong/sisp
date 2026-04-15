"""
main_logic_processing 高价值路径测试
1) 配置错误 -> 提前退出
2) Ghost失败 -> 不执行 bcdboot
"""

import unittest
from unittest.mock import Mock, patch
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main_logic_processing as mlp


class TestMainLogicHighValue(unittest.TestCase):
    @patch('main_logic_processing.pause_if_interactive')
    @patch('main_logic_processing.validate_main_config', side_effect=ValueError('bad config'))
    @patch('main_logic_processing.setup_json_config', return_value={'efi_size': 100})
    @patch('main_logic_processing.parse_arguments', return_value=argparse.Namespace(disk=1, json='json/win11.json'))
    def test_main_entry_invalid_config_early_exit(
        self,
        _mock_parse,
        _mock_setup,
        _mock_validate,
        _mock_pause,
    ):
        rc = mlp.main_entry()
        self.assertEqual(rc, 1)

    @patch('main_logic_processing.repair_boot_loader')
    @patch('main_logic_processing.call_ghost', return_value=False)
    @patch('main_logic_processing.all_disk_partitions', return_value=True)
    @patch('main_logic_processing.validate_protected_disk', return_value=True)
    @patch('main_logic_processing.resolve_c_size', return_value=153600)
    @patch('main_logic_processing.get_disk_letter', side_effect=lambda d, t: {'efi': 'E', 'c': 'F'}[t])
    @patch('main_logic_processing.windows_disk_to_ghost_disk', return_value=2)
    @patch('main_logic_processing.time.sleep', return_value=None)
    def test_ghost_fail_should_not_call_bcdboot(
        self,
        _mock_sleep,
        _mock_map,
        _mock_letters,
        _mock_resolve,
        _mock_validate,
        _mock_partitions,
        _mock_ghost,
        mock_bcd,
    ):
        cfg = {
            'efi_size': 100,
            'c_size': 153600,
            'gho_exe': 'sw/ghost64.exe',
            'win_gho': 'img/test.GHO',
            'bcd_exe': 'sw/bcdboot.exe',
            'software_file': None,
        }

        ok = mlp.execute_install_flow(1, cfg)
        self.assertFalse(ok)
        mock_bcd.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
