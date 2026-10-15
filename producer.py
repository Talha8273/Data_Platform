import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['kafka-lab:29092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("Veriler düzenli şekilde Kafka otobanına akıyor...")

while True:
    data = {
        'sensor_id': random.randint(1, 100),
        'sicaklik': round(random.uniform(20.0, 85.0), 2)
    }
    producer.send('sensor-verileri', value=data)

    time.sleep(2)
