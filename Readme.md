# Sisp - System Installation Script Project

Sisp 是一个面向 Windows 装机场景的自动化部署工具。项目通过统一配置和固定流程，自动完成磁盘分区、系统镜像恢复、引导修复以及软件目录复制，适用于批量装机和标准化交付。

## 主要功能

- 自动读取并展示本机磁盘信息。
- 按磁盘编号执行 GPT 初始化与分区流程（EFI/C/D/E）。
- 调用 Ghost 镜像恢复系统分区。
- 调用 bcdboot 修复 UEFI 启动项。
- 将预置软件目录复制到目标磁盘，并同步文件与文件夹属性。
- 通过 `excluded_disk_names` 防止误操作受保护磁盘。

## 技术栈与依赖

- 语言：Python 3
- 系统命令：DiskPart、Ghost、bcdboot
- Python 依赖：`wmi`、`tabulate`
- 打包工具：PyInstaller

## 目录结构

```text
sisp/
├── main.py                        # 主入口：展示磁盘、选择目标、调度执行
├── main_logic_processing.py       # 核心执行流程（分区->Ghost->引导修复->复制）
├── disk_info.py                   # 磁盘信息读取（WMI + PowerShell）
├── partition_disk.py              # DiskPart 分区逻辑
├── call_ghost.py                  # Ghost 调用与系统目录验证
├── call_bcdboot.py                # bcdboot 调用与 EFI 校验
├── call_copy.py                   # 软件目录复制与属性同步
├── common_functions.py            # 公共函数（配置读取、盘符映射等）
├── get_user_disknumber.py         # 用户输入与磁盘编号解析
├── json/
│   └── win11.json                 # 示例配置文件
├── sw/
│   ├── ghost64.exe                # Ghost 可执行文件
│   └── bcdboot.exe                # bcdboot 可执行文件
├── img/
│   └── test.GHO                   # 示例镜像
├── tests/                         # 全部测试脚本
│   ├── run_tests.py               # 测试入口
│   └── test_*.py                  # 单元测试与模块测试
├── main.spec                      # main.exe 打包配置
└── main_logic_processing.spec     # main_logic_processing.exe 打包配置
```

## 配置说明

主要配置文件位于 `json/win11.json`，关键字段包括：

- `description`：任务描述
- `efi_size`：EFI 分区大小（MB）
- `c_size`：C 分区大小（MB）。例如 `153600` 表示 150GB。
- `enable_dynamic_c_size`：是否按磁盘容量动态覆盖 `c_size`（`true`/`false`）
  - `< 600GB` -> `c_size = 153600`（150GB）
  - `>= 600GB 且 < 1200GB` -> `c_size = 204800`（200GB）
  - `>= 1200GB` -> `c_size = 307200`（300GB）
- `gho_exe`：Ghost 程序路径
- `win_gho`：系统镜像路径
- `bcd_exe`：bcdboot 程序路径
- `software_file`：待复制软件目录路径
- `main_logic`：核心执行程序路径
- `excluded_disk_names`：受保护磁盘名称列表

路径建议使用“相对路径（相对项目根目录或配置文件目录）”，避免写死为某台机器上的绝对路径（例如 `D:\sisp\...`）。

## 使用方式

### 1) 开发模式运行

```bash
python main.py --json json/win11.json
```

主程序会显示磁盘信息，并根据输入磁盘编号调用核心流程。

### 2) 直接运行核心流程

```bash
python main_logic_processing.py -d 1 -j json/win11.json
```

### 3) 运行测试

```bash
python tests/run_tests.py
```

Windows 下若出现中文乱码，优先使用：

```bat
run_tests.bat
```

说明：`py_compile` 仅用于 `.py` 文件，不要传入 `Readme.md` 等非 Python 文件。

## 打包 EXE

```bash
python -m PyInstaller --clean main.spec
python -m PyInstaller --clean main_logic_processing.spec
```

输出目录：`dist/`

- `dist/main.exe`
- `dist/main_logic_processing.exe`

## 流程概览

1. 读取 JSON 配置。
2. 枚举磁盘并选择目标磁盘编号。
3. 校验是否命中受保护磁盘。
4. 执行分区：GPT -> EFI -> C -> (可选 D) -> E。
5. 调用 Ghost 恢复系统镜像。
6. 调用 bcdboot 修复 UEFI 启动。
7. 复制软件目录并同步属性。

## 硬盘相关改动总结

- 新增 `enable_dynamic_c_size` 配置开关，控制是否按目标磁盘容量动态覆盖 `c_size`。
- 动态规则已实现并接入主流程：
  - `< 600GB` -> `c_size = 153600`（150GB）
  - `>= 600GB 且 < 1200GB` -> `c_size = 204800`（200GB）
  - `>= 1200GB` -> `c_size = 307200`（300GB）
- 开关关闭时保持原行为，继续使用 JSON 中固定 `c_size`，确保向后兼容。
- 分区流程当前为：`GPT(含EFI创建) -> C -> (容量>=600GB 时创建 D) -> E`，任一步失败即中断。
- 软件复制逻辑已增强为同步文件和文件夹的全部 Windows 属性（不仅隐藏属性）。
- 测试体系新增两类专项测试：
  - 动态 C 分区测试：`tests/test_dynamic_c_size.py`
  - 分区流程测试（含严格调用顺序断言）：`tests/test_partition_workflow.py`

## 注意事项

- 请以管理员权限运行。
- 项目会执行真实磁盘与引导操作，请务必先确认目标磁盘编号。
- 在生产环境使用前，建议先在测试机验证配置与流程。
- 若双击 `main.exe` 直接退出，通常是缺少 `--json` 参数；请通过命令行附带参数运行。
- 打包后的 EXE 会内置 `json/win11.json` 与 `Readme.md`，但 `sw/`（ghost、bcdboot）、`img/`（镜像）和 `software_file` 目录仍需按配置在目标机器提供。
