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
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir=tests_dir, pattern='test_*.py', top_level_dir=os.path.dirname(tests_dir))
    print(f"[OK] 自动发现测试目录: {tests_dir}")
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
