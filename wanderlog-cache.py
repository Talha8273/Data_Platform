import json
import time
import datetime
import random
from kafka import KafkaProducer

print("🚀 Producer aktif: Sisteme bağlanılıyor...")

# Sadece Kafka'ya bağlanıyoruz. Veritabanı veya Redis bağlantısı yok!
producer = KafkaProducer(
    bootstrap_servers=['kafka-lab:29092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("✅ Kafka otobanına çıkıldı. Veri akışı başlıyor...")

while True:
    su_an = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Kendi temana uygun sahte veri üretiyoruz
    fiyat = random.randint(1200, 1800)
    data = {
        "sehir": "Paris",
        "canli_fiyat": f"{fiyat} USD",
        "kayit_zamani": su_an
    }
    
    # Veriyi Kafka'daki "sensor-verileri" topic'ine fırlat
    # (Consumer'ımız bu topic'i dinlediği için buraya gönderiyoruz)
    producer.send('sensor-verileri', value=data)
    
    print(f"[{su_an}] 📡 Kafka'ya fırlatıldı: {data}")
    
    # Sistemi ve RAM'i yormamak için her gönderim arası 3 saniye bekle
    time.sleep(3)
