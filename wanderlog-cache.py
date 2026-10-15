import json
import time
import datetime
import random
from kafka import KafkaProducer

print("Producer aktif: Sisteme bağlanılıyor...")

producer = KafkaProducer(
    bootstrap_servers=['kafka-lab:29092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print(" Kafkaya çıkıldı. Veri akışı başlıyor...")

while True:
    su_an = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    fiyat = random.randint(1200, 1800)
    data = {
        "sehir": "Paris",
        "canli_fiyat": f"{fiyat} USD",
        "kayit_zamani": su_an
    }

    producer.send('sensor-verileri', value=data)

    print(f"[{su_an}] Kafka'ya fırlatıldı: {data}")

    time.sleep(3)
