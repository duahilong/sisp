"""
get_user_disknumber.py 测试模块
测试用户输入解析功能，不涉及真实磁盘操作
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_user_disknumber import (
    parse_disk_input,
    validate_disk_numbers,
    validate_disk_input,
)


class TestParseDiskInput(unittest.TestCase):
    """测试 parse_disk_input 函数"""

    def test_single_number(self):
        """测试单个数字输入"""
        result = parse_disk_input("3")
        self.assertEqual(result, [3])

    def test_single_number_with_spaces(self):
        """测试带空格的单个数字"""
        result = parse_disk_input("  5  ")
        self.assertEqual(result, [5])

    def test_range_format(self):
        """测试范围格式"""
        result = parse_disk_input("1-3")
        self.assertEqual(result, [1, 2, 3])

    def test_multiple_numbers_comma(self):
        """测试逗号分隔的多个数字"""
        result = parse_disk_input("1,3,5")
        self.assertEqual(result, [1, 3, 5])

    def test_multiple_numbers_space(self):
        """测试空格分隔的多个数字"""
        result = parse_disk_input("1 3 5")
        self.assertEqual(result, [1, 3, 5])

    def test_mixed_format_comma_and_range(self):
        """测试混合格式：逗号和范围"""
        result = parse_disk_input("1,3-5,6")
        self.assertEqual(result, [1, 3, 4, 5, 6])

    def test_mixed_format_spaces_and_range(self):
        """测试混合格式：空格和范围"""
        result = parse_disk_input("1 3-5 6")
        self.assertEqual(result, [1, 3, 4, 5, 6])

    def test_a_all_input(self):
        """测试字母a表示全部"""
        with patch('get_user_disknumber.get_disk_manager') as mock_manager:
            mock_disk = Mock()
            mock_disk.index = 1
            mock_manager.return_value.get_disk_info.return_value = [mock_disk]
            result = parse_disk_input("a")
            self.assertEqual(result, [1])

    def test_empty_input(self):
        """测试空输入"""
        with self.assertRaises(ValueError):
            parse_disk_input("")

    def test_whitespace_input(self):
        """测试空白输入"""
        with self.assertRaises(ValueError):
            parse_disk_input("   ")

    def test_invalid_format(self):
        """测试无效格式"""
        with self.assertRaises(ValueError):
            parse_disk_input("abc")

    def test_out_of_range_single(self):
        """测试单个数字超出范围"""
        with self.assertRaises(ValueError):
            parse_disk_input("7")

    def test_out_of_range_start(self):
        """测试范围起始超出范围"""
        with self.assertRaises(ValueError):
            parse_disk_input("0-3")

    def test_out_of_range_end(self):
        """测试范围结束超出范围"""
        with self.assertRaises(ValueError):
            parse_disk_input("1-7")

    def test_invalid_range(self):
        """测试无效范围（起始大于结束）"""
        with self.assertRaises(ValueError):
            parse_disk_input("5-3")

    def test_duplicates_removed(self):
        """测试重复数字被移除"""
        result = parse_disk_input("1,1,2,2,3,3")
        self.assertEqual(result, [1, 2, 3])


class TestValidateDiskNumbers(unittest.TestCase):
    """测试 validate_disk_numbers 函数"""

    def test_valid_numbers(self):
        """测试有效的磁盘编号"""
        result = validate_disk_numbers([1, 2, 3])
        self.assertEqual(result, [1, 2, 3])

    def test_empty_list(self):
        """测试空列表"""
        with self.assertRaises(ValueError):
            validate_disk_numbers([])

    def test_out_of_range(self):
        """测试超出范围的编号"""
        with self.assertRaises(ValueError):
            validate_disk_numbers([0, 1, 2])

    def test_out_of_range_high(self):
        """测试超出范围的编号（大于6）"""
        with self.assertRaises(ValueError):
            validate_disk_numbers([1, 7])


class TestValidateDiskInput(unittest.TestCase):
    """测试 validate_disk_input 函数"""

    def test_integer_input(self):
        """测试整数输入"""
        result = validate_disk_input(3)
        self.assertEqual(result, [3])

    def test_string_input(self):
        """测试字符串输入"""
        result = validate_disk_input("1-3")
        self.assertEqual(result, [1, 2, 3])

    def test_invalid_type(self):
        """测试无效类型"""
        with self.assertRaises(ValueError):
            validate_disk_input([1, 2, 3])


if __name__ == '__main__':
    unittest.main(verbosity=2)
