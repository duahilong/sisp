import subprocess
import wmi
import os
import string
import tempfile
from disk_info import DiskManager

def validate_input_parameters(disk_number, efi_size=None, efi_letter=None, c_size=None, c_letter=None, d_letter=None, e_letter=None):
    """
    验证分区操作的输入参数
    
    Args:
        disk_number: 磁盘编号，必须是非负整数
        efi_size: EFI分区大小(MB)，必须是正整数，且不能大于硬盘容量的1/10
        efi_letter: EFI分区盘符，必须是单个大写字母，不能是'C'或'D'
        c_size: C分区大小(MB)，必须是正整数
        c_letter: C分区盘符，必须是单个大写字母，不能是'C'或'D'
        d_letter: D分区盘符，必须是单个大写字母，不能是'C'或'D'
        e_letter: E分区盘符，必须是单个大写字母，不能是'C'或'D'
        
    Returns:
        bool: 验证成功返回True，否则返回False并打印错误信息
        
    Raises:
        ValueError: 当参数不符合要求时抛出异常
    """
    
    try:
        # 1. 基础验证 - 磁盘编号
        if disk_number is None or not isinstance(disk_number, int) or disk_number < 0:
            raise ValueError("磁盘编号必须为非负整数。")
        
        # 2. 验证磁盘编号是否超出系统磁盘数量
        try:
            disk_manager = DiskManager()
            disk_info_list = disk_manager.get_disk_info()
            
            if disk_info_list is None or len(disk_info_list) == 0:
                raise ValueError("无法获取系统磁盘信息或系统中没有磁盘。")
            
            # 获取所有磁盘索引，找到最大索引值
            max_disk_index = max(disk.index for disk in disk_info_list)
            total_disks = len(disk_info_list)
            
            # 检查disk_number是否在有效范围内
            if disk_number > max_disk_index:
                raise ValueError(f"磁盘编号 {disk_number} 超出系统范围。系统共有 {total_disks} 个磁盘，有效磁盘编号范围为 0-{max_disk_index}。")
            
        except Exception as e:
            if "无法获取系统磁盘信息或系统中没有磁盘" in str(e):
                raise e
            else:
                raise ValueError(f"磁盘编号验证失败: {e}")
        
        # 3. EFI分区参数验证，验证EFI分区大小，检查EFI分区大小是否超过磁盘容量的1/10
        if efi_size is not None:
            if not isinstance(efi_size, int) or efi_size <= 0:
                raise ValueError("EFI分区大小必须是正整数。")
            
            # 验证EFI分区大小是否超过磁盘容量的1/10
            try:
                disk_manager = DiskManager()
                disk_info = disk_manager.get_disk_by_index(disk_number)
                
                if disk_info is None:
                    raise ValueError(f"未找到磁盘编号 {disk_number}。")
                
                # 解析磁盘容量（格式为 "XX.XX GB"）
                disk_capacity_str = disk_info.capacity.replace("GB", "").strip()
                disk_capacity_gb = float(disk_capacity_str)
                
                # 将efi_size从MB转换为GB进行比较
                efi_size_gb = efi_size / 1024.0
                max_efi_size_gb = disk_capacity_gb / 10.0
                
                # 检查EFI分区大小是否超过磁盘容量的1/10
                if efi_size_gb > max_efi_size_gb:
                    raise ValueError(f"EFI分区大小 ({efi_size} MB / {efi_size_gb:.2f} GB) 超出磁盘 {disk_number} 容量的1/10 ({max_efi_size_gb:.2f} GB)。")
                
            except Exception as e:
                raise ValueError(f"EFI分区大小验证失败: {e}")
                
        if efi_letter is not None:
            if not isinstance(efi_letter, str) or len(efi_letter) != 1 or efi_letter not in string.ascii_uppercase:
                raise ValueError("EFI分区盘符必须是单个大写字母。")
        
        # 4. C分区参数验证，验证C分区大小
        if c_size is not None:
            if not isinstance(c_size, int) or c_size <= 0:
                raise ValueError("C分区大小必须是正整数。")
            
            # 验证C分区大小是否超出磁盘容量
            try:
                disk_manager = DiskManager()
                disk_info = disk_manager.get_disk_by_index(disk_number)
                
                if disk_info is None:
                    raise ValueError(f"未找到磁盘编号 {disk_number}。")
                
                # 解析磁盘容量（格式为 "XX.XX GB"）
                disk_capacity_str = disk_info.capacity.replace("GB", "").strip()
                disk_capacity_gb = float(disk_capacity_str)
                
                # 将c_size从MB转换为GB进行比较
                c_size_gb = c_size / 1024.0
                
                # 检查C分区大小是否超出磁盘容量
                if c_size_gb > disk_capacity_gb:
                    raise ValueError(f"C分区大小 ({c_size} MB / {c_size_gb:.2f} GB) 超出磁盘 {disk_number} 的总容量 ({disk_capacity_gb} GB)。")
                
            except Exception as e:
                raise ValueError(f"C分区大小验证失败: {e}")
                
        if c_letter is not None:
            if not isinstance(c_letter, str) or len(c_letter) != 1 or c_letter not in string.ascii_uppercase:
                raise ValueError("C分区盘符必须是单个大写字母。")
        
        # 5. 其他分区盘符验证
        if d_letter is not None:
            if not isinstance(d_letter, str) or len(d_letter) != 1 or d_letter not in string.ascii_uppercase:
                raise ValueError("D分区盘符必须是单个大写字母。")
                
        if e_letter is not None:
            if not isinstance(e_letter, str) or len(e_letter) != 1 or e_letter not in string.ascii_uppercase:
                raise ValueError("E分区盘符必须是单个大写字母。")
        
        # 6. 验证盘符是否重复
        letters = [letter for letter in [efi_letter, c_letter, d_letter, e_letter] if letter is not None]
        if len(letters) != len(set(letters)):
            raise ValueError("盘符不能重复。")
            
        # 7. 验证所有盘符参数不能包含 C,D,S 这三个字母
        reserved_letters = ['C', 'D', 'S']
        for letter_param, letter_value in [('efi_letter', efi_letter), ('c_letter', c_letter), 
                                          ('d_letter', d_letter), ('e_letter', e_letter)]:
            if letter_value is not None and letter_value in reserved_letters:
                raise ValueError(f"{letter_param} 不能设置为 '{letter_value}'，因为 '{letter_value}' 是保留盘符。")
        
        return True
        
    except ValueError as e:
        print(f"参数验证失败: {e}")
        return False
    except Exception as e:
        print(f"验证过程中发生未知错误: {e}")
        return False

