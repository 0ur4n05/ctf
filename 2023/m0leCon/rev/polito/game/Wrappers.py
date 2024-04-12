import ctypes

class PolitoWrapper(ctypes.Structure):
    _fields_ = [
        ('game', ctypes.c_void_p),
        ('market', ctypes.c_void_p),
        ('earned_money', ctypes.c_ulong),
    ]

class GameWrapper(ctypes.Structure):
    _fields_ = [
        ('lives', ctypes.c_int),
        ('money', ctypes.c_ulong),
    ]


class MarketElementWrapper(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('desc', ctypes.c_char_p),
        ('price', ctypes.c_ulong),
        ('bought', ctypes.c_bool)
    ]


class MarketWrapper(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_int),
        ('elements', 7*(MarketElementWrapper)),
    ]
    