import json
import os
import os
import time
import uuid
import random
from confluent_kafka import Producer
from src.core.config import settings
from src.core.security import security

def delivery_report(err, msg):
    """Callback for Kafka delivery results."""
    if err is not None:
        print(f"[Producer] Message delivery failed: {err}")
    else:
        pass # Silent success for performance at scale

class SecureDataProducer:
    """
    Simulates a high-volume data source (100M+ potential records).
    Supports Kafka (DOCKER) or Local File (SIMULATED) modes.
    """
    def __init__(self):
        self.mode = settings.PIPELINE_MODE
        if self.mode == "DOCKER":
            self.producer = Producer(settings.get_kafka_config())
            self.topic = settings.KAFKA_TOPIC
        else:
            self.stream_file = "data/stream.jsonl"
            os.makedirs("data", exist_ok=True)
            print(f"[Producer] Running in SIMULATED mode. Output: {self.stream_file}")

    def generate_transaction(self):
        """Generates a realistic financial transaction with PII."""
        user_id = str(uuid.uuid4())
        raw_email = f"user_{random.randint(1, 1000000)}@example.com"
        encrypted_email = security.encrypt_data(raw_email).decode('utf-8')
        
        return {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user_id,
            "email_enc": encrypted_email,
            "amount": round(random.uniform(10.0, 5000.0), 2),
            "currency": "ZAR",
            "timestamp": time.time(),
            "meta": "secure_transaction_v1"
        }

    def stream_data(self, record_count: int = 1000):
        """Streams a batch of secure records."""
        print(f"[Producer] Starting secure stream of {record_count} records...")
        
        if self.mode == "DOCKER":
            for i in range(record_count):
                data = self.generate_transaction()
                self.producer.produce(self.topic, key=data["user_id"], value=json.dumps(data), callback=delivery_report)
                if i % 100 == 0: self.producer.poll(0)
            self.producer.flush()
        else:
            with open(self.stream_file, "a") as f:
                for _ in range(record_count):
                    data = self.generate_transaction()
                    f.write(json.dumps(data) + "\n")
        
        print(f"[Producer] Batch complete. {record_count} records processed.")

if __name__ == "__main__":
    producer = SecureDataProducer()
    # Test with a small batch
    producer.stream_data(record_count=100)
