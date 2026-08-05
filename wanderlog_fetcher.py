import requests
import redis
import json

# 1. Altyapı Bağlantısı (Redis)
r = redis.Redis(host='wanderlog_cache', port=6379, db=0, decode_responses=True)

print("Gercek dunya verisi aranıyor (Frankfurter API)...")

# 2. Dış Dünya ile İletişim (API Request)
# Euro'nun Dolar (USD) karşısındaki güncel değerini çekiyoruz
url = "https://api.frankfurter.app/latest?from=EUR&to=USD"

try:
    response = requests.get(url)
    response.raise_for_status() # Eğer site hata verirse (404, 500) bizi uyarır.
    
    # Gelen veriyi JSON (sözlük) formatına çeviriyoruz
    data = response.json()
    
    # İhtiyacımız olan asıl veriyi alıyoruz
    guncel_kur = data['rates']['USD']
    tarih = data['date']
    
    print(f"Cekilen Veri -> Tarih: {tarih}, EUR/USD Kuru: {guncel_kur}")

    # 3. Veriyi Platforma (Redis'e) Yazmak
    # Wanderlog projemiz için bu kuru hafızaya alıyoruz
    r.set('Wanderlog:ExchangeRate:EUR_USD', guncel_kur)
    print("Canli veri basariyla Redis'e yazildi!")

except Exception as e:
    print(f"Veri cekilirken bir hata olustu: {e}")

# 4. Kontrol (Redis'ten okuma)
kayitli_veri = r.get('Wanderlog:ExchangeRate:EUR_USD')
print(f"Sistemden Dogrulama - Kaydedilen Kur: {kayitli_veri}")
