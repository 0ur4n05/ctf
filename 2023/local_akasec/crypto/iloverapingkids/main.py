import os
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
import random
import os

#lottery system.

def do_lott():
    total_lottery = 0
    
    # fucking range shit
    for i in range(1000):
        # getting rangom getrandbits
        num = random.getrandbits(256)
        # well we just try this shit
        if i <= 900:
            print(f">> We got a new number {num} !!!!!")
        total_lottery += num
    
    return total_lottery

FLAG = b'AKASEC{d3bug_fl4g}'
iv = os.urandom(16)
key = long_to_bytes(do_lott())[:16]

cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(FLAG, block_size=16))
print(f'>> IV is {iv.hex()}')
print(f'>> Ciphertext is {ciphertext.hex()}')
