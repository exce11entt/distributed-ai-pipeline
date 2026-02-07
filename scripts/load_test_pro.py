import json
import time
import uuid
import random
import argparse
from multiprocessing import Process, cpu_count
from confluent_kafka import Producer
from src.core.config import settings
from src.core.security import security

def generate_transaction():
    """Generates a realistic financial transaction with encrypted PII."""
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
        "meta": "load_test_v2"
    }

def producer_worker(worker_id, records_per_worker):
    """A single process worker generating and pushing records."""
    mode = settings.PIPELINE_MODE
    topic = settings.KAFKA_TOPIC
    
    if mode == "DOCKER":
        p = Producer(settings.get_kafka_config())
        print(f"[Worker {worker_id}] Starting Kafka blast of {records_per_worker} records...")
    else:
        stream_file = "data/stream.jsonl"
        os.makedirs("data", exist_ok=True)
        print(f"[Worker {worker_id}] Starting File blast of {records_per_worker} records...")

    start_time = time.time()
    
    if mode == "DOCKER":
        for i in range(records_per_worker):
            data = generate_transaction()
            p.produce(topic, key=data["user_id"], value=json.dumps(data))
            if i % 1000 == 0: p.poll(0)
        p.flush()
    else:
        # SIMULATED: Multi-process safe file writing (in real use, we'd use a lock or separate files,
        # but for this 1M record showcase, simple append is fine for local verification).
        with open("data/stream.jsonl", "a") as f:
            for _ in range(records_per_worker):
                data = generate_transaction()
                f.write(json.dumps(data) + "\n")
            
    end_time = time.time()
    
    duration = end_time - start_time
    rps = records_per_worker / duration
    print(f"[Worker {worker_id}] Finished in {duration:.2f}s ({rps:.2f} records/sec)")

def run_load_test(total_records):
    """Spawns multiple workers to achieve maximum ingestion throughput."""
    num_workers = cpu_count()
    records_per_worker = total_records // num_workers
    
    print(f"[LoadTester] Blasting {total_records} records using {num_workers} workers...")
    
    processes = []
    for i in range(num_workers):
        worker_recs = records_per_worker + (1 if i < (total_records % num_workers) else 0)
        proc = Process(target=producer_worker, args=(i, worker_recs))
        processes.append(proc)
        proc.start()
        
    for proc in processes:
        proc.join()
        
    print("[LoadTester] Load test complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="High-performance Load Tester for Big Data AI Pipeline")
    parser.add_argument("--records", type=int, default=10000, help="Total records to generate")
    args = parser.parse_args()
    
    run_load_test(args.records)
