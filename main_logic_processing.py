import sys
import time
import argparse
from typing import Dict, Any, Optional

from partition_disk import initialize_disk_to_gpt
from partition_disk import initialize_disk_to_partitioning_C
from partition_disk import initialize_disk_to_partitioning_D
from partition_disk import initialize_disk_to_partitioning_E
from call_ghost import call_ghost
from call_bcdboot import repair_boot_loader
from call_copy import copy_software_folder
from common_functions import get_disk_letter, read_json_config, get_disk_manager


def pause_if_interactive(prompt: str = "请按 Enter 键退出...") -> None:
    """仅在交互终端中暂停，避免自动化场景阻塞。"""
    try:
        if sys.stdin and sys.stdin.isatty():
            input(prompt)
    except EOFError:
        pass


def parse_capacity_gb(capacity_text: str) -> float:
    """将磁盘容量字符串转换为 GB 浮点数。"""
    if not isinstance(capacity_text, str):
        raise ValueError("capacity_text 必须是字符串")

    normalized = capacity_text.upper().replace("GB", "").strip()
    return float(normalized)


def get_dynamic_c_size(disk_size_gb: float) -> int:
    """根据磁盘容量返回动态 C 分区大小（MB）。"""
    if disk_size_gb < 600:
        return 153600
    if disk_size_gb < 1200:
        return 204800
    return 307200


def resolve_c_size(disk_number: int, fallback_c_size: int, config_data: Dict[str, Any]) -> int:
    """根据开关决定是否动态计算 C 分区大小。"""
    enable_dynamic_c_size = bool(config_data.get("enable_dynamic_c_size", False))
    if not enable_dynamic_c_size:
        return fallback_c_size

    try:
        disk_manager = get_disk_manager()
        disk_info = disk_manager.get_disk_by_index(disk_number)
        if disk_info is None:
            print(f"[WARN] 未获取到磁盘 {disk_number} 信息，沿用配置 c_size={fallback_c_size}")
            return fallback_c_size

        disk_size_gb = parse_capacity_gb(disk_info.capacity)
        dynamic_c_size = get_dynamic_c_size(disk_size_gb)
        print(f"[OK] 动态C分区已启用: 磁盘 {disk_number} 容量 {disk_size_gb:.2f}GB -> c_size={dynamic_c_size}")
        return dynamic_c_size
    except Exception as e:
        print(f"[WARN] 动态计算 c_size 失败({e})，沿用配置 c_size={fallback_c_size}")
        return fallback_c_size


def windows_disk_to_ghost_disk(windows_disk_number: int) -> int:
    """将 Windows(0-based) 磁盘编号转换为 Ghost(1-based) 磁盘编号。"""
    if not isinstance(windows_disk_number, int) or windows_disk_number < 0:
        raise ValueError(f"无效Windows磁盘编号: {windows_disk_number}")
    return windows_disk_number + 1

class CustomArgumentParser(argparse.ArgumentParser):
    """
    重写 ArgumentParser，以便在发生错误或程序退出时，
    先提示用户按键，防止命令行窗口立即关闭。
    """
    
    def exit(self, status=0, message=None):
        """
        覆盖默认的 exit 方法。
        """
        if message:
            # 如果有错误或帮助信息，先打印出来
            self._print_message(message, sys.stderr)
        
        # 🌟 关键修改：在退出前添加暂停 🌟
        print("\n" + "=" * 40)
        print("程序已停止。")
        # 确保暂停指令只在 Windows 控制台环境下有效，防止闪退。
        pause_if_interactive("请按 Enter 键退出...")
        print("=" * 40)
        
        # 调用系统内置的 sys.exit 来真正退出程序
        sys.exit(status)

    def error(self, message):
        """
        覆盖默认的 error 方法 (例如参数缺失或无效)。
        它会调用上面的 exit(2, message)。
        """
        self.exit(2, '%s: error: %s\n' % (self.prog, message))

def parse_arguments():
    parser = CustomArgumentParser(
        description="磁盘信息查询工具",
        epilog="示例: python main.py --disk 3 或 python main.py -d 5 --json config.json"
    )
    
    # 添加磁盘编号参数
    parser.add_argument(
        '--disk', '-d',
        type=int,
        required=True,
        choices=[1, 2, 3, 4, 5, 6],
        help='磁盘编号 (1-6)，用于指定要操作的磁盘',
        metavar='DISK_NUMBER'
    )
    
    parser.add_argument(
        '--json', '-j',
        type=str,
        required=True,
        help='JSON配置文件路径',
        metavar='FILE_PATH'
    )
    
    return parser.parse_args()


def setup_json_config(args: argparse.Namespace) -> Dict[str, Any]:
    """设置并读取JSON配置文件"""
    if args.json:
        config_data = read_json_config(args.json)
        if config_data is None:
            print("X JSON配置文件读取失败，程序退出。")
            pause_if_interactive("请按 Enter 键退出...")
            sys.exit(1)
        else:
            if config_data and 'description' in config_data:
                print(f"成功读取JSON配置文件: {config_data['description']}")
            return config_data
    else:
        print("未指定JSON配置文件，使用默认配置。")
        return {}


def validate_main_config(config_data: Dict[str, Any]) -> None:
    """对主流程关键配置做统一校验，失败时抛出 ValueError。"""
    required_int_fields = ["efi_size", "c_size"]
    required_str_fields = ["gho_exe", "win_gho", "bcd_exe"]

    for field in required_int_fields:
        value = config_data.get(field)
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"配置项 {field} 必须为正整数，当前值: {value}")

    for field in required_str_fields:
        value = config_data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"配置项 {field} 必须为非空字符串，当前值: {value}")

    excluded_disk_names = config_data.get("excluded_disk_names", [])
    if excluded_disk_names is not None and not isinstance(excluded_disk_names, list):
        raise ValueError("配置项 excluded_disk_names 必须为列表")


