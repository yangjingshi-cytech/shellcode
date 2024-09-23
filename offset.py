import struct

# 修改 ELF 文件中某个段的 p_flags，增加执行权限
def modify_elf_program_header(file_path, ph_offset):
    """
    修改 ELF 文件的程序头表中的 p_flags 字段，使指定段可执行。
    :param file_path: ELF 文件路径
    :param ph_offset: 要修改的程序头表项的文件偏移
    """
    with open(file_path, 'rb+') as fd:
        fd.seek(ph_offset + 4)  # 偏移 4 字节，跳过 p_type 字段
        p_flags = struct.unpack('<I', fd.read(4))[0]  # 读取 p_flags 字段
        print(f"原始 p_flags: {p_flags:#x}")

        # 修改 p_flags，增加可执行权限
        new_p_flags = p_flags | 0x1  # 增加执行权限
        fd.seek(ph_offset + 4)  # 回到 p_flags 字段位置
        fd.write(struct.pack('<I', new_p_flags))  # 写入新的 p_flags

        print(f"新的 p_flags: {new_p_flags:#x}")

# 使用例子
modify_elf_program_header('hello', 0x270)  # 假设程序头表的偏移是 0x200
