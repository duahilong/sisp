"""
main.py 主流程分支测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


class TestMainFlow(unittest.TestCase):
    @patch('main.pause_if_interactive')
    @patch('main.execute_main_logic')
    @patch('main.display_selection_results')
    @patch('main.handle_user_input', return_value=[1])
    @patch('main.display_disk_information', return_value=[[1, 'Disk', '500 GB', 'C', 'GPT']])
    @patch('main.setup_json_config')
    @patch('main.parse_arguments')
    def test_main_success_path(
        self,
        mock_parse_args,
        mock_setup_json,
        _mock_display,
        _mock_handle,
        _mock_selection,
        mock_execute,
        _mock_pause,
    ):
        mock_parse_args.return_value = Mock(json='json/win11.json')
        mock_setup_json.return_value = {'main_logic': 'dist/main_logic_processing.exe'}

        main.main()

        mock_execute.assert_called_once()

    @patch('main.execute_main_logic')
    @patch('main.display_selection_results')
    @patch('main.handle_user_input')
    @patch('main.display_disk_information')
    @patch('main.setup_json_config', return_value={})
    @patch('main.parse_arguments')
    def test_main_empty_config_should_exit_early(
        self,
        mock_parse_args,
        _mock_setup,
        _mock_display,
        _mock_handle,
        _mock_selection,
        mock_execute,
    ):
        mock_parse_args.return_value = Mock(json='json/win11.json')

        main.main()

        mock_execute.assert_not_called()

    @patch('main.parse_arguments', side_effect=ValueError('bad arg'))
    def test_main_value_error_branch(self, _mock_parse):
        with patch('builtins.print') as mock_print:
            main.main()
        output = '\n'.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('输入错误', output)

    @patch('main.get_disk_info', return_value=None)
    def test_display_disk_information_none(self, _mock_get):
        self.assertIsNone(main.display_disk_information())

    @patch('main.get_disk_info', return_value=[[1, 'Disk', '500 GB', 'C', 'GPT']])
    @patch('main.print_disk_info')
    def test_display_disk_information_ok(self, mock_print_disk, _mock_get):
        data = main.display_disk_information()
        self.assertIsNotNone(data)
        mock_print_disk.assert_called_once()

    @patch('main.input_user', return_value=[])
    def test_handle_user_input_empty(self, _mock_input):
        self.assertIsNone(main.handle_user_input(None, {}))

    @patch('main.input_user', return_value=None)
    def test_handle_user_input_none(self, _mock_input):
        self.assertIsNone(main.handle_user_input(None, {}))


if __name__ == '__main__':
    unittest.main(verbosity=2)
