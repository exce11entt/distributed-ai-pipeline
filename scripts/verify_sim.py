from src.pipeline.secure_producer import SecureDataProducer
import os

print("--- Starting Pipeline Verification (Simulated) ---")
producer = SecureDataProducer()
producer.stream_data(record_count=100)

if os.path.exists("data/stream.jsonl"):
    size = os.path.getsize("data/stream.jsonl")
    print(f"SUCCESS: 'data/stream.jsonl' created. Size: {size} bytes.")
    
    with open("data/stream.jsonl", "r") as f:
        print("\n[SAMPLE RECORD FROM STREAM]:")
        print(f.readline())
else:
    print("FAILURE: 'data/stream.jsonl' was not created.")
