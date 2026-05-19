import requests
import time

# Villain listener ünvanı
url = "http://127.0.0.1:8080/p_res" 
headers = {
    "X-Hoax-ID": "test_session_123", # Koddakı header_id-yə uyğun olaraq
    "Content-Length": "12"
}

print("[*] Villain-ə əmr nəticəsi simulyasiyası göndərilir...")
try:
    # Komandanın uğurlu nəticəsi kimi "Ugurla icra olundu" datası göndərilir
    response = requests.post(url, headers=headers, data="Ugurla icra olundu", timeout=5)
    print(f"[+] Server cavabı: {response.status_code}")
except requests.exceptions.Timeout:
    print("[-] XƏTA: Server asılı qaldı (Timeout)! Kod hələ də problemlidir.")