def initialize_disk_to_gpt(disk_number, efi_size=None, efi_letter=None,):
    """
    使用 DiskPart 将指定的磁盘初始化为 GPT，并进行错误检查和验证，并创建分区。

    参数：
    disk_number (int): 要初始化的磁盘编号。
    efi_size (int): EFI分区大小 (MB)。
    efi_letter (str): EFI分区的盘符。

    返回：
    bool: 初始化成功返回 True，否则返回 False。
    """
    
    try:
        # 1. 检查管理员权限
        if not is_admin():
            print("错误: 需要管理员权限才能执行磁盘分区操作")
            return False
        
        # 2. 首先验证输入参数
        if not validate_input_parameters(disk_number, efi_size, efi_letter, None, None, None, None):
            print("错误: 输入参数验证失败")
            return False
        
        # 3. 构建DiskPart脚本命令
        diskpart_commands = [
            f"select disk {disk_number}",  # 选择硬盘
            "clean",                       # 清除磁盘
            "convert gpt",                # 转换为GPT格式
            "list partition",             # 列出分区以检查MSR分区
        ]
        
        # 4. 执行DiskPart命令进行初始化
        print(f"正在初始化磁盘 {disk_number} 为GPT格式...")
        
        # 第一个命令集：基础初始化
        result = execute_diskpart_command(diskpart_commands)
        if not result:
            print(f"错误: 磁盘 {disk_number} 初始化GPT格式失败")
            return False
        
        # 5. 检查并删除MSR分区 (convert gpt后第一个分区默认为MSR分区)
        print("检查并处理MSR分区...")
        msr_delete_commands = [
            f"select disk {disk_number}",
            "list partition",
            "select partition 1",  # MSR分区通常是GPT转换后的第一个分区
            "delete partition override"
        ]
        
        delete_result = execute_diskpart_command(msr_delete_commands)
        if delete_result:
            print("MSR分区删除成功")
        else:
            print("警告: 删除MSR分区失败，但不影响GPT初始化")
        
        # 6. 验证GPT初始化是否成功
        print("验证GPT初始化结果...")
        
        # 使用disk_info模块验证磁盘格式
        try:
            from disk_info import DiskManager
            disk_manager = DiskManager()
            partition_style = disk_manager._get_partition_style(disk_number)
            
            if partition_style != "GPT":
                print(f"错误: 磁盘 {disk_number} 当前格式为 '{partition_style}'，不是GPT格式")
                return False
            
            print(f"磁盘 {disk_number} 成功初始化为GPT格式")
            
        except Exception as e:
            print(f"警告: 无法通过disk_info验证磁盘格式，尝试备用验证方法: {e}")
            
            # 备用验证方法：使用DiskPart命令
            disk_verify_commands = [
                f"select disk {disk_number}",
                "list disk"
            ]
            
            disk_verify_result = execute_diskpart_command(disk_verify_commands, capture_output=True)
            if not disk_verify_result:
                print(f"错误: 无法验证磁盘 {disk_number} 的GPT初始化结果")
                return False
            
            # 检查磁盘格式是否为GPT - 搜索输出中的GPT标识
            disk_lines = disk_verify_result.split('\n')
            disk_format_valid = False
            
            for line in disk_lines:
                if "GPT" in line and (f"磁盘 {disk_number}" in line or f"Disk {disk_number}" in line):
                    disk_format_valid = True
                    break
            
            if not disk_format_valid:
                print(f"错误: 磁盘 {disk_number} 未成功转换为GPT格式")
                print("磁盘格式化验证失败")
                return False
            
            print(f"磁盘 {disk_number} 成功初始化为GPT格式（通过备用验证方法）")
        
        # 然后验证分区状态（确认MSR分区已删除）
        print("验证分区清理状态...")
        partition_verify_commands = [
            f"select disk {disk_number}",
            "list partition"
        ]
        
        partition_verify_result = execute_diskpart_command(partition_verify_commands, capture_output=True)
        if not partition_verify_result:
            print("警告: 无法检查分区状态，但GPT转换已成功")
        else:
            # 检查是否还有分区（除了可能的EFI分区）
            partition_lines = partition_verify_result.split('\n')
            partition_count = 0
            
            for line in partition_lines:
                # 跳过标题行和空行，计数有效分区
                line = line.strip()
                if line and not line.startswith('-') and "分区" not in line and "Partition" not in line:
                    # 计算这一行的分区信息
                    parts = line.split()
                    if len(parts) >= 4:  # 确保是有内容的分区行
                        try:
                            # 尝试解析分区编号
                            partition_num = int(parts[0])
                            partition_count += 1
                        except (ValueError, IndexError):
                            continue
            
            if partition_count > 0:
                print(f"警告: 磁盘 {disk_number} 仍有 {partition_count} 个分区（MSR分区删除可能未完全成功）")
            else:
                print("分区清理验证通过，无残留分区")
        
        # 7. 如果提供了EFI参数，可以选择创建EFI分区
        if efi_size is not None and efi_letter is not None:
            print(f"正在创建EFI分区 ({efi_size}MB, 盘符: {efi_letter})...")
            efi_commands = [
                f"select disk {disk_number}",
                f"create partition efi size={efi_size}",
                f"format fs=fat32 quick label=EFI OVERRIDE",
                f"assign letter={efi_letter}"
            ]
            
            efi_result = execute_diskpart_command(efi_commands)
            if efi_result:
                print(f"EFI分区创建成功")
            else:
                print("警告: EFI分区创建失败")
        
        return True
        
    except Exception as e:
        print(f"初始化磁盘为GPT时发生错误: {e}")
        return False


