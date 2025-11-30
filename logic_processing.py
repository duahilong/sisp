from partition_disk import initialize_disk_to_gpt
from partition_disk import initialize_disk_to_partitioning_C
from partition_disk import initialize_disk_to_partitioning_D
from partition_disk import initialize_disk_to_partitioning_E


number_list = [
    {
        "disk_number": 1,
        "efi_letter": "E",
        "c_letter": "F",
        "d_letter": "G",
        "e_letter": "H",
    },
    {
        "disk_number": 2,
        "efi_letter": "I",
        "c_letter": "J",
        "d_letter": "K",
        "e_letter": "L",
    },
    {
        "disk_number": 3,
        "efi_letter": "M",
        "c_letter": "N",
        "d_letter": "O",
        "e_letter": "P",
    },
    {
        "disk_number": 4,
        "efi_letter": "Q",
        "c_letter": "R",
        "d_letter": "S",
        "e_letter": "T",
    },
    {
        "disk_number": 5,
        "efi_letter": "U",
        "c_letter": "V",
        "d_letter": "W",
        "e_letter": "X",
    },
    {
        "disk_number": 6,
        "efi_letter": "Y",
        "c_letter": "Z",
        "d_letter": "A",
        "e_letter": "B",
    },
]


def get_disk_letter(disk_number, letter_type):
    """
    获取指定磁盘的特定分区字母
    
    Args:
        disk_number: 磁盘编号 (1-6)
        letter_type: 分区类型 ('efi', 'c', 'd', 'e')
    
    Returns:
        str: 对应的分区字母，如果未找到则返回None
        
    Example:
        >>> get_disk_letter(3, 'efi')
        'M'
    """
    for disk_config in number_list:
        if disk_config["disk_number"] == disk_number:
            if letter_type == 'efi':
                return disk_config["efi_letter"]
            elif letter_type == 'c':
                return disk_config["c_letter"]
            elif letter_type == 'd':
                return disk_config["d_letter"]
            elif letter_type == 'e':
                return disk_config["e_letter"]
            else:
                return None
    return None


def process_disk_numbers(disk_numbers, efi_size, c_size):
    """
    处理磁盘编号列表，逐个调用all_disk_partitions函数
    
    Args:
        disk_numbers: 磁盘编号列表，如 [1, 2]
        efi_size: EFI分区大小 (MB)
        c_size: C盘分区大小 (MB)
    
    Returns:
        list: 处理结果的列表
    """
    # 验证输入必须是列表
    if not isinstance(disk_numbers, list):
        raise ValueError(f"disk_numbers必须是列表格式，当前类型: {type(disk_numbers)}")
    
    results = []
    for disk_number in disk_numbers:
        try:
            all_disk_partitions(disk_number, efi_size, c_size)
            results.append({
                "disk_number": disk_number,
                "status": "success",
                "message": f"磁盘 {disk_number} 处理成功"
            })
        except Exception as e:
            results.append({
                "disk_number": disk_number,
                "status": "error",
                "message": f"磁盘 {disk_number} 处理失败: {str(e)}"
            })
    
    return results


def all_disk_partitions(disk_number, efi_size, c_size):
    """
    初始化磁盘分区
    
    Args:
        disk_number: 磁盘编号 (1-6)
        efi_size: EFI分区大小 (MB)
        c_size: C盘分区大小 (MB)
    """
    efi_letter = get_disk_letter(disk_number, 'efi')
    c_letter = get_disk_letter(disk_number, 'c')
    d_letter = get_disk_letter(disk_number, 'd')
    e_letter = get_disk_letter(disk_number, 'e')
    print(f"c_size: {c_size}")

    # 顺序执行：第一步
    initialize_disk_to_gpt(disk_number, efi_size, efi_letter)
    
    # 顺序执行：第二步
    initialize_disk_to_partitioning_C(disk_number, c_size, c_letter)
    
    # 顺序执行：第三步
    initialize_disk_to_partitioning_D(disk_number, d_letter,efi_size,c_size)
    
    # 顺序执行：第四步
    initialize_disk_to_partitioning_E(disk_number, e_letter)



def test_input(disk_number,gho_exe,bcd_exe,win_gho,efi_size,c_size,software_file):

    print(f"disk_number: {disk_number}")
    print(f"gho_exe: {gho_exe}")
    print(f"bcd_exe: {bcd_exe}")
    print(f"win_gho: {win_gho}")
    print(f"efi_size: {efi_size}")
    print(f"c_size: {c_size}")
    print(f"software_file: {software_file}")


if __name__ == "__main__":
    # 测试 process_disk_numbers 函数
    
    # 测试: 列表格式的磁盘编号
    print("测试: 列表格式的磁盘编号 [1, 2]")
    disk_numbers = [1, 2]
    efi_size = 500
    c_size = 102400
    
    result = process_disk_numbers(disk_numbers, efi_size, c_size)
    print(f"结果: {result}")
    
    print("\n" + "="*50)
    print("处理结果:")
    for item in result:
        status_symbol = "✓" if item["status"] == "success" else "✗"
        print(f"  {status_symbol} {item['message']}")
    
    # 原始测试（保持兼容性）
    # disk_number = 1
    # efi_letter = get_disk_letter(disk_number, 'efi')
    # print(efi_letter)

