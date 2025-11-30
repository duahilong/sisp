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

def get_disk_labels(data_list, target_disk_number):
    """
    根据传入的 disk_number 查找对应的记录，并返回其 efi_letter, c_letter, d_letter, e_letter 的值。

    Args:
        data_list (list): 包含磁盘记录字典的列表。
        target_disk_number (int): 目标磁盘的编号。

    Returns:
        tuple or None: 
            如果找到记录，返回一个包含 (efi_label, c_label, d_label, e_label) 的元组。
            如果未找到记录，返回 None。
    """
    
    # 1. 遍历列表，查找匹配的记录
    for record in data_list:
        if record.get("disk_number") == target_disk_number:
            
            # 2. 如果找到匹配项，提取所需的四个标签值
            efi = record.get("efi_letter")
            c = record.get("c_letter")
            d = record.get("d_letter")
            e = record.get("e_letter")
            
            # 3. 将这四个值打包成一个元组 (tuple) 返回
            return (efi, c, d, e)
            
    # 4. 如果循环结束仍未找到，则返回 None
    return None

target_disk = 2
result = get_disk_labels(number_list, target_disk)

if result:
    # 使用元组解包 (Tuple Unpacking) 将结果分别赋值给变量
    efi_letter, c_letter, d_letter, e_letter = result
    
    print(f"--- 磁盘 {target_disk} 的标签 ---")
    print(f"EFI Letter: {efi_letter}")  # Q
    print(f"C Letter: {c_letter}")      # R
    print(f"D Letter: {d_letter}")      # S
    print(f"E Letter: {e_letter}")      # T
else:
    print(f"未找到 disk_number 为 {target_disk} 的记录。")
