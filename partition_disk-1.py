import subprocess
import wmi
import os

def get_disk_name(disk_number):
    """
    获取指定硬盘的名称。

    参数：
    disk_number (int): 要获取名称的硬盘索引。

    返回：
    str: 硬盘的名称（如果找到），否则返回 None。
    """
    c = wmi.WMI()
    try:
        disks = c.Win32_DiskDrive(Index=disk_number)
        if disks:
            return disks[0].Caption  # 返回第一个匹配磁盘的名称
        else:
            return None
    except Exception:
        return None

def get_disk_size(disk_number):
    """
    获取指定硬盘的容量（以字节为单位）。

    参数：
    disk_number (int): 要获取容量的硬盘索引。

    返回：
    int: 硬盘的容量（字节），如果出错则返回 None。
    """
    c = wmi.WMI()
    try:
        disks = c.Win32_DiskDrive(Index=disk_number)
        if disks:
            return int(disks[0].Size)  # 返回第一个匹配磁盘的容量
        else:
            return None
    except Exception:
        return None

def validate_disk_operation(disk_number, efi_size=None, primary_size=None, first_letter=None, second_letter=None, efi_letter=None, operation_type="full"):
    """
    统一的磁盘操作验证函数，包含参数检查和diskpart超时检查
    
    参数：
    disk_number (int): 要操作的磁盘编号
    efi_size (int, optional): EFI分区大小 (MB)，仅完整操作需要
    primary_size (int, optional): 主分区大小 (MB)，仅完整操作需要
    first_letter (str, optional): 第一个分区的盘符，仅完整操作需要
    second_letter (str, optional): 第二个分区的盘符，仅完整操作需要
    efi_letter (str, optional): EFI分区的盘符，仅完整操作需要
    operation_type (str): 操作类型 - "full" (完整操作), "partitioning" (仅分区), "basic" (仅基础验证)
    
    返回：
    bool: 验证成功返回 True，否则返回 False 或抛出异常
    
    验证逻辑：
    1. 基础验证：磁盘编号、存在性检查
    2. 参数验证：根据操作类型验证相应参数
    3. diskpart可用性检查：检查系统是否可以执行diskpart命令
    """
    try:
        # 1. 基础验证 - 磁盘编号
        if disk_number is None or not isinstance(disk_number, int) or disk_number < 0:
            raise ValueError("磁盘编号必须为非负整数。")
        
        # 2. 磁盘存在性检查
        disk_name = get_disk_name(disk_number)
        if not disk_name:
            raise ValueError(f"磁盘 {disk_number} 不存在或无法访问。")

        # 3. 根据操作类型进行相应验证
        if operation_type == "full":
            # 完整验证 - 所有参数都需要
            if not _validate_full_operation_params(efi_size, primary_size, first_letter, second_letter, efi_letter):
                return False
                
            # 验证磁盘容量和分区大小
            if not _validate_disk_capacity(disk_number, primary_size):
                return False
                
        elif operation_type == "partitioning":
            # 分区操作验证 - 仅需要盘符
            if not _validate_partitioning_params(first_letter, second_letter, efi_letter):
                return False
        
        # 4. diskpart可用性检查
        if not _check_diskpart_availability():
            print("DiskPart命令不可用或权限不足")
            return False
            
        return True
        
    except ValueError as e:
        print(f"参数验证失败: {e}")
        return False
    except Exception as e:
        print(f"验证过程中发生未知错误: {e}")
        return False

