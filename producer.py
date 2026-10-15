import json
import time
import random
from kafka import KafkaProducer

# Localhost yerine Docker ağındaki Kafka konteynerinin adını (kafka-lab) kullanıyoruz
producer = KafkaProducer(
    bootstrap_servers=['kafka-lab:29092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("Veriler hafif ve düzenli bir şekilde Kafka otobanına akıyor...")

# 50.000 sınırı yerine sonsuz döngü kullanıyoruz
while True:
    data = {
        'sensor_id': random.randint(1, 100),
        'sicaklik': round(random.uniform(20.0, 85.0), 2)
    }
    producer.send('sensor-verileri', value=data)
    
    # Sistemi yormamak için 1 milisaniye yerine 2 saniyelik (2.0) es veriyoruz
    time.sleep(2)
