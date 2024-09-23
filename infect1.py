import struct

def inject_shellcode(elf_file, note_offset, load_offset, shellcode):
    # 读取原始 ELF 文件内容
    with open(elf_file, 'rb') as f:
        elf_data = f.read()

    # 构造跳转指令（jmp load_address）
    load_address = load_offset  # 假设 load_offset 已是虚拟地址
    note_address = note_offset  # 假设 note_offset 已是虚拟地址
    jump_offset = load_address - (note_address + 5)  # 5 是 jmp 指令长度
    jmp_instr = b'\xE9' + struct.pack('<I', jump_offset & 0xFFFFFFFF)

    # 在 NOTE 段末尾注入 jmp 指令
    patched_elf_data = elf_data[:note_offset] + jmp_instr + elf_data[note_offset+len(jmp_instr):]

    # 在 LOAD 段写入 shellcode
    patched_elf_data = patched_elf_data[:load_offset] + shellcode + patched_elf_data[load_offset+len(shellcode):]

    # 保存修改后的 ELF 文件
    with open('patched_' + elf_file, 'wb') as f:
        f.write(patched_elf_data)

# Shellcode: 输出 "Goodbye, World!"
shellcode = b"\x48\xc7\xc0\x01\x00\x00\x00\x48\xc7\xc7\x01\x00\x00\x00\x48\xc7\xc6\x00\x60\x60\x00\x48\xc7\xc2\x0d\x00\x00\x00\x0f\x05\x48\xc7\xc0\x3c\x00\x00\x00\x48\x31\xff\x0f\x05"

# 假设我们从 readelf 获得的偏移量如下：
note_offset = 0x0000000000000338  # 这是 NOTE 段的文件偏移地址
load_offset = 0x0000000000001000  # 这是 LOAD 段的文件偏移地址

# 注入 shellcode 到 hello 文件
inject_shellcode('hello', note_offset, load_offset, shellcode)
