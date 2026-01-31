import os
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

class VectorStoreBase(ABC):
    @abstractmethod
    async def upsert_documents(self, documents: List[Document]):
        pass

    @abstractmethod
    async def search(self, query: str, k: int = 5) -> List[Document]:
        pass

class ChromaService(VectorStoreBase):
    def __init__(self, collection_name="enterprise_knowledge"):
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = os.path.join(os.getcwd(), "chroma_db")
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    async def upsert_documents(self, documents: List[Document]):
        """Sync wrapper for Chroma's upsert since it can be blocking."""
        # Chroma handles upsert logic internally (add_documents)
        self.vector_store.add_documents(documents)
        self.vector_store.persist()
        return True

    async def search(self, query: str, k: int = 5) -> List[Document]:
        """Performs semantic search."""
        return self.vector_store.similarity_search(query, k=k)

# Factory pattern to easily switch to Pinecone later
def get_vector_store() -> VectorStoreBase:
    return ChromaService()
