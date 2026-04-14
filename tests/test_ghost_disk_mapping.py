"""
Ghost 磁盘编号转换测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_logic_processing import windows_disk_to_ghost_disk


class TestGhostDiskMapping(unittest.TestCase):
    def test_mapping_basic(self):
        self.assertEqual(windows_disk_to_ghost_disk(0), 1)
        self.assertEqual(windows_disk_to_ghost_disk(1), 2)
        self.assertEqual(windows_disk_to_ghost_disk(5), 6)

    def test_mapping_invalid(self):
        with self.assertRaises(ValueError):
            windows_disk_to_ghost_disk(-1)
        with self.assertRaises(ValueError):
            windows_disk_to_ghost_disk("1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
