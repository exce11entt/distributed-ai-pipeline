from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.data.vector_db import get_vector_store
import asyncio

class IngestionPipeline:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def process_text(self, text: str, source: str) -> List[Document]:
        """Chunks raw text into documents."""
        docs = self.text_splitter.create_documents(
            texts=[text],
            metadatas=[{"source": source}]
        )
        return docs

    async def ingest_document(self, text: str, source: str):
        """Full flow: Chunk -> Embed -> Upsert."""
        print(f"--- Ingesting: {source} ---")
        docs = self.process_text(text, source)
        print(f"Created {len(docs)} chunks.")
        
        await self.vector_store.upsert_documents(docs)
        print("Upsert complete.")

# Simple Manual Test
if __name__ == "__main__":
    async def main():
        pipeline = IngestionPipeline()
        
        # Simulated "Bank Policy" document
        sample_policy = """
        INTERNATIONAL TRANSFER POLICY (2025)
        
        1. Limits:
           - Personal accounts: $50,000 daily limit.
           - Business accounts: $250,000 daily limit.
           
        2. Fees:
           - SWIFT transfers incur a flat fee of $25.
           - SEPA transfers are free for amounts under €10,000.
           
        3. Compliance:
           - All transfers over $10,000 require AML verification.
           - Transfers to sanctioned regions are automatically blocked.
        """
        
        await pipeline.ingest_document(sample_policy, "policy_manual_v1.txt")

    asyncio.run(main())
