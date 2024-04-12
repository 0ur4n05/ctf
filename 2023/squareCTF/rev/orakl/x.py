import time
from pwn import *

flag = "f"
new_time = time.time()
 
while (True):
	log.warn("establishing a connection")
	pp = remote("184.72.87.9", 8006)
	log.warn("connected")
	pp.recv()
	pp.sendline(flag.encode("utf-8"))
	pp.recv()
	offset = time.time() - new_time
	new_time = time.time()
	log.warn(f"fucking newtime {offset}")
	flag += chr(int(offset) + 10)
	print(f"fucking flag {flag}")
