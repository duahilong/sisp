"""
main_logic_processing 配置与交互保护测试
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_logic_processing import validate_main_config, pause_if_interactive


class TestMainLogicConfigValidation(unittest.TestCase):
    def test_validate_main_config_success(self):
        cfg = {
            "efi_size": 100,
            "c_size": 153600,
            "gho_exe": "sw/ghost64.exe",
            "win_gho": "img/test.GHO",
            "bcd_exe": "sw/bcdboot.exe",
            "excluded_disk_names": [],
        }
        validate_main_config(cfg)

    def test_validate_main_config_invalid_int_field(self):
        cfg = {
            "efi_size": 0,
            "c_size": 153600,
            "gho_exe": "sw/ghost64.exe",
            "win_gho": "img/test.GHO",
            "bcd_exe": "sw/bcdboot.exe",
        }
        with self.assertRaises(ValueError):
            validate_main_config(cfg)

    def test_validate_main_config_invalid_str_field(self):
        cfg = {
            "efi_size": 100,
            "c_size": 153600,
            "gho_exe": "",
            "win_gho": "img/test.GHO",
            "bcd_exe": "sw/bcdboot.exe",
        }
        with self.assertRaises(ValueError):
            validate_main_config(cfg)

    def test_validate_main_config_invalid_excluded_list(self):
        cfg = {
            "efi_size": 100,
            "c_size": 153600,
            "gho_exe": "sw/ghost64.exe",
            "win_gho": "img/test.GHO",
            "bcd_exe": "sw/bcdboot.exe",
            "excluded_disk_names": "not-list",
        }
        with self.assertRaises(ValueError):
            validate_main_config(cfg)


class TestPauseIfInteractive(unittest.TestCase):
    @patch("main_logic_processing.input")
    def test_pause_non_interactive_should_not_call_input(self, mock_input):
        fake_stdin = Mock()
        fake_stdin.isatty.return_value = False

        with patch("main_logic_processing.sys.stdin", fake_stdin):
            pause_if_interactive()

        mock_input.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
