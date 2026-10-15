import json
import time
import random
import os
import logging
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka-lab:29092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sensor-verileri")

def connect_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            logging.info(f"Successfully connected to Kafka broker at {KAFKA_BROKER}")
            return producer
        except Exception as e:
            logging.warning(f"Kafka connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def main():
    producer = connect_producer()
    logging.info("Starting data stream to Kafka topic...")

    while True:
        data = {
            'sensor_id': random.randint(1, 100),
            'sicaklik': round(random.uniform(20.0, 85.0), 2)
        }
        try:
            producer.send(KAFKA_TOPIC, value=data)
            logging.info(f"Successfully transmitted payload: {data}")
        except Exception as e:
            logging.error(f"Failed to transmit data: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