def _validate_full_operation_params(efi_size, primary_size, first_letter, second_letter, efi_letter):
    """
    验证完整操作的所有参数
    """
    # 验证所有必需参数是否提供且有效
    if efi_size is None or primary_size is None or \
       first_letter is None or second_letter is None or efi_letter is None:
        raise ValueError("完整操作需要所有参数：efi_size, primary_size, first_letter, second_letter, efi_letter")
    
    # 验证分区大小参数
    if not isinstance(efi_size, int) or efi_size <= 0:
        raise ValueError("EFI分区大小必须为正整数。")
    if not isinstance(primary_size, int) or primary_size <= 0:
        raise ValueError("主分区大小必须为正整数。")
    
    # 验证盘符参数（自动转换为大写）
    valid_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if not isinstance(first_letter, str) or len(first_letter) != 1 or first_letter.upper() not in valid_letters:
        raise ValueError("第一个分区盘符必须是一个英文字母。")
    if not isinstance(second_letter, str) or len(second_letter) != 1 or second_letter.upper() not in valid_letters:
        raise ValueError("第二个分区盘符必须是一个英文字母。")
    if not isinstance(efi_letter, str) or len(efi_letter) != 1 or efi_letter.upper() not in valid_letters:
        raise ValueError("EFI分区盘符必须是一个大写英文字母。")
    
    # 验证盘符不能重复（使用大写比较）
    first_upper = first_letter.upper()
    second_upper = second_letter.upper()
    efi_upper = efi_letter.upper()
    
    if first_upper == second_upper or first_upper == efi_upper or second_upper == efi_upper:
        raise ValueError("所有分区的盘符必须不同。")
    
    return True

def _validate_partitioning_params(first_letter, second_letter, efi_letter):
    """
    验证分区操作的盘符参数
    """
    if first_letter is None or second_letter is None or efi_letter is None:
        raise ValueError("分区操作需要盘符参数：first_letter, second_letter, efi_letter")
    
    valid_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # 验证每个盘符
    for letter, name in [(first_letter, "第一个分区"), (second_letter, "第二个分区"), (efi_letter, "EFI分区")]:
        if not isinstance(letter, str) or len(letter) != 1 or letter.upper() not in valid_letters:
            raise ValueError(f"{name}盘符必须是一个英文字母。")
    
    # 检查盘符重复
    first_upper = first_letter.upper()
    second_upper = second_letter.upper()
    efi_upper = efi_letter.upper()
    
    if first_upper == second_upper or first_upper == efi_upper or second_upper == efi_upper:
        raise ValueError("所有分区的盘符必须不同。")
    
    return True

def _validate_disk_capacity(disk_number, primary_size):
    """
    验证磁盘容量是否满足要求
    """
    # 验证磁盘容量是否大于 100GB
    disk_size_bytes = get_disk_size(disk_number)
    if disk_size_bytes is None:
        raise ValueError(f"无法获取磁盘 {disk_number} 的容量。")

    disk_size_gb = disk_size_bytes / (1024 ** 3)  # 将字节转换为 GB
    if disk_size_gb < 100:
        print(f"磁盘 {disk_number} 的容量 ({disk_size_gb:.2f} GB) 小于 100 GB，禁止操作。")
        return False
    
    # 验证主分区大小不超过磁盘容量
    primary_size_gb = primary_size / 1024  # 将MB转换为GB
    if primary_size_gb >= disk_size_gb:
        print(f"主分区大小 ({primary_size_gb:.2f} GB) 不能大于或等于磁盘总容量 ({disk_size_gb:.2f} GB)。")
        return False
    
    return True

def _check_diskpart_availability():
    """
    检查 diskpart 命令是否可用（使用完整路径），以规避 PATH 和环境问题。
    """
    DISKPART_PATH = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32', 'diskpart.exe')
    
    # 确保 diskpart.exe 文件存在
    if not os.path.exists(DISKPART_PATH):
        print(f"致命错误：未找到 DiskPart 可执行文件于 {DISKPART_PATH}")
        return False
        
    try:
        # 尝试运行 diskpart 的帮助命令来检查可用性
        # 使用完整路径，确保在任何环境下都能找到 diskpart.exe
        result = subprocess.run([DISKPART_PATH, "/?"], 
                                capture_output=True, 
                                text=True, 
                                timeout=10,
                                check=False)
        
        # DiskPart 成功运行并返回帮助信息时，返回码通常是 0 或 1。
        # 如果返回码不是 0 或 1，但输出中包含 "DiskPart" 字样，我们也可以认为是可用的。
        if result.returncode in [0, 1]:
            return True
        
        # 针对某些特殊环境，如果返回码不明确，但标准输出不为空，也认为可用
        if result.stdout.strip():
             return True
             
        # 否则，可能是权限或系统错误
        print(f"DiskPart 检查返回码为 {result.returncode}，输出为空。")
        return False
        
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
        print(f"运行 DiskPart 检查时发生子进程错误: {e}")
        return False
    except Exception as e:
        print(f"运行 DiskPart 检查时发生未知错误: {e}")
        return False

