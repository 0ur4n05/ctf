from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime
import os
import random

MAX = 2**4096 # this is N
TO_GUESS = random.randint(1, MAX) #guess this.
print(TO_GUESS)
FLAG = b'AKASEC{d3bug_fl4g}'
IV = os.urandom(16)

def encrypt_flag():
    key = long_to_bytes(TO_GUESS)[:16]
    cipher = AES.new(key, AES.MODE_CBC, IV)
    ciphertext = cipher.encrypt(pad(FLAG, block_size=16))
    return ciphertext

def shuffle_list(s):
    random.shuffle(s)
    return s

def perform_magic(num, n):
    final_list = []
    for i in range(4):
        final_list.append(random.randint(0, num))
    final_list.append(n % num)
    print(f"fucking some shit (tog{n} % pr{num}) ==> {n % num}\n")
    return shuffle_list(final_list)

HEADER = r"""#####################################################################
#                                                                   #
#                                                                   #
#                                                                   #
#                       ULTIMATE GUESSER                            #
#                                                                   #
#                                                                   #
#                                                                   #
#####################################################################"""

print(HEADER)
print(">> YOU CONTROL NOTHING. ALL YOU HAVE TO DO IS TO GUESS :) <<")

encrypt_flag = encrypt_flag()
p = [getPrime(256) for i in range(40)]
s = []

for prime_num in p:
    tab = perform_magic(prime_num, TO_GUESS)
    s.append(tab)

with open("./output.txt", "w") as f:
    f.write(f'>> Encrypted Flag : {encrypt_flag.hex()}\n')
    f.write(f'>> IV is : {IV.hex()}\n')
    f.write(f'>> P is : {p}\n')
    f.write(f'>> Sn is : {s}')
# uwu
