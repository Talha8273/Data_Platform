from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from datetime import datetime, timedelta
import redis
import json

default_args = {
    'owner': 'talha',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# 1. EXTRACT: Redis'ten Veri Çekme
def redis_ten_veri_cek(**kwargs):
    # Redis konteynerine bağlanıyoruz
    r = redis.Redis(host='wanderlog-redis-cache', port=6379, db=0, decode_responses=True)
    
    # Test için Redis'e geçici bir ham veri bırakıyoruz (Normalde API'den gelir)
    ornek_veri = {"ad": "mustafa", "bolum": "istatistik"}
    r.set('gecici_ogrenci_kaydi', json.dumps(ornek_veri))
    
    # Veriyi Redis'ten çekiyoruz
    cekilen_veri = json.loads(r.get('gecici_ogrenci_kaydi'))
    print(f"Redis'ten Çekilen Ham Veri: {cekilen_veri}")
    
    return cekilen_veri

# 2. TRANSFORM: Veriyi Temizleme
def veriyi_donustur(**kwargs):
    ti = kwargs['ti']
    ham_veri = ti.xcom_pull(task_ids='extract_redis')
    
    # Veritabanı standartları için isim baş harfini büyütüp, bölümü tamamen büyük harf yapıyoruz
    temiz_veri = {
        "ad": ham_veri["ad"].capitalize(),
        "bolum": ham_veri["bolum"].upper()
    }
    print(f"Dönüştürülen Temiz Veri: {temiz_veri}")
    return temiz_veri

# 3. LOAD: MariaDB'ye Kalıcı Olarak Yazma
def mariadb_ye_yukle(**kwargs):
    ti = kwargs['ti']
    islenmis_veri = ti.xcom_pull(task_ids='transform_veri')
    
    # Airflow arayüzünde kaydettiğimiz bağlantı kasasını (mariadb_conn) çağırıyoruz
    mysql_hook = MySqlHook(mysql_conn_id='mariadb_conn')
    
    # MariaDB'ye SQL sorgusu gönderiyoruz
    insert_sql = "INSERT INTO ogrenciler (ad, bolum) VALUES (%s, %s)"
    mysql_hook.run(insert_sql, parameters=(islenmis_veri['ad'], islenmis_veri['bolum']))
    print(f"Başarılı: {islenmis_veri['ad']} verisi MariaDB'ye yazıldı!")

with DAG(
    dag_id='04_gercek_etl_redis_mariadb',
    default_args=default_args,
    description='Redis ve MariaDB Arası Gerçek Veri Taşıma',
    start_date=datetime(2026, 9, 21),
    schedule_interval=None,
    catchup=False,
    tags=['ETL', 'Redis', 'MariaDB', 'Polyglot'],
) as dag:

    task1 = PythonOperator(task_id='extract_redis', python_callable=redis_ten_veri_cek)
    task2 = PythonOperator(task_id='transform_veri', python_callable=veriyi_donustur)
    task3 = PythonOperator(task_id='load_mariadb', python_callable=mariadb_ye_yukle)

    task1 >> task2 >> task3