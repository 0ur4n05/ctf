import lief
from base64 import b64encode
from pwn import *

def sendpayload(content):
    pp = process("./run.sh")
    pp.recvuntil(b":")
    pp.sendline(content)
    pp.interactive()

binary = lief.parse("/bin/ls")
header = binary.header
header.file_type = lief._lief.ELF.E_TYPE.EXECUTABLE


log.info("building the binary")
builder = lief.ELF.Builder(binary)
builder.build()

log.info("writing the binary")
x = bytes(builder.get_build())

file  = open("filex", "rb")
content = b64encode(file.read())
file.close()
sendpayload(content)


