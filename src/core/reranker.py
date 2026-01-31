from typing import List
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

class RerankerService:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        # This model is small (80MB) and very fast for CPU inference
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, documents: List[Document], top_k: int = 3) -> List[Document]:
        if not documents:
            return []

        # Prepare pairs for the cross-encoder: (query, document_text)
        pairs = [[query, doc.page_content] for doc in documents]
        
        # Get scores
        scores = self.model.predict(pairs)
        
        # Combine docs with scores
        scored_docs = list(zip(documents, scores))
        
        # Sort by score descending
        sorted_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)
        
        # Filter: We can also add a score threshold here (e.g., must be > 0.5)
        top_docs = [doc for doc, score in sorted_docs[:top_k]]
        
        return top_docs

# Singleton instance
reranker = RerankerService()
