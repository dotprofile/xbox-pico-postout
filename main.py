from machine import Pin, UART
import time

# UART setup (TX only on GPIO28 using UART0)
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
    0x10: "0x10\t\tBEGIN\t\t1BL entry point",
    0x11: "0x11\t\tFSB_CONFIG_PHY_CONTROL\t\tFSB function 1\t\tFSB fail",
    0x12: "0x12\t\tFSB_CONFIG_RX_STATE\t\tFSB function 2\t\tFSB fail",
    0x13: "0x13\t\tFSB_CONFIG_TX_STATE\t\tFSB function 3\t\tFSB fail",
    0x14: "0x14\t\tFSB_CONFIG_TX_CREDITS\t\tFSB function 4\t\tFSB fail",
    0x15: "0x15\t\tFETCH_OFFSET\t\tFetch 2BL offset from flash\t\tGPU, SB, Nand",
    0x16: "0x16\t\tFETCH_HEADER\t\tFetch 2BL header from flash",
    0x17: "0x17\t\tVERIFY_HEADER\t\tVerify 2BL header\t\tBad 2BL header",
    0x18: "0x18\t\tFETCH_CONTENTS\t\tCopy 2BL to SRAM\t\tBad 2BL image",
    0x19: "0x19\t\tHMACSHA_COMPUTE\t\tCompute 2BL HMAC hash",
    0x1A: "0x1A\t\tRC4_INITIALIZE\t\tInitialize 2BL RC4",
    0x1B: "0x1B\t\tRC4_DECRYPT\t\tDecrypt 2BL\t\tBad 2BL image",
    0x1C: "0x1C\t\tSHA_COMPUTE\t\tCompute 2BL hash",
    0x1D: "0x1D\t\tSIG_VERIFY\t\tVerify 2BL hash\t\tBad 2BL signature",
    0x1E: "0x1E\t\tBRANCH\t\tBranch to 2BL",
    0x20: "0x20\t\t2BL entry point",
    0x21: "0x21\t\tINIT_SECOTP\t\tInitialize Secure ROM and eFUSEs",
    0x22: "0x22\t\tINIT_SECENG\t\tInitialize security engine",
    0x23: "0x23\t\tINIT_SYSRAM\t\tInitialize system RAM\t\tBad GPU, RAM",
    0x24: "0x24\t\tVERIFY_OFFSET_3BL\t\tVerify 3BL offset from flash\t\tBad 3BL image",
    0x25: "0x25\t\tLOCATE_3BL\t\tLocate 3BL in flash\t\tBad nand image",
    0x26: "0x26\t\tFETCH_HEADER_3BL\t\tFetch 3BL header from flash",
    0x27: "0x27\t\tVERIFY_HEADER_3BL\t\tVerify 3BL header\t\tBad 3BL header",
    0x28: "0x28\t\tFETCH_CONTENTS\t\tCopy 3BL to SRAM\t\tBad 3BL image",
    0x29: "0x29\t\tHMACSHA_COMPUTE_3BL\t\tCompute 3BL hash",
    0x2A: "0x2A\t\tRC4_INITIALIZE_3BL\t\tInitialize 3BL RC4",
    0x2B: "0x2B\t\tRC4_DECRYPT_3BL\t\tDecrypt 3BL\t\tBad 3BL image",
    0x2C: "0x2C\t\tSHA_COMPUTE_3BL\t\tCompute 3BL hash",
    0x2D: "0x2D\t\tSHA_VERIFY_3BL\t\tVerify 3BL hash\t\tBad 3BL signature",
    0x2E: "0x2E\t\tHWINIT\t\tHardware initialization\t\tBad GPU, RAM",
    0x2F: "0x2F\t\tRELOCATE\t\tRelocate to system RAM",
    0x30: "0x30\t\tVERIFY_OFFSET_4BL\t\tVerify 4BL offset from flash\t\tBad nand image",
    0x31: "0x31\t\tFETCH_HEADER_4BL\t\tFetch 4BL header from flash",
    0x32: "0x32\t\tVERIFY_HEADER_4BL\t\tVerify 4BL header\t\tBad 4BL header",
    0x33: "0x33\t\tFETCH_CONTENTS_4BL\t\tCopy 4BL to RAM\t\tBad 4BL image",
    0x34: "0x34\t\tHMACSHA_COMPUTE_4BL\t\tCompute 4BL hash",
    0x35: "0x35\t\tRC4_INITIALIZE_4BL\t\tInitialize 4BL RC4",
    0x36: "0x36\t\tRC4_DECRYPT_4BL\t\tDecrypt 4BL\t\tBad 4BL image",
    0x37: "0x37\t\tSHA_COMPUTE_4BL\t\tCompute 4BL hash",
    0x38: "0x38\t\tSIG_VERIFY_4BL\t\tVerify 4BL hash\t\tBad 4BL signature",
    0x39: "0x39\t\tSHA_VERIFY_4BL\t\tVerify 4BL hash\t\tBad 4BL signature",
    0x3A: "0x3A\t\tBRANCH\t\tBranch to 4BL",
    0x3B: "0x3B\t\tPCI_INIT\t\tInitialize PCI",
    0x40: "0x40\t\t4BL entry point",
    0x41: "0x41\t\tVERIFY_OFFSET\t\tVerify 5BL offset in flash\t\tBad 5BL image",
    0x42: "0x42\t\tFETCH_HEADER\t\tFetch 5BL header from flash",
    0x43: "0x43\t\tVERIFY_HEADER\t\tVerify 5BL header\t\tBad 5BL header",
    0x44: "0x44\t\tFETCH_CONTENTS\t\tCopy 5BL to RAM\t\tBad 5BL image",
    0x45: "0x45\t\tHMACSHA_COMPUTE\t\tCompute 5BL hash",
    0x46: "0x46\t\tRC4_INITIALIZE\t\tInitialize 5BL RC4",
    0x47: "0x47\t\tRC4_DECRYPT\t\tDecrypt 5BL\t\tBad 5BL image",
    0x48: "0x48\t\tSHA_COMPUTE\t\tCompute 5BL hash",
    0x49: "0x49\t\tSHA_VERIFY\t\tVerify 5BL hash\t\tBad 5BL signature",
    0x4A: "0x4A\t\tLOAD_6BL\t\tLoad 6BL",
    0x4B: "0x4B\t\tLZX_EXPAND\t\tExpand 6BL",
    0x4C: "0x4C\t\tSWEEP_CACHES\t\tClear L1 and L2 cache",
    0x4D: "0x4D\t\tDECODE_FUSES\t\tDecode fuses",
    0x4E: "0x4E\t\tFETCH_OFFSET_6BL\t\tFetch 6BL offset from flash",
    0x4F: "0x4F\t\tVERIFY_OFFSET_6BL\t\tVerify 6BL offset\t\tBad 6BL offset",
    0x50: "0x50\t\tLOAD_UPDATE_1\t\tLoad Patch Slot 1\t\tBad patch slot 1 image",
    0x51: "0x51\t\tLOAD_UPDATE_2\t\tLoad Patch Slot 2\t\tBad patch slot 2 image",
    0x52: "0x52\t\tBRANCH\t\tBranch to hypervisor",
    0x53: "0x53\t\tDECRYPT_VERIFY_HV_CERT\t\tDecrypt and verify HV cert\t\tBad HV cert",
    0x58: "0x58\t\tINIT_HYPERVISOR\t\tInitialize hypervisor",
    0x59: "0x59\t\tINIT_SOC_MMIO\t\tInitialize SoC MMIO\t\tBad CPU",
    0x5A: "0x5A\t\tINIT_XEX_TRAINING\t\tInitialize XEX training",
    0x5B: "0x5B\t\tINIT_KEYRING\t\tInitialize key ring",
    0x5C: "0x5C\t\tINIT_KEYS\t\tInitialize keys",
    0x5D: "0x5D\t\tINIT_SOC_INT\t\tInitialize SoC interrupts",
    0x5E: "0x5E\t\tINIT_SOC_INT_COMPLETE\t\tHypervisor initialization complete",
    0x60: "0x60\t\tINIT_KERNEL\t\tInitialize kernel",
    0x61: "0x61\t\tINITIAL_HAL_PHASE_0\t\tInitialize HAL phase 0",
    0x62: "0x62\t\tINIT_PROCESS_OBJECTS\t\tInitialize process objects",
    0x63: "0x63\t\tINIT_KERNEL_DEBUGGER\t\tInitialize kernel debugger",
    0x64: "0x64\t\tINIT_MEMORY_MANAGER\t\tInitialize memory manager",
    0x65: "0x65\t\tINIT_STACKS\t\tInitialize stacks",
    0x66: "0x66\t\tINIT_OBJECT_SYSTEM\t\tInitialize object system",
    0x67: "0x67\t\tINIT_PHASE1_THREAD\t\tInitialize phase 1 thread",
    0x68: "0x68\t\tINIT_PROCESSORS\t\tInitialize processors",
    0x69: "0x69\t\tINIT_KEYVAULT\t\tInitialize keyvault\t\tBad keyvault",
    0x6A: "0x6A\t\tINIT_HAL_PHASE_1\t\tInitialize HAL phase 1",
    0x6B: "0x6B\t\tINIT_SFC_DRIVER\t\tInitialize flash controller",
    0x6C: "0x6C\t\tINIT_SECURITY\t\tInitialize security",
    0x6D: "0x6D\t\tINIT_KEY_EX_VAULT\t\tInitialize extended keyvault\t\tBad keyvault",
    0x6E: "0x6E\t\tINIT_SETTINGS\t\tInitialize settings",
    0x6F: "0x6F\t\tINIT_POWER_MODE\t\tInitialize power mode",
    0x70: "0x70\t\tINIT_VIDEO_DRIVER\t\tInitialize video driver",
    0x71: "0x71\t\tINIT_AUDIO_DRIVER\t\tInitialize audio driver",
    0x72: "0x72\t\tINIT_BOOT_ANIMATION\t\tInitialize bootanim.xex, XMADecoder, XAudioRender\t\tMissing/corrupted bootanim.xex",
    0x73: "0x73\t\tINIT_SATA_DRIVER\t\tInitialize SATA driver",
    0x74: "0x74\t\tINIT_SHADOWBOOT\t\tInitialize shadowboot",
    0x75: "0x75\t\tINIT_DUMP_SYSTEM\t\tInitialize dump system",
    0x76: "0x76\t\tINIT_SYSTEM_ROOT\t\tInitialize system root",
    0x77: "0x77\t\tINIT_OTHER_DRIVERS\t\tInitialize other drivers",
    0x78: "0x78\t\tINIT_STFS_DRIVER\t\tInitialize STFS driver",
    0x79: "0x79\t\tLOAD_XAM\t\tInitialize xam.xex\t\tMissing/corrupted xam.xex",
    0xFF: "0xFF\t\tFATAL\t\tPanic - Hypervisor Error",
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
            msg = POST_MESSAGES.get(val, "0x{:02X}\t\tUnknown code".format(val))
            uart.write(msg + "\r\n")

    time.sleep(0.005)
