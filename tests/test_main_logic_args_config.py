"""
main_logic_processing 参数与配置分支测试
"""

import unittest
from unittest.mock import patch, Mock
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main_logic_processing as mlp


class TestMainLogicArgsConfig(unittest.TestCase):
    def test_parse_arguments_ok(self):
        with patch.object(sys, 'argv', ['main_logic_processing.py', '-d', '1', '-j', 'json/win11.json']):
            args = mlp.parse_arguments()
        self.assertEqual(args.disk, 1)
        self.assertEqual(args.json, 'json/win11.json')

    def test_parse_arguments_invalid_choice(self):
        with patch.object(sys, 'argv', ['main_logic_processing.py', '-d', '0', '-j', 'x.json']):
            with self.assertRaises(SystemExit):
                mlp.parse_arguments()

    @patch('main_logic_processing.read_json_config', return_value=None)
    @patch('main_logic_processing.pause_if_interactive')
    def test_setup_json_config_fail_exit(self, _mock_pause, _mock_read):
        args = argparse.Namespace(json='missing.json')
        with self.assertRaises(SystemExit):
            mlp.setup_json_config(args)

    @patch('main_logic_processing.read_json_config', return_value={'description': 'ok'})
    def test_setup_json_config_success(self, _mock_read):
        args = argparse.Namespace(json='ok.json')
        cfg = mlp.setup_json_config(args)
        self.assertEqual(cfg['description'], 'ok')


if __name__ == '__main__':
    unittest.main(verbosity=2)
