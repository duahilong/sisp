#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ghost软件调用模块
用于调用Ghost软件对硬盘进行镜像刻录操作
"""

import subprocess
import sys
import os
import time
from typing import Union


def call_ghost(disk_number: Union[int, str], gho_exe: str, win_gho: str) -> bool:
    """
    调用Ghost软件对指定硬盘进行镜像刻录
    
    参数:
        disk_number (int or str): 目标硬盘编号 (例如: 1, 2, 3等)
        gho_exe (str): Ghost可执行文件的相对路径
        win_gho (str): 需要刻录的镜像文件路径
    
    返回:
        bool: 如果Ghost软件成功执行完毕返回True，否则返回False
    
    异常:
        FileNotFoundError: 当Ghost可执行文件不存在时抛出
        ValueError: 当参数格式不正确时抛出
    """
    
    # 参数验证
    if not gho_exe or not win_gho:
        raise ValueError("gho_exe和win_gho参数不能为空")
    
    if not isinstance(disk_number, (int, str)):
        raise ValueError("disk_number参数必须是整数或字符串类型")
    
    # 检查Ghost可执行文件是否存在
    if not os.path.exists(gho_exe):
        raise FileNotFoundError(f"Ghost可执行文件不存在: {gho_exe}")
    
    # 检查镜像文件是否存在
    if not os.path.exists(win_gho):
        raise FileNotFoundError(f"镜像文件不存在: {win_gho}")
    
    try:
        # 构建Ghost命令
        # 格式: ghost.exe -clone,mode=pload,src=镜像文件:1,dst=硬盘编号:2 -sure -ntexact
        gho_command = f'{gho_exe} -clone,mode=pload,src={win_gho}:1,dst={disk_number}:2 -sure -ntexact'
        
        print(f"正在启动Ghost软件...")
        print(f"执行命令: {gho_command}")
        print(f"目标硬盘: {disk_number}")
        print(f"镜像文件: {win_gho}")
        print(f"Ghost程序: {gho_exe}")
        
        # 启动Ghost进程
        # 使用shell=True来确保命令正确执行
        # 等待进程完成，Ghost是交互式程序，需要等待用户操作或自动完成
        process = subprocess.Popen(
            gho_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='gbk'  # Windows命令行通常使用GBK编码
        )
        
        print(f"Ghost进程已启动，进程ID: {process.pid}")
        
        # 等待Ghost进程完成
        # Ghost通常需要较长时间完成镜像刻录，这里设置20分钟超时时间
        try:
            # 等待进程完成，设置超时时间为20分钟(1200秒)
            stdout, stderr = process.communicate(timeout=1200)
            
            # 检查进程返回码
            if process.returncode == 0:
                print("Ghost软件执行成功!")
                print("镜像刻录操作已完成")
                
                # 如果有输出信息，也显示出来
                if stdout:
                    print("标准输出:")
                    print(stdout)
                    
                if stderr:
                    print("错误输出:")
                    print(stderr)
                
                return True
            else:
                print(f"Ghost软件执行失败，返回码: {process.returncode}")
                
                if stdout:
                    print("标准输出:")
                    print(stdout)
                    
                if stderr:
                    print("错误输出:")
                    print(stderr)
                    
                return False
                
        except subprocess.TimeoutExpired:
            # 超时处理
            print("Ghost软件执行超时(20分钟)，强制终止进程")
            process.kill()
            
            # 尝试获取剩余输出
            try:
                stdout, stderr = process.communicate(timeout=5)
                if stdout:
                    print("标准输出:")
                    print(stdout)
                if stderr:
                    print("错误输出:")
                    print(stderr)
            except:
                pass
                
            return False
            
    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
        return False
        
    except Exception as e:
        print(f"执行Ghost命令时发生未知错误: {e}")
        return False




if __name__ == "__main__":
    """
    测试代码示例 - 移除多余的测试调用，避免重复启动Ghost
    """
    # 测试参数
    test_disk_number = 3  # 根据你的规则，测试硬盘编号是3
    test_gho_exe = "sw\\ghost64.exe"
    test_win_gho = "img\\test.GHO"
    
    print("=== Ghost软件调用测试 ===")
    
    try:
        # 只测试一个版本，避免重复启动Ghost
        result = call_ghost(test_disk_number, test_gho_exe, test_win_gho)
        print(f"测试结果: {'成功' if result else '失败'}")
        
    except Exception as e:
        print(f"测试执行时发生错误: {e}")
        print("注意: 这个错误可能是因为Ghost程序不存在或配置不正确导致的")