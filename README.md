# Secure Big Data AI Pipeline (100M+ Records)

A production-grade, security-first distributed pipeline for processing, anonymizing, and vectorizing massive datasets (100M+ records) in real-time.

## 🚀 Overview
This project demonstrates high-scale AI engineering, focusing on the intersection of **Big Data**, **Generative AI**, and **Cybersecurity**. It moves data from raw ingestion to a searchable vector database while maintaining absolute privacy and sub-second processing latency.

### Key Features
- **Scalable Ingestion**: Decoupled producer architecture using Kafka with TLS/SSL.
- **Real-Time Anonymization**: Distributed PII scrubbing using PySpark UDFs.
- **Massively Parallel Vectorization**: Partition-level embedding generation using `sentence-transformers`.
- **High-Throughput Sink**: Optimized Pinecone gRPC upserts for 100M+ record indexing.
- **Enterprise Security**: HashiCorp Vault integration, end-to-end encryption, and automated audit trails.

## 🛠️ Tech Stack
- **Frameworks**: PySpark (3.5+), Kafka, LangChain
- **AI**: Sentence-Transformers, Pinecone (gRPC)
- **Security**: HashiCorp Vault, Fernet (AES-128), SHA-256 Salting
- **Infrastructure**: Docker, Kubernetes, Prometheus/Grafana

## 📂 Project Structure
```text
├── src/
│   ├── core/           # Security, Config, Spark Factory
│   ├── pipeline/       # Producer, Anonymizer, Vector Engine
│   └── main.py         # Orchestrator
├── deploy/             # Kubernetes & Docker files
├── requirements.txt    # Project dependencies
└── README.md
```

## 🔒 Security Posture
1. **PII Anonymization**: All sensitive user IDs and emails are salted and hashed before entering the vector store.
2. **Encryption In-Transit**: Mandatory TLS for all service-to-service communication.
3. **Secret Isolation**: Zero hardcoded keys; all credentials fetched dynamically via the `SecurityEngine`.

## 📈 Performance
- **Target Scale**: 100,000,000+ Records
- **Processing Latency**: < 800ms (End-to-End)
- **Ingestion Speed**: Optimized for 50k+ records/sec per partition.
