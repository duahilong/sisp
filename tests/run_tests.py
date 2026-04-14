"""
测试运行入口
运行所有测试模块
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_test_suite():
    """创建测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_modules = [
        'tests.test_common_functions',
        'tests.test_disk_info_standalone',
        'tests.test_get_user_disknumber',
        'tests.test_call_ghost',
        'tests.test_partition_disk',
        'tests.test_call_bcdboot',
        'tests.test_call_copy',
        'tests.test_dynamic_c_size',
        'tests.test_partition_workflow',
    ]
    
    for module in test_modules:
        try:
            suite.addTests(loader.loadTestsFromName(module))
            print(f"[OK] 加载测试模块: {module}")
        except Exception as e:
            print(f"[FAIL] 加载测试模块失败: {module}")
            print(f"      错误: {e}")
    
    return suite


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Sisp 测试套件")
    print("=" * 60)
    print()
    
    suite = create_test_suite()
    
    if suite.countTestCases() == 0:
        print("没有找到任何测试用例！")
        return
    
    print()
    print(f"总计: {suite.countTestCases()} 个测试用例")
    print("-" * 60)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"测试用例数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print()
        print("[OK] 所有测试通过！")
        return 0
    else:
        print()
        print("[ERROR] 部分测试失败！")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
