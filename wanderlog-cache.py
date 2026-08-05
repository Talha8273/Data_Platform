import redis

# Redis konteynerimize bağlanıyoruz (Port 6379'u ayarlamıştık)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

print("Redis ile baglanti kuruluyor...")

# Wanderlog için örnek bir veriyi Redis'e (Hafızaya) yazıyoruz
r.set('Wanderlog:Paris_Cost', '1500 USD')
print("Veri Redis'e yazildi!")

# Şimdi o veriyi Redis'ten okuyup ekrana basıyoruz
paris_fiyati = r.get('Wanderlog:Paris_Cost')
print(f"Redis'ten okunan Paris fiyati: {paris_fiyati}")
