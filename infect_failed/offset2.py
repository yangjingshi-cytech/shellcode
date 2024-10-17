import struct

# 修改 ELF 文件中 PT_NOTE 段的 p_flags，增加执行权限
def modify_ptnote_permissions(fd, ph_offset):
    """
    修改 ELF 文件的程序头表中的 PT_NOTE 段的 p_flags 字段，使其可执行。
    :param fd: 文件描述符
    :param ph_offset: PT_NOTE 段的程序头表项的偏移位置
    """
    fd.seek(ph_offset + 4)  # 偏移 4 字节，跳过 p_type 字段
    p_flags = struct.unpack('<I', fd.read(4))[0]  # 读取当前的 p_flags 字段
    print(f"原始 p_flags: {p_flags:#x}")

    # 增加执行权限 (0x1 表示可执行权限)
    new_p_flags = p_flags | 0x1  # 为段增加可执行权限
    fd.seek(ph_offset + 4)  # 移动回 p_flags 字段位置
    fd.write(struct.pack('<I', new_p_flags))  # 写入新的 p_flags

    print(f"新的 p_flags: {new_p_flags:#x}")

# 使用这个函数来修改 ELF 文件的 PT_NOTE 段
def infect_elf(file_path):
    with open(file_path, 'rb+') as fd:
        ph_offset = 0x1c8  # PT_NOTE 段的程序头表偏移

        # 修改 PT_NOTE 段的权限为可执行
        modify_ptnote_permissions(fd, ph_offset)

# 使用例子
infect_elf('hello')
