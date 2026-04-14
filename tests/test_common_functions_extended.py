"""
common_functions.py 扩展覆盖测试
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, Mock
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import common_functions as cf


class TestCommonFunctionsExtended(unittest.TestCase):
    def setUp(self):
        cf.clear_json_cache()

    def test_validate_json_file_path_errors(self):
        with self.assertRaises(FileNotFoundError):
            cf._validate_json_file_path('not_exists.json')

        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            with self.assertRaises(ValueError):
                cf._validate_json_file_path(path)
        finally:
            os.unlink(path)

    def test_cache_helpers(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({'a': 1}, f)
            path = os.path.abspath(f.name)
        try:
            self.assertIsNone(cf._check_json_cache(path))
            cf._update_json_cache(path, {'a': 1})
            cached = cf._check_json_cache(path)
            self.assertEqual(cached, {'a': 1})
        finally:
            os.unlink(path)

    def test_read_and_parse_json_retry(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write('{"a":1}')
            path = f.name
        try:
            self.assertEqual(cf._read_and_parse_json(path), {'a': 1})
        finally:
            os.unlink(path)

    def test_setup_logging_and_get_logger(self):
        logger1 = cf.setup_logging()
        logger2 = cf.get_logger()
        self.assertIs(logger1, logger2)

    @patch('common_functions.DiskManager', create=True)
    def test_get_disk_manager_singleton(self, _mock_dm):
        # 通过 patch disk_info.DiskManager 路径规避真实初始化
        cf._disk_manager_instance = None
        with patch('disk_info.DiskManager') as mock_dm:
            mock_dm.return_value = Mock()
            a = cf.get_disk_manager()
            b = cf.get_disk_manager()
            self.assertIs(a, b)


if __name__ == '__main__':
    unittest.main(verbosity=2)
