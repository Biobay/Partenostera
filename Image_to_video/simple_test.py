import requests

# Test diretto API AI Horde
API_KEY = "xbCXATE-9l8CPYqfojI9iQ"

print("Test AI Horde API...")

# Test 1: Heartbeat
try:
    r = requests.get("https://stablehorde.net/api/v2/status/heartbeat", timeout=10)
    print(f"Heartbeat: {r.status_code}")
except Exception as e:
    print(f"Errore heartbeat: {e}")

# Test 2: User info
try:
    headers = {"apikey": API_KEY}
    r = requests.get("https://stablehorde.net/api/v2/find_user", headers=headers, timeout=10)
    print(f"User info: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Username: {data.get('username', 'N/A')}")
        print(f"Kudos: {data.get('kudos', 0)}")
except Exception as e:
    print(f"Errore user info: {e}")

print("Test completato!")
