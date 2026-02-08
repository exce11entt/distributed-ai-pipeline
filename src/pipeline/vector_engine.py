import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from src.core.config import settings
from typing import List, Dict

class VectorEngine:
    """
    Massively parallel vectorization and loader for Chroma DB.
    Designed to be run within Spark Partitions for 100M+ scale.
    """
    def __init__(self):
        # Initialize Chroma HTTP Client (distributed safe)
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST, 
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Load embedding model locally on each worker
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def upsert_batch(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict], documents: List[str]):
        """
        Upserts a batch of vectors to Chroma DB.
        """
        try:
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
        except Exception as e:
            print(f"[VectorEngine] Chroma Upsert failed: {e}")

def process_spark_partition(iter):
    """
    Spark Partition task: processes a chunk of data, generates embeddings, 
    and upserts to Chroma in one high-throughput cycle.
    """
    engine = VectorEngine()
    
    ids = []
    embeddings = []
    metadatas = []
    documents = []
    
    for row in iter:
        # Prepare text for embedding
        text_to_embed = f"User {row.anonymized_id} Transacted {row.amount} {row.currency}"
        
        # Generate single embedding for the row
        vector = engine.generate_embeddings([text_to_embed])[0]
        
        ids.append(row.transaction_id)
        embeddings.append(vector)
        metadatas.append({
            "anonymized_id": row.anonymized_id,
            "amount": row.amount,
            "currency": row.currency,
            "audit_tag": row.audit_tag
        })
        documents.append(text_to_embed)
        
        # Upsert in batches of 100 for stability and throughput
        if len(ids) >= 100:
            engine.upsert_batch(ids, embeddings, metadatas, documents)
            ids, embeddings, metadatas, documents = [], [], [], []

    # Final flush
    if ids:
        engine.upsert_batch(ids, embeddings, metadatas, documents)
    
    return [True] 

if __name__ == "__main__":
    print("[VectorEngine] Initialized for Chroma DB distributed execution.")
