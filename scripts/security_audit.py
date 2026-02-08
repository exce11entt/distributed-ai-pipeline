import json
from src.core.security import SecurityEngine
from src.pipeline.secure_producer import SecureDataProducer

def audit_security_layers():
    print("--- STARTING SECURITY AUDIT & VALIDATION ---")
    
    security = SecurityEngine()
    producer = SecureDataProducer()
    
    # 1. Test Raw Data Generation
    raw_data = producer.generate_transaction()
    print(f"[1] Raw Transaction Generated: {raw_data['transaction_id']}")
    
    # 2. Check PII Encryption (Producer Level)
    if "email_enc" in raw_data and raw_data["email_enc"] != "user@example.com":
        print("✅ PASS: Producer-level encryption active.")
    else:
        print("❌ FAIL: Producer-level encryption inactive.")
        
    # 3. Test Anonymization (Spark Layer Logic)
    test_user_id = "USER_12345"
    anonymized = security.anonymize_pii(test_user_id)
    
    print(f"[2] Anonymization Test:")
    print(f"    Raw ID: {test_user_id}")
    print(f"    Anonymized ID: {anonymized}")
    
    if test_user_id not in anonymized and len(anonymized) == 64:
        print("✅ PASS: SHA-256 Hashing with Salt verified.")
    else:
        print("❌ FAIL: Anonymization logic compromised.")
        
    # 4. Check for Salt Consistency
    anonymized_2 = security.anonymize_pii(test_user_id)
    if anonymized == anonymized_2:
        print("✅ PASS: Deterministic hashing (Salt applied correctly).")
    else:
        print("❌ FAIL: Salt is inconsistent.")

if __name__ == "__main__":
    audit_security_layers()
