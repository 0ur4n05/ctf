from pwn import *
import sys
from ctypes import CDLL
import math

####### NOT SOLVED 

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "warn"        # 'DEBUG', 'ERROR', 'INFO', 'NOTSET', 'WARN', 'WARNING'
binary = "./super-sick-tank-game"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b main
'''
libc = CDLL("libc.so.6")
now = int(math.floor(time.time()))
libc.srand(now)

def guess_player():
    enemy_placement = (libc.rand() % 112) - 1
    # keep in mind, it returns the index
    return (enemy_placement)

def get_tragectoir(enemy_pos):
    for x in range(0, 90):
        for i in range(0, 33):
            rad_angle = (x * 3.141592653589793) / 180.0
            cos_angle = math.cos(rad_angle);
            sin_angle = math.sin(rad_angle);
            power = cos_angle * i * ((sin_angle * i + sin_angle * i) / 9.81);
            if (int(power) == enemy_pos):
                return (int(i), x)

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

def exploit(pp):
    #offset = 
    log.info("binary loaded")
    for i in range(0,3):
        print(pp.recvuntil(b"power:")).decode("utf-8"))
        enemypos = guess_player()
        log.warn(f"player pos {enemypos}")
        log.warn("sending the power")
        trag = get_tragectoir(enemypos)
        log.warn(f"power {trag[0]} angle {trag[1]}")
        pp.sendline(str(trag[0]).encode("utf-8"))
        pp.recvuntil(b":")
        log.warn("sending the angle")
        pp.sendline(str(trag[1]).encode("utf-8"))
        log.warn("pew!!!!")
        pp.recvuntil(b"ready!")
        pp.sendline(b"pew!")

    #   pp.recv()
    # pp.sendline(b"33")
    # pp.recv()
    # pp.sendline(b"45")
    # pp.recv()
    # pp.sendline(b"pew!")
    # zebi = pp.recv()
    # print(zebi)
    # print(zebi.decode("utf-8"))
    # payload = flat(
    #
    #         )
    pp.interactive()

elf = context.binary = ELF(binary)
pp = init()
exploit(pp)