def initialize_disk_to_gpt(disk_number, efi_size, primary_size, first_letter, second_letter, efi_letter):
    """
    使用 DiskPart 将指定的磁盘初始化为 GPT，并进行错误检查和验证，并创建分区。

    参数：
    disk_number (int): 要初始化的磁盘编号。
    efi_size (int): EFI分区大小 (MB)。
    primary_size (int): 主分区大小 (MB)，必须小于磁盘总容量。
    first_letter (str): 第一个分区的盘符。
    second_letter (str): 第二个分区的盘符。
    efi_letter (str): EFI分区的盘符。

    返回：
    bool: 初始化成功返回 True，否则返回 False。
    """
    try:
        # 统一验证：参数检查和diskpart可用性检查
        if not validate_disk_operation(disk_number, efi_size,  first_letter, second_letter, efi_letter, operation_type="full"):
            return False

        print(f"开始初始化磁盘 {disk_number}...")
        
        # 第一部分：磁盘初始化、GPT转换和基础分区创建
        diskpart_commands_part1 = [
            f"select disk {disk_number}",
            "clean",
            "convert gpt",
            f"create partition efi size={efi_size}",
            
        ]

        diskpart_script_part1 = "\n".join(diskpart_commands_part1)

        # 使用超时机制运行diskpart命令第一部分
        completed_process_part1 = run_diskpart_with_timeout(diskpart_script_part1, timeout=120)  # 2分钟超时
        if completed_process_part1 is None:
            print(f"磁盘 {disk_number} 第一部分操作超时，diskpart命令执行时间过长")
            return False

        # 检查第一部分执行结果
        success_part1 = analyze_diskpart_result(disk_number, completed_process_part1)
        if not success_part1:
            print(f"磁盘 {disk_number} 第一部分初始化失败")
            return False

        print(f"磁盘 {disk_number} 第一部分初始化成功，继续第二部分...")
        
        # 第二部分：剩余的分区操作和格式化
        return complete_disk_partitioning(disk_number, first_letter, second_letter, efi_letter)

    except subprocess.CalledProcessError as e:
        print(f"磁盘 {disk_number} 初始化为 GPT 或创建分区失败：{e}")
        return False
    except ValueError as e:
        print(f"磁盘 {disk_number} 初始化或创建分区过程中发生值错误：{e}")
        return False
    except Exception as e:
        print(f"磁盘 {disk_number} 初始化或创建分区过程中发生未知错误：{e}")
        return False

