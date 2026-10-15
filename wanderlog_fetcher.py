import requests
import redis
import json

r = redis.Redis(host='wanderlog_cache', port=6379, db=0, decode_responses=True)

print("Gercek dunya verisi aranıyor (Frankfurter API)...")

url = "https://api.frankfurter.app/latest?from=EUR&to=USD"

try:
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    guncel_kur = data['rates']['USD']
    tarih = data['date']

    print(f"Cekilen Veri -> Tarih: {tarih}, EUR/USD Kuru: {guncel_kur}")


    r.set('Wanderlog:ExchangeRate:EUR_USD', guncel_kur)
    print("Canli veri basariyla Redis'e yazildi!")

except Exception as e:
    print(f"Veri cekilirken bir hata olustu: {e}")


kayitli_veri = r.get('Wanderlog:ExchangeRate:EUR_USD')
print(f"Sistemden Dogrulama - Kaydedilen Kur: {kayitli_veri}")
