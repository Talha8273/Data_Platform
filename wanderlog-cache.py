import redis
import schedule
import time
import datetime
import psycopg2 # PostgreSQL ile konuşmamızı sağlayan kütüphane

def veri_cekme_gorevi():
    su_an = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{su_an}] ⏱️ Wanderlog işlemi başlatıldı...")
    
    # 1. VERİYİ ÜRETME (Şimdilik sahte veri, sonra canlıya geçeceğiz)
    canli_fiyat = "1500 USD"
    hedef_sehir = "Paris"
    
    # 2. REDİS'E YAZMA (Hafıza)
    try:
        r = redis.Redis(host='wanderlog-redis-cache', port=6379, db=0, decode_responses=True)
        r.set(f'Wanderlog:{hedef_sehir}_Cost', canli_fiyat)
        print(f"[{su_an}] 🟢 Veri Redis'e yazıldı!")
    except Exception as e:
        print(f"[{su_an}] ❌ Redis hatası: {e}")

    # 3. POSTGRESQL'E YAZMA (Kalıcı Disk)
    try:
        # DİKKAT: Buradaki şifre ve kullanıcı adını docker-compose.yml dosyasındaki ayarlarına göre düzelt!
        conn = psycopg2.connect(
            host="wanderlog-postgres-db", # Portainer'da gördüğümüz DB konteynerinin adı
            database="postgres",          # docker-compose içindeki POSTGRES_DB (genelde postgres'tir)
            user="postgres",              # docker-compose içindeki POSTGRES_USER
            password="Talha8293.",# docker-compose içindeki POSTGRES_PASSWORD
            port="5432"
        )
        cursor = conn.cursor()
        
        # Tablo yoksa otomatik oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wanderlog_fiyatlar (
                id SERIAL PRIMARY KEY,
                sehir VARCHAR(50),
                fiyat VARCHAR(50),
                kayit_zamani TIMESTAMP
            )
        """)
        
        # Veriyi tabloya ekle
        cursor.execute("""
            INSERT INTO wanderlog_fiyatlar (sehir, fiyat, kayit_zamani)
            VALUES (%s, %s, %s)
        """, (hedef_sehir, canli_fiyat, su_an))
        
        # Değişiklikleri kaydet ve kapıyı kapat
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[{su_an}] 🔵 Veri PostgreSQL'e kalıcı olarak yazıldı!")
        
    except Exception as e:
        print(f"[{su_an}] ❌ PostgreSQL hatası: {e}")

    print(f"[{su_an}] ✅ İşlem başarıyla tamamlandı!\n")

# Görevi her 1 dakikada bir çalıştır
schedule.every(1).minutes.do(veri_cekme_gorevi)

print("🚀 Zamanlayıcı aktif. Sistem hazır...")
veri_cekme_gorevi() # Beklemeden ilk tetikleme

while True:
    schedule.run_pending()
    time.sleep(1)