backup_len = len
backup_eval = eval
backup_print = print
backup_input = input
backup_all = all
backup_ord = ord

# osu must be in the fucking input
def rescued_osu(input):
    return input.count('o') == 1 and input.count('s') == 1 and input.count('u') == 1

def caught_by_guards(input):
    # return '[' in input or ']' in input or '{' in input or '}' in input or not backup_all(0 <= backup_ord(c) <= 255 for c in input)
    return False
    # alright [] {} must not be in in the input


print(len)
globals()['__builtins__'].__dict__.clear()          # clearing the builtins

input = backup_input()                          # getting input
if caught_by_guards(input) or not rescued_osu(input):
    backup_print('[You failed to break the jail]')
else:
    backup_print(backup_eval(input,{},{}))