def validate_protected_disk(disk_number: int, config_data: Optional[dict] = None) -> bool:
    """验证用户输入的disk_number是否为保护硬盘"""
    if not isinstance(disk_number, int) or disk_number < 1 or disk_number > 6:
        raise ValueError(f"磁盘编号必须在1-6范围内")
    
    if config_data is None:
        return True
    
    excluded_disk_names = config_data.get('excluded_disk_names', [])
    if not isinstance(excluded_disk_names, list):
        raise ValueError("excluded_disk_names必须是列表格式")
    
    try:
        disk_manager = get_disk_manager()
        disk_info = disk_manager.get_disk_by_index(disk_number)
        
        if disk_info is None:
            raise RuntimeError(f"未找到磁盘 {disk_number}")
        
        if disk_info.name in excluded_disk_names:
            print(f"[WARN] 磁盘 {disk_number} ({disk_info.name}) 是保护硬盘，无法操作")
            return False
        return True
            
    except Exception as e:
        raise RuntimeError(f"获取磁盘 {disk_number} 信息失败: {e}")



def all_disk_partitions(disk_number, efi_size, c_size, software_path=None):
    """初始化磁盘分区"""
    efi_letter = get_disk_letter(disk_number, 'efi')
    c_letter = get_disk_letter(disk_number, 'c')
    d_letter = get_disk_letter(disk_number, 'd')
    e_letter = get_disk_letter(disk_number, 'e')
    
    disk_manager = get_disk_manager()
    disk_info = disk_manager.get_disk_by_index(disk_number)
    if disk_info is None:
        print(f"[ERROR] 未找到磁盘 {disk_number} 的信息")
        return False
    disk_size_gb = parse_capacity_gb(disk_info.capacity)


    # 顺序执行：第一步
    if not initialize_disk_to_gpt(disk_number, efi_size, efi_letter):
        return False
    
    # 顺序执行：第二步
    if not initialize_disk_to_partitioning_C(disk_number, c_size, c_letter):
        return False
    
    # 顺序执行：第三步
    # if not initialize_disk_to_partitioning_D(disk_number, d_letter, efi_size, c_size):
    #     return False
    if disk_size_gb >= 600:
        if not initialize_disk_to_partitioning_D(disk_number, d_letter, efi_size, c_size):
            return False
    
    # 顺序执行：第四步
    if not initialize_disk_to_partitioning_E(disk_number, e_letter):
        return False
    
    # 顺序执行：第五步 - 复制软件文件夹（如果提供了路径）
    if software_path:
        copy_result = copy_software_folder(disk_number, software_path)
        if not isinstance(copy_result, dict):
            print(f"[ERROR] 软件复制返回格式异常: {copy_result}")
            return False
        if not copy_result.get("success", False):
            print(f"[ERROR] 软件复制失败: {copy_result.get('message')}")
            return False
    
    return True



if __name__ == "__main__":
    
    args = parse_arguments()
    disk_number = args.disk
    json_data = setup_json_config(args)
    
    # 检查JSON数据是否有效
    if not json_data:
        print("X JSON配置数据无效，程序终止。")
        pause_if_interactive("请按 Enter 键退出...")
        sys.exit(1)

    try:
        validate_main_config(json_data)
    except ValueError as e:
        print(f"[ERROR] 配置校验失败: {e}")
        pause_if_interactive("请按 Enter 键退出...")
        sys.exit(1)
    
    efi_size = json_data.get("efi_size")
    c_size = json_data.get("c_size")
    c_size = resolve_c_size(disk_number, c_size, json_data)
    gho_exe = json_data.get("gho_exe")
    win_gho = json_data.get("win_gho")
    bcd_exe = json_data.get("bcd_exe")
    efi_letter = get_disk_letter(disk_number, 'efi')
    c_letter = get_disk_letter(disk_number, 'c')
    software_file = json_data.get("software_file")
    # 验证磁盘是否可操作
    if validate_protected_disk(disk_number, json_data):
        print("[OK] 磁盘验证通过")
        
        # 执行磁盘分区
        if all_disk_partitions(disk_number, efi_size, c_size, software_file):
            print("[OK] 磁盘分区完成")
            time.sleep(5)
            
            # 执行Ghost镜像恢复
            ghost_ok = False
            try:
                ghost_disk_number = windows_disk_to_ghost_disk(disk_number)
                print(f"[INFO] 磁盘编号转换: Windows={disk_number} -> Ghost={ghost_disk_number}")
                ghost_ok = call_ghost(ghost_disk_number, gho_exe, win_gho, c_letter)
            except Exception as e:
                print(f"[ERROR] Ghost镜像恢复异常: {e}")

            if ghost_ok:
                print("[OK] Ghost镜像恢复完成")
                time.sleep(5)
                
                # 修复启动加载器
                if repair_boot_loader(bcd_exe, efi_letter, c_letter):
                    print("[OK] 启动加载器修复完成")
                    print("[OK] 所有操作成功完成!")
                else:
                    print("[ERROR] 启动加载器修复失败")
            else:
                print("[ERROR] Ghost镜像恢复失败")
        else:
            print("[ERROR] 磁盘分区失败")
    else:
        print("[ERROR] 磁盘验证失败，操作终止")


    pause_if_interactive("请按 Enter 键退出...")
