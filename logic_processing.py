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


def test_input(disk_number,gho_exe,bcd_exe,win_gho,efi_size,c_size,software_file):
    
    print(f"disk_number: {disk_number}")
    print(f"gho_exe: {gho_exe}")
    print(f"bcd_exe: {bcd_exe}")
    print(f"win_gho: {win_gho}")
    print(f"efi_size: {efi_size}")
    print(f"c_size: {c_size}")
    print(f"software_file: {software_file}")


if __name__ == "__main__":
    disk_number = 1
    efi_letter = get_disk_letter(disk_number, 'efi')
    print(efi_letter)