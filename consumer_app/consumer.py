import json
import os
import psycopg2
from kafka import KafkaConsumer

print("Postgres'e bağlanılıyor...")
# Docker secret dosyasından şifreyi okuyoruz
pg_password = open('/run/secrets/postgres_password').read().strip()

conn = psycopg2.connect(
    host="wanderlog-postgres-db",
    database="postgres",
    user="postgres",
    password=pg_password
)
conn.autocommit = False # DeepSeek Önerisi: Manuel commit kontrolü bizde

# Tabloyu otomatik oluştur (Eğer yoksa)
with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_events (
            id SERIAL PRIMARY KEY,
            payload JSONB,
            kafka_offset BIGINT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
conn.commit()

print("Kafka'ya bağlanılıyor...")
consumer = KafkaConsumer(
    'sensor-verileri', # Producer'ın veri gönderdiği topic adını buraya yazıyoruz
    bootstrap_servers=['kafka-lab:29092'],
    group_id='pg-writer-group',
    auto_offset_reset='earliest',
    enable_auto_commit=False, # DeepSeek Önerisi: Sadece DB'ye yazılırsa Kafka'da ilerle
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Consumer aktif. Veriler dinleniyor ve Postgres'e yazılıyor...")

for msg in consumer:
    try:
        with conn.cursor() as cur:
            # ON CONFLICT DO NOTHING: Aynı mesaj iki kez gelirse (tekrar) veritabanına çift yazılmasını engeller
            cur.execute(
                "INSERT INTO raw_events (payload, kafka_offset) VALUES (%s, %s) ON CONFLICT (kafka_offset) DO NOTHING",
                (json.dumps(msg.value), msg.offset)
            )
        conn.commit()      # 1. Önce Veritabanına işlemi onayla
        consumer.commit()  # 2. Sonra Kafka'ya "bu mesajı başarıyla işledim" de
        print(f"Başarıyla yazıldı: Offset {msg.offset} -> Veri: {msg.value}")
    except Exception as e:
        conn.rollback()    # Hata olursa DB işlemini iptal et
        print(f"Kritik Hata: {e}")
