import json
import re
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import psycopg2

# DAG'ın çalışma kuralları
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def clean_and_transfer_data():
    print("Veritabanına bağlanılıyor...")
    # Şifreyi güvenli secret dosyasından alıyoruz
    with open('/run/secrets/postgres_password', 'r') as f:
        pg_password = f.read().strip()

    conn = psycopg2.connect(
        host="wanderlog-postgres-db",
        database="postgres",
        user="postgres",
        password=pg_password
    )
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            # 1. Ham veri tablosuna "işlendi mi?" (is_processed) damgası ekle
            cur.execute("ALTER TABLE raw_events ADD COLUMN IF NOT EXISTS is_processed BOOLEAN DEFAULT FALSE;")
            
            # 2. Vitrin (Analytics) tablosunu oluştur
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clean_events (
                    id SERIAL PRIMARY KEY,
                    raw_id INT UNIQUE,
                    sehir VARCHAR(50),
                    fiyat_usd INT,
                    kayit_zamani TIMESTAMP,
                    temizlenme_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Sadece YENİ (işlenmemiş) verileri çek
            cur.execute("SELECT id, payload FROM raw_events WHERE is_processed = FALSE;")
            rows = cur.fetchall()

            if not rows:
                print("İşlenecek yeni veri bulunamadı. Her şey güncel!")
                return

            basarili = 0
            islenen_idler = []

            # 4. Verileri döngüyle temizle
            for row in rows:
                raw_id = row[0]
                payload = row[1] # JSON verimiz
                
                try:
                    sehir = payload.get("sehir")
                    canli_fiyat_str = payload.get("canli_fiyat", "")
                    kayit_zamani = payload.get("kayit_zamani")

                    # Kalite Kontrol: "1500 USD" yazısındaki harfleri sil, sadece sayıyı (1500) al
                    fiyat_rakam = int(re.sub(r'[^0-9]', '', canli_fiyat_str))

                    # Temizlenmiş veriyi vitrin tablosuna (clean_events) yaz
                    cur.execute("""
                        INSERT INTO clean_events (raw_id, sehir, fiyat_usd, kayit_zamani)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (raw_id) DO NOTHING
                    """, (raw_id, sehir, fiyat_rakam, kayit_zamani))

                    basarili += 1
                except Exception as e:
                    print(f"Hatalı veri atlandı (ID: {raw_id}): {e}")
                finally:
                    islenen_idler.append(raw_id)

            # 5. İşlenen ham verileri "işlendi" olarak işaretle ki bir sonraki sefer tekrar almasın
            if islenen_idler:
                cur.execute("UPDATE raw_events SET is_processed = TRUE WHERE id = ANY(%s)", (islenen_idler,))

            conn.commit()
            print(f"🎉 Rapor: {basarili} yeni kayıt başarıyla temizlendi ve vitrine aktarıldı!")
            
    except Exception as e:
        conn.rollback()
        print(f"Kritik Hata: {e}")
        raise e
    finally:
        conn.close()

# Airflow DAG Tanımlaması (Her 5 dakikada bir çalışacak)
with DAG(
    'wanderlog_kalite_kontrol_pipeline',
    default_args=default_args,
    description='Ham Kafka verilerini temizler ve analitik tabloya aktarır',
    schedule_interval=timedelta(minutes=5), # 5 dakikada bir çalışır
    catchup=False,
) as dag:

    # Görev ataması
    temizleme_gorevi = PythonOperator(
        task_id='ham_veriyi_temizle_ve_aktar',
        python_callable=clean_and_transfer_data,
    )
