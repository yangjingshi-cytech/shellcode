import struct

# 读取ELF Header并解析信息
def parse_elf_header(elf_file):
    elf_file.seek(0)
    elf_header = elf_file.read(64)
    
    e_ident = elf_header[:16]
    is_64bit = e_ident[4] == 2  # 如果第5个字节为2，则为64位ELF
    
    e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, \
    e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack('<HHIQQQIHHHHHH', elf_header[16:])
    
    return {
        'is_64bit': is_64bit,
        'e_phoff': e_phoff,
        'e_phnum': e_phnum,
        'e_phentsize': e_phentsize
    }

# 解析Program Headers，找到PT_NOTE和PT_LOAD
def find_segments(elf_file, elf_header):
    pt_note = None
    pt_load = None
    
    elf_file.seek(elf_header['e_phoff'])
    for i in range(elf_header['e_phnum']):
        program_header = elf_file.read(elf_header['e_phentsize'])
        
        if elf_header['is_64bit']:
            # 64位ELF的程序头大小为56字节
            p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack('<IIQQQQII', program_header)
        else:
            # 32位ELF的程序头大小为32字节
            p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack('<IIIIIIII', program_header)
        
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

if __name__ == '__main__':
    main()
