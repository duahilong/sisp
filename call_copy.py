from common_functions import get_disk_letter, get_disk_manager
import os
import shutil
import ctypes


def verify_disk_letter(disk_number):
    """验证并返回指定磁盘的可用盘符"""
    d_letter = get_disk_letter(disk_number, 'd')
    e_letter = get_disk_letter(disk_number, 'e')
    
    if not d_letter and not e_letter:
        return None
    
    disk_manager = get_disk_manager()
    disk_info = disk_manager.get_disk_by_index(disk_number)
    
    if not disk_info:
        return None
    
    drive_letters = getattr(disk_info, "drive_letters", "")
    if not drive_letters or drive_letters == "Unknown":
        return None

    available_letters = [letter.strip() for letter in drive_letters.split(",") if letter.strip()]
    
    if d_letter and d_letter in available_letters:
        return d_letter
    
    if e_letter and e_letter in available_letters:
        return e_letter
    
    return None


def copy_software_folder(disk_number, software_file):
    """将软件文件夹复制到指定磁盘的根目录"""
    if not os.path.exists(software_file):
        return f"错误：源文件夹 {software_file} 不存在"
    
    if not os.path.isdir(software_file):
        return f"错误：{software_file} 不是一个有效的文件夹"
    
    target_drive = verify_disk_letter(disk_number)
    
    if not target_drive:
        return "错误：无法获取目标盘符"
    
    folder_name = os.path.basename(os.path.normpath(software_file))
    target_root = f"{target_drive}:\\"
    target_path = os.path.join(target_root, folder_name)
    
    try:
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        
        shutil.copytree(software_file, target_path)
        _copy_hidden_attributes_recursive(software_file, target_path)
        
        if os.path.exists(target_path) and os.path.isdir(target_path):
            if os.listdir(target_path):
                return f"成功：文件夹已复制到 {target_path}"
            else:
                return f"警告：文件夹已复制但目标文件夹为空"
        else:
            return f"错误：复制验证失败"
            
    except Exception as e:
        return f"错误：复制过程中发生异常 - {str(e)}"


def _get_windows_file_attributes(path):
    """获取Windows文件属性。失败时返回None。"""
    attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
    if attrs == 0xFFFFFFFF:
        return None
    return attrs


def _set_windows_file_attributes(path, attrs):
    """设置Windows文件属性。"""
    return bool(ctypes.windll.kernel32.SetFileAttributesW(str(path), attrs))


def _sync_file_attributes(src_path, dst_path):
    """同步源路径的全部Windows文件属性到目标路径。"""
    src_attrs = _get_windows_file_attributes(src_path)
    if src_attrs is None:
        return
    _set_windows_file_attributes(dst_path, src_attrs)


def _copy_hidden_attributes_recursive(src_root, dst_root):
    """递归复制文件和文件夹的全部属性，包含根目录和所有子项。"""
    _sync_file_attributes(src_root, dst_root)

    for root, dirs, files in os.walk(src_root):
        relative = os.path.relpath(root, src_root)
        target_root = dst_root if relative == "." else os.path.join(dst_root, relative)

        for name in dirs:
            src_dir = os.path.join(root, name)
            dst_dir = os.path.join(target_root, name)
            if os.path.exists(dst_dir):
                _sync_file_attributes(src_dir, dst_dir)

        for name in files:
            src_file = os.path.join(root, name)
            dst_file = os.path.join(target_root, name)
            if os.path.exists(dst_file):
                _sync_file_attributes(src_file, dst_file)
