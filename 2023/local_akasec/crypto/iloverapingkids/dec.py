from Crypto.Cipher import AES
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Util.Padding import pad


cipher = "db23ea10ecae48476bef1d4369ad323136628ac21de1239ba5a7320ac3b30c0368c4e03d774f72b20859804b3758b2f5"
iv = "266cb7d5d0efe0cdd9cf193a3a5b5ec3"

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

def decrypt(key, iv, ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(ciphertext)

def main():
    putput = open('output.txt', 'r')
    putputd = 0
    zebi = putput.readlines()
    for zeb in zebi:
        putputd += int(zeb)
    print(putput)
    while True : 
        key = long_to_bytes(do_lott())[:16]
        flag = decrypt(key, iv.decode("hex"), cipher.decode("hex"))
        if ("akasec" in flag ):
            print(flag)

