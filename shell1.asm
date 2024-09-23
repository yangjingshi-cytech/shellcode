section .data
    msg db 'Hello, World!', 0xA  ; 定义要输出的字符串，0xA 是换行符
    len equ $-msg                ; 计算字符串长度

section .text
    global _start

_start:
    ; 系统调用 write(stdout, msg, len)
    mov rax, 1                   ; 系统调用号：sys_write
    mov rdi, 1                   ; 文件描述符：stdout
    mov rsi, msg                 ; 要输出的字符串
    mov rdx, len                 ; 字符串长度
    syscall                      ; 调用系统中断

    ; 系统调用 exit(0)
    mov rax, 60                  ; 系统调用号：sys_exit
    xor rdi, rdi                 ; 返回值：0
    syscall                      ; 调用系统中断