def complete_disk_partitioning(disk_number, primary_size, first_letter, second_letter, efi_letter):
    """
    完成磁盘分区的第二部分操作：格式化、分配盘符和创建EFI分区
    
    参数：
    disk_number (int): 磁盘编号
    primary_size (int): 主分区大小 (MB)，必须小于磁盘总容量。   
    first_letter (str): 第一个分区的盘符
    second_letter (str): 第二个分区的盘符
    efi_letter (str): EFI分区的盘符
    
    返回：
    bool: 操作成功返回 True，否则返回 False
    """
    try:
        # 统一验证：基础检查和diskpart可用性检查（仅分区操作验证）
        if not validate_disk_operation(disk_number, first_letter=first_letter, second_letter=second_letter, efi_letter=efi_letter, operation_type="partitioning"):
            return False

        print(f"开始磁盘 {disk_number} 的分区格式化操作...")
        
        diskpart_commands_part2 = [
            f"create partition primary size={primary_size}",
            "format quick fs=ntfs override",
            f"assign letter={first_letter}",
            "create partition primary",
            "format quick fs=ntfs override",
            f"assign letter={second_letter}",
            f"select disk {disk_number}",
            "select partition 1",
            "delete partition override",
            "select partition 2",
            "delete partition override",
            f"select disk {disk_number}",
            "create partition efi ",
            "format quick fs=fat32",
            f"assign letter={efi_letter}",
            "exit",
        ]

        diskpart_script_part2 = "\n".join(diskpart_commands_part2)

        # 使用超时机制运行diskpart命令第二部分
        completed_process_part2 = run_diskpart_with_timeout(diskpart_script_part2, timeout=120)  # 2分钟超时
        if completed_process_part2 is None:
            print(f"磁盘 {disk_number} 第二部分操作超时，diskpart命令执行时间过长")
            return False

        # 检查第二部分执行结果
        success_part2 = analyze_diskpart_result(disk_number, completed_process_part2)
        if success_part2:
            print(f"磁盘 {disk_number} 初始化成功")
        else:
            print(f"磁盘 {disk_number} 第二部分分区操作失败")
        return success_part2

    except subprocess.CalledProcessError as e:
        print(f"磁盘 {disk_number} 第二部分分区操作失败：{e}")
        return False
    except ValueError as e:
        print(f"磁盘 {disk_number} 第二部分分区操作过程中发生值错误：{e}")
        return False
    except Exception as e:
        print(f"磁盘 {disk_number} 第二部分分区操作过程中发生未知错误：{e}")
        return False

