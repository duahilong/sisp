"""
common_functions.py 测试模块
测试公共函数功能，不涉及真实磁盘操作
"""

import unittest
import os
import tempfile
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_functions import (
    get_disk_letter,
    number_list,
    read_json_config,
    clear_json_cache,
)


class TestGetDiskLetter(unittest.TestCase):
    """测试 get_disk_letter 函数"""

    def test_disk_1_efi(self):
        """测试磁盘1的EFI盘符"""
        self.assertEqual(get_disk_letter(1, 'efi'), 'E')

    def test_disk_1_c(self):
        """测试磁盘1的C盘符"""
        self.assertEqual(get_disk_letter(1, 'c'), 'F')

    def test_disk_1_d(self):
        """测试磁盘1的D盘符"""
        self.assertEqual(get_disk_letter(1, 'd'), 'G')

    def test_disk_1_e(self):
        """测试磁盘1的E盘符"""
        self.assertEqual(get_disk_letter(1, 'e'), 'H')

    def test_disk_2_letters(self):
        """测试磁盘2的盘符"""
        self.assertEqual(get_disk_letter(2, 'efi'), 'I')
        self.assertEqual(get_disk_letter(2, 'c'), 'J')
        self.assertEqual(get_disk_letter(2, 'd'), 'K')
        self.assertEqual(get_disk_letter(2, 'e'), 'L')

    def test_disk_6_letters(self):
        """测试磁盘6的盘符"""
        self.assertEqual(get_disk_letter(6, 'efi'), 'Y')
        self.assertEqual(get_disk_letter(6, 'c'), 'Z')
        self.assertEqual(get_disk_letter(6, 'd'), 'A')
        self.assertEqual(get_disk_letter(6, 'e'), 'B')

    def test_invalid_disk_number(self):
        """测试无效的磁盘编号"""
        self.assertIsNone(get_disk_letter(0, 'c'))
        self.assertIsNone(get_disk_letter(7, 'c'))
        self.assertIsNone(get_disk_letter(-1, 'c'))

    def test_invalid_letter_type(self):
        """测试无效的盘符类型"""
        self.assertIsNone(get_disk_letter(1, 'x'))
        self.assertIsNone(get_disk_letter(1, ''))


class TestNumberList(unittest.TestCase):
    """测试 number_list 配置"""

    def test_all_disks_configured(self):
        """测试所有磁盘是否都有配置"""
        self.assertEqual(len(number_list), 6)
        for i in range(1, 7):
            disk = next((d for d in number_list if d['disk_number'] == i), None)
            self.assertIsNotNone(disk, f"磁盘 {i} 缺少配置")

    def test_each_disk_has_required_keys(self):
        """测试每个磁盘配置是否包含必需的键"""
        required_keys = ['disk_number', 'efi_letter', 'c_letter', 'd_letter', 'e_letter']
        for disk in number_list:
            for key in required_keys:
                self.assertIn(key, disk, f"磁盘 {disk['disk_number']} 缺少键 {key}")


class TestReadJsonConfig(unittest.TestCase):
    """测试 read_json_config 函数"""

    def setUp(self):
        """创建临时JSON文件用于测试"""
        self.temp_dir = tempfile.mkdtemp()
        self.valid_json_path = os.path.join(self.temp_dir, 'valid.json')
        self.invalid_json_path = os.path.join(self.temp_dir, 'invalid.json')
        self.nonexistent_path = os.path.join(self.temp_dir, 'nonexistent.json')
        
        valid_config = {
            "description": "测试配置",
            "efi_size": 100,
            "c_size": 1536,
            "excluded_disk_names": ["Disk1", "Disk2"]
        }
        with open(self.valid_json_path, 'w', encoding='utf-8') as f:
            json.dump(valid_config, f)
        
        with open(self.invalid_json_path, 'w', encoding='utf-8') as f:
            f.write('{"invalid": json}')

    def tearDown(self):
        """清理临时文件"""
        clear_json_cache()
        for path in [self.valid_json_path, self.invalid_json_path]:
            if os.path.exists(path):
                os.unlink(path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_read_valid_json(self):
        """测试读取有效的JSON文件"""
        result = read_json_config(self.valid_json_path, use_cache=False)
        self.assertIsNotNone(result)
        self.assertEqual(result['description'], '测试配置')
        self.assertEqual(result['efi_size'], 100)

    def test_read_nonexistent_file(self):
        """测试读取不存在的文件"""
        result = read_json_config(self.nonexistent_path)
        self.assertIsNone(result)

    def test_read_invalid_json(self):
        """测试读取无效的JSON文件"""
        result = read_json_config(self.invalid_json_path, use_cache=False)
        self.assertIsNone(result)


class TestClearJsonCache(unittest.TestCase):
    """测试 clear_json_cache 函数"""

    def test_clear_cache_no_error(self):
        """测试清空缓存不会出错"""
        try:
            clear_json_cache()
        except Exception as e:
            self.fail(f"clear_json_cache 抛出异常: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
