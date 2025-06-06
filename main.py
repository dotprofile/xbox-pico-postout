from machine import Pin, UART
import time

# UART setup (TX only on GPIO29 using UART1)
uart = UART(0, baudrate=115200, tx=Pin(28))	
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

# post message dictionary taken from https://xenonlibrary.com/wiki/Post_Codes 

POST_MESSAGES = {
    0x10: "0x10\tBEGIN\t1BL entry point",
    0x11: "0x11\tFSB_CONFIG_PHY_CONTROL\tFSB function 1\tFSB fail",
    0x12: "0x12\tFSB_CONFIG_RX_STATE\tFSB function 2\tFSB fail",
    0x13: "0x13\tFSB_CONFIG_TX_STATE\tFSB function 3\tFSB fail",
    0x14: "0x14\tFSB_CONFIG_TX_CREDITS\tFSB function 4\tFSB fail",
    0x15: "0x15\tFETCH_OFFSET\tFetch 2BL offset from flash\tGPU, SB, Nand",
    0x16: "0x16\tFETCH_HEADER\tFetch 2BL header from flash",
    0x17: "0x17\tVERIFY_HEADER\tVerify 2BL header\tBad 2BL header",
    0x18: "0x18\tFETCH_CONTENTS\tCopy 2BL to SRAM\tBad 2BL image",
    0x19: "0x19\tHMACSHA_COMPUTE\tCompute 2BL HMAC hash",
    0x1A: "0x1A\tRC4_INITIALIZE\tInitialize 2BL RC4",
    0x1B: "0x1B\tRC4_DECRYPT\tDecrypt 2BL\tBad 2BL image",
    0x1C: "0x1C\tSHA_COMPUTE\tCompute 2BL hash",
    0x1D: "0x1D\tSIG_VERIFY\tVerify 2BL hash\tBad 2BL signature",
    0x1E: "0x1E\tBRANCH\tBranch to 2BL",
    0x20: "0x20\t2BL entry point",
    0x21: "0x21\tINIT_SECOTP\tInitialize Secure ROM and eFUSEs",
    0x22: "0x22\tINIT_SECENG\tInitialize security engine",
    0x23: "0x23\tINIT_SYSRAM\tInitialize system RAM\tBad GPU, RAM",
    0x24: "0x24\tVERIFY_OFFSET_3BL\tVerify 3BL offset from flash\tBad 3BL image",
    0x25: "0x25\tLOCATE_3BL\tLocate 3BL in flash\tBad nand image",
    0x26: "0x26\tFETCH_HEADER_3BL\tFetch 3BL header from flash",
    0x27: "0x27\tVERIFY_HEADER_3BL\tVerify 3BL header\tBad 3BL header",
    0x28: "0x28\tFETCH_CONTENTS\tCopy 3BL to SRAM\tBad 3BL image",
    0x29: "0x29\tHMACSHA_COMPUTE_3BL\tCompute 3BL hash",
    0x2A: "0x2A\tRC4_INITIALIZE_3BL\tInitialize 3BL RC4",
    0x2B: "0x2B\tRC4_DECRYPT_3BL\tDecrypt 3BL\tBad 3BL image",
    0x2C: "0x2C\tSHA_COMPUTE_3BL\tCompute 3BL hash",
    0x2D: "0x2D\tSHA_VERIFY_3BL\tVerify 3BL hash\tBad 3BL signature",
    0x2E: "0x2E\tHWINIT\tHardware initialization\tBad GPU, RAM",
    0x2F: "0x2F\tRELOCATE\tRelocate to system RAM",
    0x30: "0x30\tVERIFY_OFFSET_4BL\tVerify 4BL offset from flash\tBad nand image",
    0x31: "0x31\tFETCH_HEADER_4BL\tFetch 4BL header from flash",
    0x32: "0x32\tVERIFY_HEADER_4BL\tVerify 4BL header\tBad 4BL header",
    0x33: "0x33\tFETCH_CONTENTS_4BL\tCopy 4BL to RAM\tBad 4BL image",
    0x34: "0x34\tHMACSHA_COMPUTE_4BL\tCompute 4BL hash",
    0x35: "0x35\tRC4_INITIALIZE_4BL\tInitialize 4BL RC4",
    0x36: "0x36\tRC4_DECRYPT_4BL\tDecrypt 4BL\tBad 4BL image",
    0x37: "0x37\tSHA_COMPUTE_4BL\tCompute 4BL hash",
    0x38: "0x38\tSIG_VERIFY_4BL\tVerify 4BL hash\tBad 4BL signature",
    0x39: "0x39\tSHA_VERIFY_4BL\tVerify 4BL hash\tBad 4BL signature",
    0x3A: "0x3A\tBRANCH\tBranch to 4BL",
    0x3B: "0x3B\tPCI_INIT\tInitialize PCI",
    0x40: "0x40\t4BL entry point",
    0x41: "0x41\tVERIFY_OFFSET\tVerify 5BL offset in flash\tBad 5BL image",
    0x42: "0x42\tFETCH_HEADER\tFetch 5BL header from flash",
    0x43: "0x43\tVERIFY_HEADER\tVerify 5BL header\tBad 5BL header",
    0x44: "0x44\tFETCH_CONTENTS\tCopy 5BL to RAM\tBad 5BL image",
    0x45: "0x45\tHMACSHA_COMPUTE\tCompute 5BL hash",
    0x46: "0x46\tRC4_INITIALIZE\tInitialize 5BL RC4",
    0x47: "0x47\tRC4_DECRYPT\tDecrypt 5BL\tBad 5BL image",
    0x48: "0x48\tSHA_COMPUTE\tCompute 5BL hash",
    0x49: "0x49\tSHA_VERIFY\tVerify 5BL hash\tBad 5BL signature",
    0x4A: "0x4A\tLOAD_6BL\tLoad 6BL",
    0x4B: "0x4B\tLZX_EXPAND\tExpand 6BL",
    0x4C: "0x4C\tSWEEP_CACHES\tClear L1 and L2 cache",
    0x4D: "0x4D\tDECODE_FUSES\tDecode fuses",
    0x4E: "0x4E\tFETCH_OFFSET_6BL\tFetch 6BL offset from flash",
    0x4F: "0x4F\tVERIFY_OFFSET_6BL\tVerify 6BL offset\tBad 6BL offset",
    0x50: "0x50\tLOAD_UPDATE_1\tLoad Patch Slot 1\tBad patch slot 1 image",
    0x51: "0x51\tLOAD_UPDATE_2\tLoad Patch Slot 2\tBad patch slot 2 image",
    0x52: "0x52\tBRANCH\tBranch to hypervisor",
    0x53: "0x53\tDECRYPT_VERIFY_HV_CERT\tDecrypt and verify HV cert\tBad HV cert",
    0x58: "0x58\tINIT_HYPERVISOR\tInitialize hypervisor",
    0x59: "0x59\tINIT_SOC_MMIO\tInitialize SoC MMIO\tBad CPU",
    0x5A: "0x5A\tINIT_XEX_TRAINING\tInitialize XEX training",
    0x5B: "0x5B\tINIT_KEYRING\tInitialize key ring",
    0x5C: "0x5C\tINIT_KEYS\tInitialize keys",
    0x5D: "0x5D\tINIT_SOC_INT\tInitialize SoC interrupts",
    0x5E: "0x5E\tINIT_SOC_INT_COMPLETE\tHypervisor initialization complete",
    0x60: "0x60\tINIT_KERNEL\tInitialize kernel",
    0x61: "0x61\tINITIAL_HAL_PHASE_0\tInitialize HAL phase 0",
    0x62: "0x62\tINIT_PROCESS_OBJECTS\tInitialize process objects",
    0x63: "0x63\tINIT_KERNEL_DEBUGGER\tInitialize kernel debugger",
    0x64: "0x64\tINIT_MEMORY_MANAGER\tInitialize memory manager",
    0x65: "0x65\tINIT_STACKS\tInitialize stacks",
    0x66: "0x66\tINIT_OBJECT_SYSTEM\tInitialize object system",
    0x67: "0x67\tINIT_PHASE1_THREAD\tInitialize phase 1 thread",
    0x68: "0x68\tINIT_PROCESSORS\tInitialize processors",
    0x69: "0x69\tINIT_KEYVAULT\tInitialize keyvault\tBad keyvault",
    0x6A: "0x6A\tINIT_HAL_PHASE_1\tInitialize HAL phase 1",
    0x6B: "0x6B\tINIT_SFC_DRIVER\tInitialize flash controller",
    0x6C: "0x6C\tINIT_SECURITY\tInitialize security",
    0x6D: "0x6D\tINIT_KEY_EX_VAULT\tInitialize extended keyvault\tBad keyvault",
    0x6E: "0x6E\tINIT_SETTINGS\tInitialize settings",
    0x6F: "0x6F\tINIT_POWER_MODE\tInitialize power mode",
    0x70: "0x70\tINIT_VIDEO_DRIVER\tInitialize video driver",
    0x71: "0x71\tINIT_AUDIO_DRIVER\tInitialize audio driver",
    0x72: "0x72\tINIT_BOOT_ANIMATION\tInitialize bootanim.xex, XMADecoder, XAudioRender\tMissing/corrupted bootanim.xex",
    0x73: "0x73\tINIT_SATA_DRIVER\tInitialize SATA driver",
    0x74: "0x74\tINIT_SHADOWBOOT\tInitialize shadowboot",
    0x75: "0x75\tINIT_DUMP_SYSTEM\tInitialize dump system",
    0x76: "0x76\tINIT_SYSTEM_ROOT\tInitialize system root",
    0x77: "0x77\tINIT_OTHER_DRIVERS\tInitialize other drivers",
    0x78: "0x78\tINIT_STFS_DRIVER\tInitialize STFS driver",
    0x79: "0x79\tLOAD_XAM\tInitialize xam.xex\tMissing/corrupted xam.xex",
    0xFF: "0xFF\tFATAL\tPanic - Hypervisor Error",
}


# Setup input pins (reversed order: GPIO7 is MSB)
inputs = [Pin(i, Pin.IN) for i in range(8)]

# Segment output pins for two digits
seg1 = [Pin(i, Pin.OUT) for i in range(8, 15)]    # Display 1
seg2 = [Pin(i, Pin.OUT) for i in range(15, 22)]   # Display 2

def update_display(value):
    high = (value >> 4) & 0x0F
    low = value & 0x0F
    for i in range(7):
        seg1[i].value(HEX_MAP[high][i])
        seg2[i].value(HEX_MAP[low][i])

last_val = -1

while True:
    val = 0
    for i in range(8):
        if inputs[7 - i].value():  # Reverse bit order cus I dumbo 
            val |= (1 << i)

    if val != last_val:
        last_val = val
        if val != 0:  # Suppress 0x00
            update_display(val)
            msg = POST_MESSAGES.get(val, "0x{:02X}\tUnknown code".format(val))
            uart.write(msg + "\r\n")

    time.sleep(0.005)
