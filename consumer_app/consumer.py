import json
import os
import time
import logging
import psycopg2
from kafka import KafkaConsumer

# Configure centralized logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fetch configurations from environment variables (Cloud-native approach)
DB_HOST = os.getenv("DB_HOST", "wanderlog-postgres-db")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka-lab:29092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sensor-verileri")

def get_db_password():
    try:
        with open('/run/secrets/postgres_password', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        logging.error("Secret file not found. Ensure Docker secrets are configured.")
        return None

def connect_to_db():
    pg_password = get_db_password()
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=pg_password
            )
            conn.autocommit = False
            logging.info("Successfully connected to PostgreSQL.")
            return conn
        except psycopg2.OperationalError as e:
            logging.warning(f"Database connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def initialize_db(conn):
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
    logging.info("Database table 'raw_events' initialized and ready.")

def main():
    conn = connect_to_db()
    initialize_db(conn)

    logging.info(f"Connecting to Kafka broker at {KAFKA_BROKER}...")
    
    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                group_id='pg-writer-group',
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logging.info("Kafka Consumer is active. Listening for messages...")
            break
        except Exception as e:
            logging.warning(f"Kafka connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    for msg in consumer:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO raw_events (payload, kafka_offset) VALUES (%s, %s) ON CONFLICT (kafka_offset) DO NOTHING",
                    (json.dumps(msg.value), msg.offset)
                )
            conn.commit()
            consumer.commit()
            logging.info(f"Processed and committed message offset {msg.offset}")
        except Exception as e:
            conn.rollback()
            logging.error(f"Critical error processing message: {e}")

if __name__ == "__main__":
    main()
