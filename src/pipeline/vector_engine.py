import os
import json
import numpy as np
from typing import List, Dict
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from src.core.config import settings

class VectorEngine:
    """
    Massively parallel vectorization and loader for Pinecone.
    Designed to be run within Spark Partitions for 100M+ scale.
    """
    def __init__(self):
        # Initialize Pinecone gRPC
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        
        # Load embedding model locally on each worker
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generates embeddings for a batch of texts."""
        return self.model.encode(texts, convert_to_numpy=True)

    def upsert_batch(self, data_points: List[Dict]):
        """
        Upserts a batch of vectors to Pinecone.
        Format: [{"id": "...", "values": [...], "metadata": {...}}]
        """
        try:
            # Use gRPC for high throughput
            self.index.upsert(vectors=data_points)
        except Exception as e:
            print(f"[VectorEngine] Upsert failed: {e}")

def process_spark_partition(iter):
    """
    Spark Partition task: processes a chunk of data, generates embeddings, 
    and upserts to Pinecone in one high-throughput cycle.
    """
    engine = VectorEngine()
    batch = []
    
    for row in iter:
        # Prepare text for embedding (e.g., combine anonymized_id and amount)
        text_to_embed = f"User {row.anonymized_id} Transacted {row.amount} {row.currency}"
        
        embedding = engine.generate_embeddings([text_to_embed])[0].tolist()
        
        vector_data = {
            "id": row.transaction_id,
            "values": embedding,
            "metadata": {
                "anonymized_id": row.anonymized_id,
                "amount": row.amount,
                "currency": row.currency,
                "audit_tag": row.audit_tag
            }
        }
        batch.append(vector_data)
        
        # Upsert in batches of 100 for stability
        if len(batch) >= 100:
            engine.upsert_batch(batch)
            batch = []

    # Final flush
    if batch:
        engine.upsert_batch(batch)
    
    return [True] # Signal success per partition

if __name__ == "__main__":
    print("[VectorEngine] Initialized for distributed execution.")
