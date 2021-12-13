# MPEG version <number> layer <number> bit rate in kbps (k=1000)
m1l1 = {
        1: 32,
        2: 64,
        3: 96,
        4: 128,
        5: 160,
        6: 192,
        7: 224,
        8: 256,
        9: 288,
        10: 320,
        11: 352,
        12: 384,
        13: 416,
        14: 448
    }
m1l2 = {
        1: 32,
        2: 48,
        3: 56,
        4: 64,
        5: 80,
        6: 96,
        7: 112,
        8: 128,
        9: 160,
        10: 192,
        11: 224,
        12: 256,
        13: 320,
        14: 384
    }


m1l3 = {
        1: 32,
        2: 40,
        3: 48,
        4: 56,
        5: 64,
        6: 80,
        7: 96,
        8: 112,
        9: 128,
        10: 160,
        11: 192,
        12: 224,
        13: 256,
        14: 320
    }
m2l1 = {
        1: 32,
        2: 64,
        3: 96,
        4: 128,
        5: 160,
        6: 192,
        7: 224,
        8: 256,
        9: 288,
        10: 320,
        11: 352,
        12: 384,
        13: 416,
        14: 448
    }
m2l2 = {
        1: 32,
        2: 48,
        3: 56,
        4: 64,
        5: 80,
        6: 96,
        7: 112,
        8: 128,
        9: 160,
        10: 192,
        11: 224,
        12: 256,
        13: 320,
        14: 384
    }
m2l3 = {
        1: 8,
        2: 16,
        3: 24,
        4: 32,
        5: 64,
        6: 80,
        7: 56,
        8: 64,
        9: 128,
        10: 160,
        11: 112,
        12: 128,
        13: 256,
        14: 320
    }

# sample per second according to mpeg version and layer, first bit =1 version 1, =0 version 2, next 2 bits =01 layer 3, =10 layer 2, =11 layer 1
sample = {
    0b101: 1152,
    0b110: 1152,
    0b111: 384,
    0b01: 1152,
    0b10: 1152,
    0b11: 384,
}

# sample rate in hertz, m1 = mpeg version 1, numbers are in the header's frequency bits
m1sr = {
    0: 44100,
    1: 48000,
    2: 32000
}
m2sr = {
    0: 22050,
    1: 24000,
    2: 16000
}

# gets the header of an mp3 frame (4 bytes) and returns the bit rate and teh sample rate
def headtorate(header: bytearray):
    res =(header[1] & 0b1110) >> 1
    bits = ((header[2] & 0b11110000) >> 4)
    sam = (header[2]&0b1100) >>2
    if res == 0b101:
        # MPEG 1 layer 3
        return m1l3[bits], m1sr[sam]
    elif res == 0b110:
        # mpeg 1 layer 2
        return m1l2[bits], m1sr[sam]
    elif res == 0b111:
        # mpeg 1 layer 1
        return m1l1[bits], m1sr[sam]
    elif res == 0b1:
        # MPEG 2 layer 3
        return m2l3[bits], m2sr[sam]
    elif res == 0b10:
        # mpeg 2 layer 2
        return m2l2[bits], m2sr[sam]
    elif res == 0b11:
        # mpeg 2 layer 1
        return m2l1[bits], m2sr[sam]
    else:
        raise Exception('bad format')
