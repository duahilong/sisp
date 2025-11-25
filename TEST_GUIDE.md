# 手动测试 partition_disk.py 指南

## 测试脚本说明

我为你创建了两个测试脚本，分别适用于不同的测试需求：

### 1. test_partition_manual.py - 完整测试版本
功能齐全，包含参数验证、磁盘信息展示、操作确认等安全特性。

**使用方法：**
```bash
python test_partition_manual.py <磁盘编号> <EFI大小> <主分区大小> <盘符1> <盘符2> <EFI盘符>
```

**示例：**
```bash
# 测试磁盘2，EFI分区200MB，主分区50GB，盘符分别为L、K、J
python test_partition_manual.py 2 200 50000 L K J

# 测试磁盘2，EFI分区300MB，主分区约220GB，盘符分别为L、K、J  
python test_partition_manual.py 2 300 225290 L K J
```

**特点：**
- ✅ 完整的参数验证
- ✅ 显示目标磁盘信息（名称、容量）
- ✅ 显示主分区占磁盘容量的百分比
- ✅ 操作前确认提示（防止误操作）
- ✅ 详细的错误提示信息

### 2. test_partition_simple.py - 简化测试版本
快速测试，直接执行，适合开发调试。

**使用方法：**
```bash
python test_partition_simple.py <磁盘编号> <EFI大小> <主分区大小> <盘符1> <盘符2> <EFI盘符>
```

**示例：**
```bash
# 快速测试，无确认步骤
python test_partition_simple.py 2 200 50000 L K J
```

**特点：**
- ⚡ 快速执行，无确认步骤
- ⚡ 简洁的输出信息
- ⚡ 适合频繁测试使用

## 参数说明

| 参数 | 说明 | 建议值 |
|------|------|--------|
| 磁盘编号 | 目标磁盘号 | 0, 1, 2... |
| EFI大小 | EFI分区大小(MB) | 200-500MB |
| 主分区大小 | 主分区大小(MB) | 必须小于磁盘总容量 |
| 盘符1 | 第一个分区盘符 | A-Z |
| 盘符2 | 第二个分区盘符 | A-Z |
| EFI盘符 | EFI分区盘符 | A-Z |

## 测试建议

### 安全测试流程
1. **先使用完整版本**了解参数是否合理
2. **检查磁盘信息**确认目标磁盘正确
3. **使用简化版本**进行频繁测试

### 常见测试场景
```bash
# 场景1：标准分区
python test_partition_manual.py 2 200 50000 L K J

# 场景2：大EFI分区
python test_partition_manual.py 2 500 100000 M N O

# 场景3：小主分区（测试边界条件）
python test_partition_manual.py 2 200 1000 P Q R
```

## 注意事项

⚠️ **重要警告：**
- 需要**管理员权限**运行（否则会出现权限错误）
- 操作会**清除磁盘所有数据**
- 确保选择**正确的磁盘编号**
- 主分区大小**不能超过磁盘总容量**
- 所有盘符**必须不同**

## 错误处理

如果测试失败，脚本会显示具体的错误原因：
- 参数格式错误
- 磁盘不存在
- 容量不足
- 盘符重复
- 权限问题
- 超时问题

## 管理员权限运行方法

1. **方法一：右键运行**
   - 右键点击"命令提示符" → "以管理员身份运行"
   - 切换到脚本目录：`cd D:\Sisp`
   - 执行测试命令

2. **方法二：PowerShell**
   ```powershell
   # 以管理员身份打开PowerShell
   Start-Process powershell -Verb RunAs
   cd D:\Sisp
   python test_partition_manual.py 2 200 50000 L K J
   ```

祝你测试顺利！ 🚀