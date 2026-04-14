"""
硬盘分区流程专项测试
覆盖 main_logic_processing.all_disk_partitions 的核心分支逻辑。
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_logic_processing import all_disk_partitions


def _fake_disk_letter(_disk_number, letter_type):
    mapping = {
        "efi": "E",
        "c": "F",
        "d": "G",
        "e": "H",
    }
    return mapping[letter_type]


class TestPartitionWorkflow(unittest.TestCase):
    """分区流程专项测试"""

    @patch("main_logic_processing.copy_software_folder")
    @patch("main_logic_processing.initialize_disk_to_partitioning_E")
    @patch("main_logic_processing.initialize_disk_to_partitioning_D")
    @patch("main_logic_processing.initialize_disk_to_partitioning_C")
    @patch("main_logic_processing.initialize_disk_to_gpt")
    @patch("main_logic_processing.get_disk_manager")
    @patch("main_logic_processing.get_disk_letter", side_effect=_fake_disk_letter)
    def test_small_disk_skip_d_partition(
        self,
        _mock_letter,
        mock_get_disk_manager,
        mock_gpt,
        mock_c,
        mock_d,
        mock_e,
        mock_copy,
    ):
        """<600GB 时应跳过 D 分区"""
        mock_disk_info = Mock()
        mock_disk_info.capacity = "500 GB"
        mock_mgr = Mock()
        mock_mgr.get_disk_by_index.return_value = mock_disk_info
        mock_get_disk_manager.return_value = mock_mgr

        mock_gpt.return_value = True
        mock_c.return_value = True
        mock_d.return_value = True
        mock_e.return_value = True
        mock_copy.return_value = "成功：文件夹已复制"

        result = all_disk_partitions(1, 100, 153600, "D:\\apps")

        self.assertTrue(result)
        mock_gpt.assert_called_once_with(1, 100, "E")
        mock_c.assert_called_once_with(1, 153600, "F")
        mock_d.assert_not_called()
        mock_e.assert_called_once_with(1, "H")

    @patch("main_logic_processing.copy_software_folder")
    @patch("main_logic_processing.initialize_disk_to_partitioning_E")
    @patch("main_logic_processing.initialize_disk_to_partitioning_D")
    @patch("main_logic_processing.initialize_disk_to_partitioning_C")
    @patch("main_logic_processing.initialize_disk_to_gpt")
    @patch("main_logic_processing.get_disk_manager")
    @patch("main_logic_processing.get_disk_letter", side_effect=_fake_disk_letter)
    def test_large_disk_create_d_partition(
        self,
        _mock_letter,
        mock_get_disk_manager,
        mock_gpt,
        mock_c,
        mock_d,
        mock_e,
        mock_copy,
    ):
        ">=600GB 时应创建 D 分区"""
        mock_disk_info = Mock()
        mock_disk_info.capacity = "800 GB"
        mock_mgr = Mock()
        mock_mgr.get_disk_by_index.return_value = mock_disk_info
        mock_get_disk_manager.return_value = mock_mgr

        mock_gpt.return_value = True
        mock_c.return_value = True
        mock_d.return_value = True
        mock_e.return_value = True
        mock_copy.return_value = "成功：文件夹已复制"

        result = all_disk_partitions(1, 100, 204800, "D:\\apps")

        self.assertTrue(result)
        mock_d.assert_called_once_with(1, "G", 100, 204800)

    @patch("main_logic_processing.initialize_disk_to_partitioning_E")
    @patch("main_logic_processing.initialize_disk_to_partitioning_D")
    @patch("main_logic_processing.initialize_disk_to_partitioning_C")
    @patch("main_logic_processing.initialize_disk_to_gpt")
    @patch("main_logic_processing.get_disk_manager")
    @patch("main_logic_processing.get_disk_letter", side_effect=_fake_disk_letter)
    def test_stop_when_c_partition_failed(
        self,
        _mock_letter,
        mock_get_disk_manager,
        mock_gpt,
        mock_c,
        mock_d,
        mock_e,
    ):
        """C 分区失败时应立即中断后续步骤"""
        mock_disk_info = Mock()
        mock_disk_info.capacity = "1000 GB"
        mock_mgr = Mock()
        mock_mgr.get_disk_by_index.return_value = mock_disk_info
        mock_get_disk_manager.return_value = mock_mgr

        mock_gpt.return_value = True
        mock_c.return_value = False

        result = all_disk_partitions(1, 100, 204800)

        self.assertFalse(result)
        mock_d.assert_not_called()
        mock_e.assert_not_called()

    @patch("main_logic_processing.copy_software_folder")
    @patch("main_logic_processing.initialize_disk_to_partitioning_E")
    @patch("main_logic_processing.initialize_disk_to_partitioning_D")
    @patch("main_logic_processing.initialize_disk_to_partitioning_C")
    @patch("main_logic_processing.initialize_disk_to_gpt")
    @patch("main_logic_processing.get_disk_manager")
    @patch("main_logic_processing.get_disk_letter", side_effect=_fake_disk_letter)
    def test_copy_error_should_fail_workflow(
        self,
        _mock_letter,
        mock_get_disk_manager,
        mock_gpt,
        mock_c,
        mock_d,
        mock_e,
        mock_copy,
    ):
        """软件复制返回错误时，分区流程应失败"""
        mock_disk_info = Mock()
        mock_disk_info.capacity = "1200 GB"
        mock_mgr = Mock()
        mock_mgr.get_disk_by_index.return_value = mock_disk_info
        mock_get_disk_manager.return_value = mock_mgr

        mock_gpt.return_value = True
        mock_c.return_value = True
        mock_d.return_value = True
        mock_e.return_value = True
        mock_copy.return_value = "错误：复制失败"

        result = all_disk_partitions(1, 100, 307200, "D:\\apps")

        self.assertFalse(result)

    @patch("main_logic_processing.copy_software_folder")
    @patch("main_logic_processing.initialize_disk_to_partitioning_E")
    @patch("main_logic_processing.initialize_disk_to_partitioning_D")
    @patch("main_logic_processing.initialize_disk_to_partitioning_C")
    @patch("main_logic_processing.initialize_disk_to_gpt")
    @patch("main_logic_processing.get_disk_manager")
    @patch("main_logic_processing.get_disk_letter", side_effect=_fake_disk_letter)
    def test_partition_call_order_strict(
        self,
        _mock_letter,
        mock_get_disk_manager,
        mock_gpt,
        mock_c,
        mock_d,
        mock_e,
        mock_copy,
    ):
        """严格校验调用顺序：GPT -> C -> D -> E。"""
        call_order = []

        mock_disk_info = Mock()
        mock_disk_info.capacity = "1000 GB"  # 触发 D 分区
        mock_mgr = Mock()
        mock_mgr.get_disk_by_index.return_value = mock_disk_info
        mock_get_disk_manager.return_value = mock_mgr

        def _mark(name):
            def _inner(*_args, **_kwargs):
                call_order.append(name)
                return True
            return _inner

        mock_gpt.side_effect = _mark("GPT")
        mock_c.side_effect = _mark("C")
        mock_d.side_effect = _mark("D")
        mock_e.side_effect = _mark("E")
        mock_copy.return_value = "成功：文件夹已复制"

        result = all_disk_partitions(1, 100, 204800, "D:\\apps")

        self.assertTrue(result)
        self.assertEqual(call_order, ["GPT", "C", "D", "E"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
