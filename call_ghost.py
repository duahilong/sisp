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


def validate_windows_folder(c_letter: str) -> bool:
    """
    验证指定盘符下是否存在Windows文件夹
    
    参数:
        c_letter (str): 盘符字母，例如 "C:", "D:", "E:" 等
    
    返回:
        bool: 如果找到Windows文件夹返回True，否则返回False
    """
    
    # 确保盘符格式正确（以冒号结尾）
    if not c_letter.endswith(':'):
        c_letter = c_letter + ':'
    
    # 构建Windows文件夹路径
    windows_path = os.path.join(c_letter, 'Windows')
    
    try:
        # 检查Windows文件夹是否存在
        if os.path.exists(windows_path) and os.path.isdir(windows_path):
            # 额外验证：检查文件夹是否非空
            try:
                contents = os.listdir(windows_path)
                if contents:
                    print("系统验证成功")
                    return True
                else:
                    print(f"未发现Windows文件夹: {windows_path}")
                    return False
            except PermissionError:
                print(f"无法访问Windows文件夹: {windows_path}")
                return False
        else:
            print(f"未发现Windows文件夹: {windows_path}")
            return False
            
    except Exception as e:
        print(f"验证Windows文件夹时发生错误: {e}")
        return False


def call_ghost(disk_number: Union[int, str], gho_exe: str, win_gho: str, c_letter: str) -> bool:
    """
    调用Ghost软件对指定硬盘进行镜像刻录
    
    参数:
        disk_number (int or str): 目标硬盘编号 (例如: 1, 2, 3等)
        gho_exe (str): Ghost可执行文件的相对路径
        win_gho (str): 需要刻录的镜像文件路径
        c_letter (str): 验证的盘符字母，用于验证Windows文件夹是否存在
                       例如: "C:", "D:"等。必需参数，不可为空
    
    返回:
        bool: 如果Ghost软件成功执行完毕且验证通过返回True，否则返回False
    
    异常:
        FileNotFoundError: 当Ghost可执行文件不存在时抛出
        ValueError: 当参数格式不正确或c_letter为空时抛出
    """
    
    # 参数验证
    if not gho_exe or not win_gho or not c_letter:
        raise ValueError("gho_exe、win_gho和c_letter参数都不能为空")
    
    # 验证c_letter参数格式
    if not isinstance(c_letter, str) or len(c_letter.strip()) == 0:
        raise ValueError("c_letter参数必须是有效的字符串，不能为空")
    
    if not isinstance(disk_number, (int, str)):
        raise ValueError("disk_number参数必须是整数或字符串类型")
    
    # 检查Ghost可执行文件是否存在
    if not os.path.exists(gho_exe):
        raise FileNotFoundError(f"Ghost可执行文件不存在: {gho_exe}")
    
    # 检查镜像文件是否存在
    if not os.path.exists(win_gho):
        raise FileNotFoundError(f"镜像文件不存在: {win_gho}")
    
    try:
        # 确保disk_number是整数类型
        if isinstance(disk_number, str):
            disk_number = int(disk_number)
        elif not isinstance(disk_number, int):
            raise ValueError(f"disk_number必须是整数或字符串类型，当前类型: {type(disk_number)}")
        
        # 构建Ghost命令
        # 格式: ghost.exe -clone,mode=pload,src=镜像文件:1,dst=硬盘编号:2 -sure -ntexact
        gho_command = f'{gho_exe} -clone,mode=pload,src={win_gho}:1,dst={disk_number + 1}:2 -sure -ntexact'
        
        print(f"执行命令: {gho_command}")
        print(f"镜像文件: {win_gho}")
        
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
                # 进行Windows文件夹验证（c_letter现在是必需参数）
                validation_result = validate_windows_folder(c_letter)
                
                if validation_result:
                    return True
                else:
                    print(f"验证失败: {c_letter} 盘符下未发现Windows文件夹")
                    return False
            else:
                print(f"Ghost软件执行失败，返回码: {process.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            # 超时处理
            print("Ghost软件执行超时(20分钟)，强制终止进程")
            process.kill()
            return False
            
    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
        return False
        
    except Exception as e:
        print(f"执行Ghost命令时发生未知错误: {e}")
        return False




if __name__ == "__main__":
    """
    测试代码示例 
    """
    # 测试参数
    test_disk_number = 3  # 根据你的规则，测试硬盘编号是3
    test_gho_exe = "sw\\ghost64.exe"
    test_win_gho = "img\\test.GHO"
    c_letter = "U"
    
    print("=== Ghost软件调用测试 ===")
    
    try:
        # 只测试一个版本
        # 注意: c_letter现在是必需参数，这里使用U:作为示例
        result = call_ghost(test_disk_number, test_gho_exe, test_win_gho, c_letter)
        print(f"测试结果: {'成功' if result else '失败'}")
        
    except Exception as e:
        print(f"测试执行时发生错误: {e}")
        print("注意: 这个错误可能是因为Ghost程序不存在或配置不正确导致的")