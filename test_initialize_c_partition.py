#!/usr/bin/env python3
"""
测试 initialize_disk_to_partitioning_C 函数的脚本

使用方法:
    python test_initialize_c_partition.py --disk_number 3 --c_size 51200 --c_letter C
    
参数说明:
    --disk_number: 磁盘编号 (必需)
    --c_size: C分区大小 (MB) (可选)
    --c_letter: C分区盘符 (可选)
"""

import argparse
import sys
import traceback
import os

# 将当前目录添加到Python路径，确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from partition_disk import initialize_disk_to_partitioning_C
except ImportError as e:
    print(f"错误: 无法导入 partition_disk 模块: {e}")
    print("请确保 partition_disk.py 文件存在于当前目录下")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='测试 initialize_disk_to_partitioning_C 函数',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python test_initialize_c_partition.py --disk_number 3 --c_size 51200 --c_letter C
    python test_initialize_c_partition.py --disk_number 3 --c_size 102400 --c_letter D
        """
    )
    
    parser.add_argument('--disk_number', type=int, required=True,
                       help='磁盘编号 (必需参数)')
    parser.add_argument('--c_size', type=int, default=None,
                       help='C分区大小 (MB) (可选)')
    parser.add_argument('--c_letter', type=str, default=None,
                       help='C分区盘符 (可选, 例如: C, D, E)')
    
    args = parser.parse_args()
    
    # 参数验证
    if args.c_letter and len(args.c_letter) != 1:
        print("错误: C分区盘符必须是单个字母")
        sys.exit(1)
        
    if args.c_size is not None and args.c_size <= 0:
        print("错误: C分区大小必须是正整数")
        sys.exit(1)
    
    print(f"测试参数:")
    print(f"  磁盘编号: {args.disk_number}")
    print(f"  C分区大小: {args.c_size} MB")
    print(f"  C分区盘符: {args.c_letter}")
    print("-" * 50)
    
    try:
        # 调用函数
        result = initialize_disk_to_partitioning_C(
            disk_number=args.disk_number,
            c_size=args.c_size,
            c_letter=args.c_letter
        )
        
        print("-" * 50)
        if result:
            print("✓ 测试成功: C分区初始化完成")
            sys.exit(0)
        else:
            print("✗ 测试失败: C分区初始化失败")
            sys.exit(1)
            
    except Exception as e:
        print("-" * 50)
        print(f"✗ 测试过程中发生异常:")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()