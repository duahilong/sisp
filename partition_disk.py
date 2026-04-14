import os
import string
import subprocess
import tempfile
import time
from common_functions import get_disk_manager


def is_admin():
    """检查当前是否以管理员权限运行"""
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def execute_diskpart_command(commands, capture_output=False):
    """执行DiskPart命令"""
    script_path = None
    try:
        if not isinstance(commands, list) or not commands:
            raise ValueError("DiskPart命令列表不能为空")

        normalized_commands = [str(cmd).strip() for cmd in commands if str(cmd).strip()]
        if not normalized_commands:
            raise ValueError("DiskPart命令列表无有效命令")

        script_content = "\n".join(normalized_commands) + "\nexit\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='ascii') as script_file:
            script_file.write(script_content)
            script_path = script_file.name
        
        if capture_output:
            result = subprocess.run(
                ['diskpart', '/s', script_path],
                capture_output=True,
                text=True,
                encoding='gbk',
                errors='replace',
                timeout=120
            )
            return result.stdout + result.stderr
        else:
            result = subprocess.run(
                ['diskpart', '/s', script_path],
                capture_output=True,
                text=True,
                encoding='gbk',
                errors='replace',
                timeout=120
            )
            if result.returncode != 0:
                output = (result.stdout or "") + (result.stderr or "")
                print(f"[ERROR] DiskPart执行失败，返回码={result.returncode}")
                if output.strip():
                    print(output)
            return result.returncode == 0
                
    except subprocess.TimeoutExpired:
        print("错误: DiskPart命令执行超时")
        return False
    except Exception as e:
        print(f"错误: 执行DiskPart命令时发生异常: {e}")
        return False
    finally:
        if script_path and os.path.exists(script_path):
            try:
                os.unlink(script_path)
            except Exception:
                pass


def _validate_partition_letter(letter, name):
    """验证分区盘符格式"""
    if not isinstance(letter, str) or len(letter) != 1 or letter not in string.ascii_uppercase:
        raise ValueError(f"{name}必须是单个大写字母。")


def _verify_partition_created(disk_number, expected_letter):
    """验证分区创建成功"""
    time.sleep(2)
    
    disk_manager = get_disk_manager()
    disk_info = disk_manager.get_disk_by_index(disk_number)
    
    if disk_info is None:
        return False, f"未找到磁盘编号为 {disk_number} 的磁盘信息"
    
    drive_letters = disk_info.drive_letters
    
    if drive_letters == "Unknown":
        return False, f"磁盘 {disk_number} 的盘符信息未知"
    
    assigned_letters = [l.strip() for l in drive_letters.split(',')]
    
    if expected_letter in assigned_letters:
        return True, f"磁盘 {disk_number} 分区初始化完成"
    else:
        return False, f"未分配预期盘符 {expected_letter}，实际盘符: {drive_letters}"


def initialize_disk_to_gpt(disk_number, efi_size=None, efi_letter=None):
    """使用 DiskPart 将指定的磁盘初始化为 GPT"""
    
    if not is_admin():
        print("[ERROR] 权限错误: 磁盘分区操作需要管理员权限")
        return False
    
    disk_manager = get_disk_manager()
    disk_info = disk_manager.get_disk_by_index(disk_number)
    
    if disk_info is None:
        print(f"[ERROR] 错误: 未找到磁盘 {disk_number}")
        return False
    
    diskpart_commands = [
        f"select disk {disk_number}",
        "clean",
        "convert gpt",
        "list partition",
    ]
    
    if not execute_diskpart_command(diskpart_commands):
        print(f"[ERROR] 磁盘 {disk_number} 的GPT初始化失败")
        return False
    
    msr_delete_commands = [
        f"select disk {disk_number}",
        "list partition",
        "select partition 1",
        "delete partition override"
    ]
    execute_diskpart_command(msr_delete_commands)
    
    partition_style = disk_manager._get_partition_style(disk_number)
    if partition_style != "GPT":
        print(f"[ERROR] 磁盘 {disk_number} 格式为 '{partition_style}'，不是GPT")
        return False
    
    if efi_size is not None and efi_letter is not None:
        _validate_partition_letter(efi_letter, "EFI盘符")
        
        efi_commands = [
            f"select disk {disk_number}",
            f"create partition efi size={efi_size}",
            f"format fs=fat32 quick label=EFI OVERRIDE",
            f"assign letter={efi_letter}"
        ]
        
        if not execute_diskpart_command(efi_commands):
            print(f"[ERROR] EFI分区创建失败")
            return False
    
    print("[OK] 磁盘GPT初始化成功完成")
    return True


