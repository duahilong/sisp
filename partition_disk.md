## 执行流程
 - 判断传入参数(-disk_number, -efi_size, -primary_size, -first_letter, -second_letter, -efi_letter) 
 - 验证磁盘可信息.
 - 执行diskpart命令前验证管理员权限.
 - 执行初始化GPT分区表,( 选择硬盘- 清除磁盘- 转换为GPT格式-判断MSR分区,如果存在删除MSR分区,)
 - 验证初始化GPT 成功,如果失败,返回False.
 - 执行分区操作, ( 选择硬盘- 创建分区1(150G)- 格式化- 分配盘符, 选择硬盘- 创建分区2,3(平均分配)- 格式化- 分配盘符, 选择硬盘- 创建EFI分区(200M)- 格式化- 分配盘符)
 - 验证分区操作成功,如果失败,返回False.

## 设计细节规范
 - 验证传入参数
    - disk_number: 必须是整数,且大于等于0.
    - efi_size: 必须是整数,且大于0.
    - c_size: 必须是整数,且大于0.
    - c_letter: 必须是单个字母,且为大写.
    - d_letter: 必须是单个字母,且为大写.
    - efi_letter: 必须是单个字母,且为大写.
    - 验证传入参数是否重复
    - 验证传入参数是否合法
    - 验证传入c_size参数是否超出disk_number磁盘容量
    - 验证传入参数是否为大写字母
    - 验证传入所有letter参数不能包含 C,D 这两个字母
    - 验证传入参数是否和现有分区盘符冲突
    - 验证成功返回true,否则返回false 并抛出错误异常

   - 使用系统工具 diskpart(调用工具前检查管理员权限) 初始化GPT分区表 (disk_number efi_size efi_letter)
    - 根据传入参数 disk_number 选择硬盘
    - 清除磁盘
    - 转换为GPT格式
    - 判断MSR分区,如果存在删除MSR分区
    
 - 测试git 更改