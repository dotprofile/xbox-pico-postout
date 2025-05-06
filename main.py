from machine import Pin
import time

# 7-segment map for hex digits (common anode, so 0 = ON)
HEX_MAP = [
    [0,0,0,0,0,0,1],  # 0
    [1,0,0,1,1,1,1],  # 1
    [0,0,1,0,0,1,0],  # 2
    [0,0,0,0,1,1,0],  # 3
    [1,0,0,1,1,0,0],  # 4
    [0,1,0,0,1,0,0],  # 5
    [0,1,0,0,0,0,0],  # 6
    [0,0,0,1,1,1,1],  # 7
    [0,0,0,0,0,0,0],  # 8
    [0,0,0,0,1,0,0],  # 9
    [0,0,0,1,0,0,0],  # A
    [1,1,0,0,0,0,0],  # B
    [0,1,1,0,0,0,1],  # C
    [1,0,0,0,0,1,0],  # D
    [0,1,1,0,0,0,0],  # E
    [0,1,1,1,0,0,0],  # F
]

# Input pins (from level shifter)
inputs = [Pin(i, Pin.IN) for i in range(8)]

# Output segment pins for two displays
seg1 = [Pin(i, Pin.OUT) for i in range(8, 15)]   # Left digit (high nibble)
seg2 = [Pin(i, Pin.OUT) for i in range(15, 22)]  # Right digit (low nibble)

def update_display(value):
    high = (value >> 4) & 0x0F
    low = value & 0x0F
    for i in range(7):
        seg1[i].value(HEX_MAP[high][i])
        seg2[i].value(HEX_MAP[low][i])

# Track last displayed value
last_val = -1

while True:
    val = 0
    for i in range(8):
        if inputs[i].value():
            val |= (1 << i)
    if val != last_val:
        update_display(val)
        last_val = val
    time.sleep(0.01)
