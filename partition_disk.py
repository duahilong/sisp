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
            raise PermissionError("磁盘分区操作需要管理员权限。请以管理员身份运行此程序。")
        
        # 2. 首先验证输入参数
        if not validate_input_parameters(disk_number, efi_size, efi_letter, None, None, None, None):
            raise ValueError(f"参数验证失败: 磁盘编号={disk_number}, EFI大小={efi_size}, EFI盘符={efi_letter}")
        
        # 3. 构建DiskPart脚本命令
        diskpart_commands = [
            f"select disk {disk_number}",  # 选择硬盘
            "clean",                       # 清除磁盘
            "convert gpt",                # 转换为GPT格式
            "list partition",             # 列出分区以检查MSR分区
        ]
        
        # 4. 执行DiskPart命令进行初始化
        
        # 第一个命令集：基础初始化
        result = execute_diskpart_command(diskpart_commands)
        if not result:
            raise RuntimeError(f"磁盘 {disk_number} 的GPT初始化失败。可能的原因：1)磁盘被占用；2)磁盘损坏；3)DiskPart命令执行异常。请检查磁盘状态并重试。")
        
        # 5. 检查并删除MSR分区 (convert gpt后第一个分区默认为MSR分区)
        msr_delete_commands = [
            f"select disk {disk_number}",
            "list partition",
            "select partition 1",  # MSR分区通常是GPT转换后的第一个分区
            "delete partition override"
        ]
        
        delete_result = execute_diskpart_command(msr_delete_commands)
        if not delete_result:
            print("警告: MSR分区删除失败，但不影响GPT初始化")
        
        # 6. 验证GPT初始化是否成功
        
        # 使用disk_info模块验证磁盘格式
        try:
            from disk_info import DiskManager
            disk_manager = DiskManager()
            partition_style = disk_manager._get_partition_style(disk_number)
            
            if partition_style != "GPT":
                raise RuntimeError(f"磁盘 {disk_number} 当前格式为 '{partition_style}'，不是GPT格式。转换可能未成功或磁盘格式检查异常。")
            
        except Exception as e:
            # 备用验证方法：使用DiskPart命令
            disk_verify_commands = [
                f"select disk {disk_number}",
                "list disk"
            ]
            
            disk_verify_result = execute_diskpart_command(disk_verify_commands, capture_output=True)
            if not disk_verify_result:
                raise RuntimeError(f"无法验证磁盘 {disk_number} 的GPT初始化结果。可能是DiskPart命令执行失败或磁盘访问异常。")
            
            # 检查磁盘格式是否为GPT - 搜索输出中的GPT标识
            disk_lines = disk_verify_result.split('\n')
            disk_format_valid = False
            
            for line in disk_lines:
                if "GPT" in line and (f"磁盘 {disk_number}" in line or f"Disk {disk_number}" in line):
                    disk_format_valid = True
                    break
            
            if not disk_format_valid:
                raise RuntimeError(f"磁盘 {disk_number} 未成功转换为GPT格式。DiskPart命令执行可能失败或磁盘状态异常。请检查磁盘是否被其他程序占用。")
        
        # 然后验证分区状态（确认MSR分区已删除）
        partition_verify_commands = [
            f"select disk {disk_number}",
            "list partition"
        ]
        
        partition_verify_result = execute_diskpart_command(partition_verify_commands, capture_output=True)
        if partition_verify_result:
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
        
        # 7. 如果提供了EFI参数，可以选择创建EFI分区
        if efi_size is not None and efi_letter is not None:
            efi_commands = [
                f"select disk {disk_number}",
                f"create partition efi size={efi_size}",
                f"format fs=fat32 quick label=EFI OVERRIDE",
                f"assign letter={efi_letter}"
            ]
            
            efi_result = execute_diskpart_command(efi_commands)
            if not efi_result:
                raise RuntimeError(f"EFI分区创建失败。请检查磁盘 {disk_number} 是否可用，以及指定的盘符 {efi_letter} 是否已被占用。")
        
        print("✅ 磁盘GPT初始化成功完成")
        return True
        
    except PermissionError as e:
        print(f"❌ 权限错误: {e}")
        return False
    except ValueError as e:
        print(f"❌ 参数错误: {e}")
        return False
    except RuntimeError as e:
        print(f"❌ 执行错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False


def initialize_disk_to_partitioning_C (disk_number, c_size= None, c_letter=None):
    """
    创建NTFS的C分区
    
    Args:
        disk_number (int): 磁盘编号
        c_size (int, optional): C分区大小（MB），默认None
        c_letter (str, optional): C分区盘符，默认None
        
    Returns:
        bool: 初始化成功返回True，失败返回False
    """
    try:
        # 1. 检查管理员权限
        print("检查管理员权限...")
        if not is_admin():
            print("错误: 当前用户没有管理员权限，磁盘分区操作需要管理员权限")
            raise PermissionError("磁盘分区操作需要管理员权限")
        print("管理员权限验证通过")
        
        # 2. 验证传入参数正确
        print("验证输入参数...")
        
        # 使用现有的 validate_input_parameters 函数进行参数验证
        validation_result = validate_input_parameters(
            disk_number=disk_number,
            c_size=c_size,
            c_letter=c_letter
        )
        
        if not validation_result:
            print("错误: 参数验证失败，磁盘分区初始化终止")
            return False
        
        
        # 3. 构建diskpart命令
        print(f"开始为磁盘 {disk_number} 创建分区...")

        if c_size is not None and c_letter is not None:
            print("创建C分区...")
            c_partition_commands = [
                f"select disk {disk_number}",
                f"create partition primary size={c_size}",
                "format quick fs=ntfs override",
                f"assign letter={c_letter}"
            ]

            c_partition_result = execute_diskpart_command(c_partition_commands)
            if not c_partition_result:
                print("错误: C分区创建失败")
                return False
            print("C分区创建成功")

            # 4. 验证C分区创建成功
            # 使用disk_info.py模块直接验证盘符分配
            print(f"验证磁盘 {disk_number} 上的分区盘符 {c_letter} 是否分配成功...")
            
            # 等待2秒钟，以便系统有足够时间识别新创建的分区
            import time
            time.sleep(2)
            
            try:
                # 导入DiskManager类
                from disk_info import DiskManager
                
                # 创建磁盘管理器实例
                disk_manager = DiskManager()
                
                # 获取指定磁盘的信息
                disk_info = disk_manager.get_disk_by_index(disk_number)
                
                if disk_info is None:
                    print(f"验证失败: 未找到磁盘编号为 {disk_number} 的磁盘信息。")
                    return False
                
                # 检查该磁盘是否包含指定的盘符
                drive_letters = disk_info.drive_letters
                
                # 处理"Unknown"情况
                if drive_letters == "Unknown":
                    print(f"验证失败: 磁盘 {disk_number} 的盘符信息未知。")
                    return False
                
                # 将盘符字符串拆分为列表（盘符可能以逗号分隔）
                if drive_letters:
                    assigned_letters = [l.strip() for l in drive_letters.split(',')]
                else:
                    assigned_letters = []
                
                # 检查指定的盘符是否在该磁盘的盘符列表中
                if c_letter in assigned_letters:
                    print(f"验证成功: 磁盘 {disk_number} 已成功分配盘符 {c_letter}。")
                    # 输出磁盘详细信息用于日志记录
                    print(f"  磁盘名称: {disk_info.name}")
                    print(f"  磁盘容量: {disk_info.capacity}")
                    print(f"  分配的所有盘符: {drive_letters}")
                    print(f"  分区表格式: {disk_info.partition_style}")
                    print(f"磁盘 {disk_number} 分区初始化完成")
                    return True
                else:
                    print(f"验证失败: 磁盘 {disk_number} 未分配盘符 {c_letter}。")
                    print(f"  磁盘 {disk_number} 当前分配的盘符: {drive_letters}")
                    print(f"  预期盘符: {c_letter}")
                    print(f"磁盘 {disk_number} 分区验证失败")
                    return False
                    
            except ImportError as e:
                print(f"验证过程中发生错误: 导入disk_info模块失败 {e}")
                print("请确保disk_info.py文件存在于同一目录下")
                return False
            except Exception as e:
                print(f"验证过程中发生错误: {e}")
                print(f"磁盘编号: {disk_number}, 预期盘符: {c_letter}")
                return False
        else:
            print("没有指定C分区的大小或盘符，不执行任何分区操作。")
            # 如果没有提供C分区信息，我们认为操作是“成功”的，因为没有任务需要执行
            return True

    except PermissionError as e:
        print(f"权限错误: {e}")
        return False
    except ValueError as e:
        print(f"参数错误: {e}")
        return False
    except Exception as e:
        print(f"磁盘分区初始化过程中发生错误: {e}")
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



