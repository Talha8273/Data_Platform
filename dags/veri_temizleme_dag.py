import json
import re
import os
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import psycopg2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_HOST = os.getenv("DB_HOST", "wanderlog-postgres-db")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

def get_db_password():
    try:
        with open('/run/secrets/postgres_password', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.error("Secret file not found. Ensure Docker secrets are configured.")
        return None

def clean_and_transfer_data():
    logging.info("Initiating data transformation (ETL) pipeline...")
    pg_password = get_db_password()

    if not pg_password:
        raise ValueError("Database password could not be retrieved.")

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=pg_password
        )
        conn.autocommit = False
        logging.info("Successfully connected to PostgreSQL instance.")
    except psycopg2.OperationalError as e:
        logging.error(f"Database connection failed: {e}")
        raise

    try:
        with conn.cursor() as cur:

            cur.execute("ALTER TABLE raw_events ADD COLUMN IF NOT EXISTS is_processed BOOLEAN DEFAULT FALSE;")

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

            cur.execute("SELECT id, payload FROM raw_events WHERE is_processed = FALSE;")
            rows = cur.fetchall()

            if not rows:
                logging.info("No new records found for processing. Pipeline is fully synced.")
                return

            successful_inserts = 0
            processed_ids = []

            for row in rows:
                raw_id = row[0]
                payload = row[1]

                try:
                    sehir = payload.get("sehir")
                    canli_fiyat_str = payload.get("canli_fiyat", "")
                    kayit_zamani = payload.get("kayit_zamani")

                    fiyat_rakam = int(re.sub(r'[^0-9]', '', canli_fiyat_str))

                    cur.execute("""
                        INSERT INTO clean_events (raw_id, sehir, fiyat_usd, kayit_zamani)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (raw_id) DO NOTHING
                    """, (raw_id, sehir, fiyat_rakam, kayit_zamani))

                    successful_inserts += 1
                except Exception as e:
                    logging.warning(f"Data validation failed for record ID {raw_id}, skipping. Reason: {e}")
                finally:
                    processed_ids.append(raw_id)

            if processed_ids:
                cur.execute("UPDATE raw_events SET is_processed = TRUE WHERE id = ANY(%s)", (processed_ids,))

            conn.commit()
            logging.info(f"ETL Summary: Successfully processed and transferred {successful_inserts} records.")

    except Exception as e:
        conn.rollback()
        logging.error(f"Critical pipeline failure: {e}")
        raise
    finally:
        conn.close()
        logging.info("Database connection closed gracefully.")

with DAG(
    'wanderlog_kalite_kontrol_pipeline',
    default_args=default_args,
    description='Extracts, cleans, and loads raw Kafka events into the analytics data mart',
    schedule_interval=timedelta(minutes=5),
    catchup=False,
) as dag:

    temizleme_gorevi = PythonOperator(
        task_id='clean_and_transfer_raw_data',
        python_callable=clean_and_transfer_data,
    )