def run_diskpart_with_timeout(diskpart_script, timeout=120):
    """
    运行diskpart命令并设置超时，防止命令卡住
    
    参数：
    diskpart_script (str): diskpart脚本内容
    timeout (int): 超时时间（秒），默认120秒
    
    返回：
    subprocess.CompletedProcess or None: 成功返回结果对象，超时或失败返回None
    """
    try:
        # 使用Popen实现更精细的控制
        process = subprocess.Popen(
            ["diskpart"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 发送命令并等待响应
        try:
            stdout, stderr = process.communicate(input=diskpart_script, timeout=timeout)
            
            # 创建CompletedProcess对象
            return subprocess.CompletedProcess(
                args=["diskpart"],
                returncode=process.returncode,
                stdout=stdout,
                stderr=stderr
            )
            
        except subprocess.TimeoutExpired:
            # 超时处理
            print(f"DiskPart命令执行超时（{timeout}秒），正在终止进程...")
            
            # 尝试优雅终止
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 强制终止
                process.kill()
                process.wait()
            
            print("DiskPart进程已终止")
            return None
            
    except Exception as e:
        print(f"运行DiskPart命令时发生错误: {e}")
        return None

def run_diskpart_with_progress(diskpart_script, timeout=120):
    """
    运行diskpart命令并监控进度，提供实时反馈
    
    参数：
    diskpart_script (str): diskpart脚本内容
    timeout (int): 超时时间（秒），默认120秒
    
    返回：
    subprocess.CompletedProcess or None: 成功返回结果对象，超时或失败返回None
    """
    try:
        import threading
        import time
        
        # 启动进程
        process = subprocess.Popen(
            ["diskpart"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 进度监控线程
        def monitor_progress():
            """监控命令执行进度"""
            start_time = time.time()
            last_output = ""
            
            while process.poll() is None:
                try:
                    # 读取部分输出
                    output = process.stdout.read(100)  # 读取100字符
                    if output and output != last_output:
                        last_output = output
                        # 检查是否有进度指示
                        if "完成" in output or "completed" in output.lower():
                            print(".", end="", flush=True)
                        elif "正在" in output or "processing" in output.lower():
                            print("*", end="", flush=True)
                    
                    # 每10秒显示一次进度
                    elapsed = time.time() - start_time
                    if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                        print(f"\n[进度] 已执行 {int(elapsed)} 秒...")
                    
                    time.sleep(0.5)  # 避免CPU占用过高
                    
                except:
                    break  # 进程结束或出错时退出
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        monitor_thread.start()
        
        print("[开始] 正在执行DiskPart命令...")
        
        try:
            # 发送命令并等待完成
            stdout, stderr = process.communicate(input=diskpart_script, timeout=timeout)
            
            # 等待监控线程结束
            monitor_thread.join(timeout=2)
            
            print("\n[完成] DiskPart命令执行结束")
            
            # 创建CompletedProcess对象
            return subprocess.CompletedProcess(
                args=["diskpart"],
                returncode=process.returncode,
                stdout=stdout,
                stderr=stderr
            )
            
        except subprocess.TimeoutExpired:
            # 超时处理
            print(f"\n[超时] DiskPart命令执行超时（{timeout}秒）")
            
            # 尝试优雅终止
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("[强制] 强制终止DiskPart进程")
                process.kill()
                process.wait()
            
            return None
            
    except Exception as e:
        print(f"[错误] 运行DiskPart命令时发生错误: {e}")
        return None

def analyze_diskpart_result(disk_number, completed_process):
    """
    分析DiskPart命令执行结果，判断操作是否成功
    
    参数：
    disk_number (int): 磁盘编号
    completed_process (subprocess.CompletedProcess): subprocess运行结果
    
    返回：
    bool: 操作成功返回True，失败返回False
    """
    try:
        # 获取返回码、标准输出和标准错误
        return_code = completed_process.returncode
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        
        # 首先检查返回码
        if return_code != 0:
            return False
        
        # 检查标准输出中的关键成功/失败指标
        success_indicators = [
            "成功",           # 中文成功标识
            "success",        # 英文成功标识
            "completed",      # 完成标识
            "操作成功完成",    # 中文完成标识
        ]
        
        failure_indicators = [
            "失败",           # 中文失败标识
            "failed",         # 英文失败标识
            "错误",           # 中文错误标识
            "error",          # 英文错误标识
            "无法",           # 无法完成标识
            "cannot",         # 无法完成英文标识
            "拒绝访问",       # 权限问题
            "access denied",  # 权限问题英文
        ]
        
        # 转换为大写进行不区分大小写的检查
        stdout_upper = stdout.upper() if stdout else ""
        stderr_upper = stderr.upper() if stderr else ""
        
        # 检查失败指标
        for indicator in failure_indicators:
            if indicator.upper() in stdout_upper or indicator.upper() in stderr_upper:
                return False
        
        # 检查成功指标
        for indicator in success_indicators:
            if indicator.upper() in stdout_upper:
                return True
        
        # 如果没有明确的成功标识但有输出，认为可能是成功的
        if stdout.strip():
            return True
        
        return False
            
    except Exception as e:
        return False

# 示例用法：调用函数时必须提供所有必需参数
# success = initialize_disk_to_gpt(
#     disk_number=2,         # 磁盘编号
#     efi_size=200,          # EFI分区大小200MB
#     primary_size=50000,    # 主分区大小50000MB（约50GB，必须小于磁盘总容量）
#     first_letter="L",      # 第一个分区盘符L
#     second_letter="K",     # 第二个分区盘符K
#     efi_letter="J"         # EFI分区盘符J
# )
# if success:
#     print("磁盘初始化成功！")
# else:
#     print("磁盘初始化失败。")

# 错误示例：缺少参数将导致错误
# success = initialize_disk_to_gpt(2)  # 错误：缺少必需参数
# success = initialize_disk_to_gpt(2, 200, 225290, "Y", "Y", "X")  # 错误：盘符重复
