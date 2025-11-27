#!/usr/bin/env python3
"""
按顺序测试所有分区初始化函数的脚本

调用顺序:
1. initialize_disk_to_gpt     - 初始化磁盘为GPT格式
2. initialize_disk_to_partitioning_C - 创建C分区
3. initialize_disk_to_partitioning_D - 创建D分区
4. initialize_disk_to_partitioning_E - 创建E分区

使用方法:
    python test_initialize_all_partitions.py --disk_number 3 --c_letter C --c_size 100000 --d_letter D --e_letter E --efi_size 100 --efi_letter S
    
参数说明:
    --disk_number: 磁盘编号 (必需)
    --c_letter: C分区盘符 (必需)
    --c_size: C分区大小MB (必需)
    --d_letter: D分区盘符 (必需)
    --e_letter: E分区盘符 (必需)
    --efi_size: EFI分区大小MB (可选, 默认100)
    --efi_letter: EFI分区盘符 (可选)
"""

import argparse
import sys
import traceback
import os

# 将当前目录添加到Python路径，确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from partition_disk import (
        initialize_disk_to_gpt,
        initialize_disk_to_partitioning_C,
        initialize_disk_to_partitioning_D,
        initialize_disk_to_partitioning_E
    )
except ImportError as e:
    print(f"错误: 无法导入 partition_disk 模块: {e}")
    print("请确保 partition_disk.py 文件存在于当前目录下")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='按顺序测试所有分区初始化函数',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 基本使用 - 创建一个标准的四分区磁盘
    python test_initialize_all_partitions.py --disk_number 3 --c_letter C --c_size 100000 --d_letter D --e_letter E
    
    # 完整参数 - 指定EFI分区
    python test_initialize_all_partitions.py --disk_number 3 --c_letter C --c_size 100000 --d_letter D --e_letter E --efi_size 100 --efi_letter S
    
注意事项:
    1. 这是一个破坏性操作，会清除磁盘上的所有数据
    2. 需要管理员权限运行
    3. 请确保指定的盘符未被使用
    4. 建议先备份重要数据
        """
    )
    
    # 必需参数
    parser.add_argument('--disk_number', type=int, required=True,
                       help='磁盘编号 (必需参数)')
    parser.add_argument('--c_letter', type=str, required=True,
                       help='C分区盘符 (必需参数, 例如: C)')
    parser.add_argument('--c_size', type=int, required=True,
                       help='C分区大小(MB) (必需参数)')
    parser.add_argument('--d_letter', type=str, required=True,
                       help='D分区盘符 (必需参数, 例如: D)')
    parser.add_argument('--e_letter', type=str, required=True,
                       help='E分区盘符 (必需参数, 例如: E)')
    
    # 可选参数
    parser.add_argument('--efi_size', type=int, default=100,
                       help='EFI分区大小(MB) (可选, 默认100MB)')
    parser.add_argument('--efi_letter', type=str,
                       help='EFI分区盘符 (可选)')
    
    args = parser.parse_args()
    
    # 参数验证
    # 验证盘符长度
    for param_name, param_value in [('C分区盘符', args.c_letter), ('D分区盘符', args.d_letter), ('E分区盘符', args.e_letter)]:
        if len(param_value) != 1:
            print(f"错误: {param_name}必须是单个字母")
            sys.exit(1)
        if not param_value.isalpha():
            print(f"错误: {param_name}必须是字母")
            sys.exit(1)
    
    # 验证EFI盘符（如果提供）
    if args.efi_letter is not None:
        if len(args.efi_letter) != 1:
            print("错误: EFI分区盘符必须是单个字母")
            sys.exit(1)
        if not args.efi_letter.isalpha():
            print("错误: EFI分区盘符必须是字母")
            sys.exit(1)
    
    # 验证大小参数
    if args.c_size <= 0:
        print("错误: C分区大小必须为正整数")
        sys.exit(1)
    
    if args.efi_size <= 0:
        print("错误: EFI分区大小必须为正整数")
        sys.exit(1)
    
    print("=" * 60)
    print("分区初始化测试开始")
    print("=" * 60)
    print(f"测试参数:")
    print(f"  磁盘编号: {args.disk_number}")
    print(f"  C分区: {args.c_letter} {args.c_size}MB")
    print(f"  D分区: {args.d_letter}")
    print(f"  E分区: {args.e_letter}")
    print(f"  EFI分区: {args.efi_size}MB", end="")
    if args.efi_letter:
        print(f" {args.efi_letter}", end="")
    print()
    print("=" * 60)
    
    # 存储每个步骤的结果
    results = {}
    
    try:
        # 第1步: 初始化GPT格式
        print("\n[步骤 1/4] 初始化GPT格式...")
        print("-" * 40)
        
        results['gpt'] = initialize_disk_to_gpt(
            disk_number=args.disk_number,
            efi_size=args.efi_size,
            efi_letter=args.efi_letter
        )
        
        if not results['gpt']:
            print("✗ GPT初始化失败，停止后续测试")
            sys.exit(1)
        else:
            print("✓ GPT初始化成功")
        
        # 第2步: 创建C分区
        print("\n[步骤 2/4] 创建C分区...")
        print("-" * 40)
        
        results['c_partition'] = initialize_disk_to_partitioning_C(
            disk_number=args.disk_number,
            c_size=args.c_size,
            c_letter=args.c_letter
        )
        
        if not results['c_partition']:
            print("✗ C分区创建失败，停止后续测试")
            sys.exit(1)
        else:
            print("✓ C分区创建成功")
        
        # 第3步: 创建D分区
        print("\n[步骤 3/4] 创建D分区...")
        print("-" * 40)
        
        results['d_partition'] = initialize_disk_to_partitioning_D(
            disk_number=args.disk_number,
            d_letter=args.d_letter,
            efi_size=args.efi_size,
            c_size=args.c_size
        )
        
        if not results['d_partition']:
            print("✗ D分区创建失败，停止后续测试")
            sys.exit(1)
        else:
            print("✓ D分区创建成功")
        
        # 第4步: 创建E分区
        print("\n[步骤 4/4] 创建E分区...")
        print("-" * 40)
        
        results['e_partition'] = initialize_disk_to_partitioning_E(
            disk_number=args.disk_number,
            e_letter=args.e_letter
        )
        
        if not results['e_partition']:
            print("✗ E分区创建失败")
            sys.exit(1)
        else:
            print("✓ E分区创建成功")
        
        # 汇总结果
        print("\n" + "=" * 60)
        print("所有分区初始化测试完成！")
        print("=" * 60)
        print("测试结果汇总:")
        for step_name, result in results.items():
            status = "✓ 成功" if result else "✗ 失败"
            print(f"  {step_name}: {status}")
        print("=" * 60)
        
        # 检查所有步骤是否都成功
        if all(results.values()):
            print("🎉 所有分区初始化步骤都成功完成！")
            sys.exit(0)
        else:
            print("❌ 部分分区初始化步骤失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了测试过程")
        print("请注意: 部分分区可能已经创建，请检查磁盘状态")
        sys.exit(1)
    except Exception as e:
        print("\n" + "-" * 60)
        print(f"✗ 测试过程中发生异常:")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        print("\n" + "-" * 60)
        print("⚠️ 请注意: 部分分区可能已经创建，请检查磁盘状态")
        sys.exit(1)

if __name__ == "__main__":
    main()