def is_admin():
    """
    检查当前是否以管理员权限运行
    
    Returns:
        bool: 如果是管理员权限返回True，否则返回False
    """
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def execute_diskpart_command(commands, capture_output=False):
    """
    执行DiskPart命令
    
    Args:
        commands (list): DiskPart命令列表
        capture_output (bool): 是否捕获输出文本
        
    Returns:
        bool or str: 执行成功返回True或输出文本，失败返回False
    """
    try:
        # 构建DiskPart脚本内容
        script_content = "\n".join(commands) + "\nexit\n"
        
        # 使用临时文件执行DiskPart命令
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as script_file:
            script_file.write(script_content)
            script_path = script_file.name
        
        try:
            # 执行DiskPart命令
            if capture_output:
                result = subprocess.run(
                    ['diskpart', '/s', script_path],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2分钟超时
                )
                return result.stdout + result.stderr
            else:
                result = subprocess.run(
                    ['diskpart', '/s', script_path],
                    capture_output=True,
                    timeout=120  # 2分钟超时
                )
                return result.returncode == 0
                
        finally:
            # 清理临时文件
            if os.path.exists(script_path):
                os.unlink(script_path)
                
    except subprocess.TimeoutExpired:
        print("错误: DiskPart命令执行超时")
        return False
    except Exception as e:
        print(f"错误: 执行DiskPart命令时发生异常: {e}")
        return False
