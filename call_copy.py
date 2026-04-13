from common_functions import get_disk_letter, get_disk_manager
import os
import shutil


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
    
    available_letters = disk_info.drive_letters.split(", ")
    
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
    target_path = os.path.join(f"{target_drive}:", folder_name)
    
    try:
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        
        shutil.copytree(software_file, target_path)
        
        if os.path.exists(target_path) and os.path.isdir(target_path):
            if os.listdir(target_path):
                return f"成功：文件夹已复制到 {target_path}"
            else:
                return f"警告：文件夹已复制但目标文件夹为空"
        else:
            return f"错误：复制验证失败"
            
    except Exception as e:
        return f"错误：复制过程中发生异常 - {str(e)}"