def initialize_disk_to_partitioning_C(disk_number, c_size=None, c_letter=None):
    """创建NTFS的C分区"""
    
    if not is_admin():
        print("[ERROR] 权限错误: 磁盘分区操作需要管理员权限")
        return False
    
    print("管理员权限验证通过")
    
    if c_size is not None and c_letter is not None:
        if not isinstance(c_size, int) or c_size <= 0:
            print(f"[ERROR] 参数错误: C分区大小必须是正整数")
            return False
        
        _validate_partition_letter(c_letter, "C分区盘符")
        
        print(f"开始为磁盘 {disk_number} 创建分区...")
        
        c_partition_commands = [
            f"select disk {disk_number}",
            f"create partition primary size={c_size}",
            "format quick fs=ntfs override",
            f"assign letter={c_letter}"
        ]

        if not execute_diskpart_command(c_partition_commands):
            print(f"[ERROR] C分区创建失败")
            return False
        
        success, msg = _verify_partition_created(disk_number, c_letter)
        if success:
            print("[OK] C分区创建成功")
            print(msg)
            return True
        else:
            print(f"[ERROR] {msg}")
            return False
    
    print("没有指定C分区的大小或盘符，不执行任何分区操作。")
    return True


def initialize_disk_to_partitioning_D(disk_number, d_letter=None, efi_size=None, c_size=None):
    """创建NTFS的D分区"""
    
    if not is_admin():
        print("[ERROR] 权限错误: 磁盘分区操作需要管理员权限")
        return False
    
    print("管理员权限验证通过")
    
    if d_letter is not None and c_size is not None and efi_size is not None:
        _validate_partition_letter(d_letter, "D分区盘符")
        
        if efi_size <= 0 or c_size <= 0:
            print(f"[ERROR] 参数错误: EFI和C分区大小必须为正整数")
            return False
        
        print(f"开始为磁盘 {disk_number} 创建分区...")
        
        disk_manager = get_disk_manager()
        disk_info = disk_manager.get_disk_by_index(disk_number)
        
        if disk_info is None:
            print(f"[ERROR] 磁盘信息获取失败")
            return False
        
        disk_capacity_gb = float(disk_info.capacity.replace("GB", "").strip())
        total_disk_capacity_int = int(disk_capacity_gb * 1024)
        
        calculated_d_size = total_disk_capacity_int - int(efi_size) - int(c_size)
        d_size = calculated_d_size // 2
        
        print(f"D分区大小: {d_size} MB")
        
        if d_size <= 0:
            print(f"[ERROR] 分区大小计算失败: D分区大小无效")
            return False
        
        d_partition_commands = [
            f"select disk {disk_number}",
            f"create partition primary size={int(d_size)}",
            "format quick fs=ntfs override",
            f"assign letter={d_letter}"
        ]

        if not execute_diskpart_command(d_partition_commands):
            print(f"[ERROR] D分区创建失败")
            return False
        
        success, msg = _verify_partition_created(disk_number, d_letter)
        if success:
            print("[OK] D分区创建成功")
            print(msg)
            return True
        else:
            print(f"[ERROR] {msg}")
            return False
    
    print("没有指定D分区的盘符或C分区大小，不执行任何分区操作。")
    return True


def initialize_disk_to_partitioning_E(disk_number, e_letter=None):
    """创建NTFS的E分区，使用所有剩余空间"""
    
    if not is_admin():
        print("[ERROR] 权限错误: 磁盘分区操作需要管理员权限")
        return False
    
    print("管理员权限验证通过")
    
    if e_letter is None:
        print(f"[ERROR] 参数错误: E分区盘符不能为空")
        return False
    
    _validate_partition_letter(e_letter, "E分区盘符")
    
    print(f"开始为磁盘 {disk_number} 创建分区...")

    e_partition_commands = [
        f"select disk {disk_number}",
        "create partition primary",
        "format quick fs=ntfs override",
        f"assign letter={e_letter}"
    ]

    if not execute_diskpart_command(e_partition_commands):
        print(f"[ERROR] E分区创建失败")
        return False
    
    success, msg = _verify_partition_created(disk_number, e_letter)
    if success:
        print("[OK] E分区创建成功")
        print(msg)
        return True
    else:
        print(f"[ERROR] {msg}")
        return False
