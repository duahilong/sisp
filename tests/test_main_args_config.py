"""
main.py 参数与配置分支测试
"""

import unittest
from unittest.mock import patch, Mock
import argparse
import tempfile
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


class TestMainArgsConfig(unittest.TestCase):
    def test_parse_arguments_ok(self):
        with patch.object(sys, 'argv', ['main.py', '--json', 'json/win11.json']):
            args = main.parse_arguments()
        self.assertEqual(args.json, 'json/win11.json')

    def test_parse_arguments_missing_required(self):
        with patch.object(sys, 'argv', ['main.py']):
            with self.assertRaises(SystemExit):
                main.parse_arguments()

    @patch('main.read_json_config', return_value=None)
    def test_setup_json_config_read_fail(self, _mock_read):
        args = argparse.Namespace(json='x.json')
        self.assertEqual(main.setup_json_config(args), {})

    @patch('main.read_json_config', return_value={'description': 'desc'})
    def test_setup_json_config_success(self, _mock_read):
        args = argparse.Namespace(json='ok.json')
        self.assertEqual(main.setup_json_config(args), {'description': 'desc'})

    def test_pause_if_interactive_eof(self):
        fake_stdin = Mock()
        fake_stdin.isatty.return_value = True
        with patch('main.sys.stdin', fake_stdin), patch('main.input', side_effect=EOFError):
            main.pause_if_interactive()

    def test_display_selection_results_single_and_multi(self):
        with patch('builtins.print') as mock_print:
            main.display_selection_results([1], {'description': 'd'})
            main.display_selection_results([1, 2], {'description': 'd'})
        self.assertTrue(mock_print.called)


if __name__ == '__main__':
    unittest.main(verbosity=2)
