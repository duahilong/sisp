from disk_info import DiskManager
from common_functions import get_disk_letter
import os
import shutil


def verify_disk_letter(disk_number):
    """
    验证并返回指定磁盘的可用盘符
    
    Args:
        disk_number: 磁盘编号
    
    Returns:
        str: 返回验证成功的盘符（优先返回D，其次返回E）
        str: 如果两个盘符都验证失败，返回错误信息
    """
    try:
        # 获取D和E的盘符信息
        d_letter = get_disk_letter(disk_number, 'd')
        e_letter = get_disk_letter(disk_number, 'e')
        
        # 如果没有获取到任何盘符，返回错误
        if not d_letter and not e_letter:
            return "错误：无法获取磁盘的盘符信息"
        
        # 创建磁盘管理器实例
        disk_manager = DiskManager()
        
        # 获取磁盘信息
        disk_info = disk_manager.get_disk_by_index(disk_number)
        if not disk_info:
            return "错误：无法获取指定磁盘信息"
        
        # 获取该磁盘的所有盘符
        available_letters = disk_info.drive_letters.split(", ")
        
        # 验证D盘符
        if d_letter and d_letter in available_letters:
            return d_letter
        
        # D盘符验证失败，验证E盘符
        if e_letter and e_letter in available_letters:
            return e_letter
        
        # 两个盘符都验证失败
        return "错误：盘符验证失败"
        
    except Exception as e:
        return f"错误：验证盘符时发生异常 - {str(e)}"


def copy_software_folder(disk_number, software_file):
    """
    将软件文件夹复制到指定磁盘的根目录
    
    Args:
        disk_number: 磁盘编号
        software_file: 要复制的文件夹路径
    
    Returns:
        str: 复制成功返回成功信息和目标路径，失败返回错误信息
    """
    try:
        # 验证源文件夹是否存在
        if not os.path.exists(software_file):
            return f"错误：源文件夹 {software_file} 不存在"
        
        if not os.path.isdir(software_file):
            return f"错误：{software_file} 不是一个有效的文件夹"
        
        # 获取目标盘符
        target_drive = verify_disk_letter(disk_number)
        
        # 检查返回的是否是错误信息（错误信息通常包含"错误"字样）
        if isinstance(target_drive, str) and "错误" in target_drive:
            return f"获取目标盘符失败：{target_drive}"
        
        # 构建目标路径
        folder_name = os.path.basename(os.path.normpath(software_file))
        target_path = os.path.join(f"{target_drive}:", folder_name)
        
        # 如果目标文件夹已存在，先删除
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        
        # 复制文件夹
        shutil.copytree(software_file, target_path)
        
        # 验证复制是否成功
        if os.path.exists(target_path) and os.path.isdir(target_path):
            # 检查文件夹是否非空
            if os.listdir(target_path):
                return f"成功：文件夹已复制到 {target_path}"
            else:
                return f"警告：文件夹已复制但目标文件夹为空 {target_path}"
        else:
            return f"错误：复制验证失败，目标文件夹不存在 {target_path}"
            
    except Exception as e:
        return f"错误：复制过程中发生异常 - {str(e)}"


# if __name__ == "__main__":
#     disk_number = 2
#     result = verify_disk_letter(disk_number)
#     print(result)
#     software_file = r"D:\\常用软件"
#     result = copy_software_folder(disk_number, software_file)
#     print(result)