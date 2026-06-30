"""
vector_store.py — Local FAISS Vector Database for RAG (Phase 5)
===============================================================
Manages a FAISS vector database stored locally.
Uses HuggingFace embeddings for 100% free offline embedding.
"""

import os
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

from services.mock_data import generate_10k_excerpts, generate_news

INDEX_PATH = "faiss_index"

# Use free HuggingFace embeddings (downloads model automatically on first run)
_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Global singleton for the in-memory store
_vector_store = None


def _initialize_store():
    """Load the FAISS store from disk, or create and save it if missing."""
    global _vector_store
    
    if os.path.exists(INDEX_PATH):
        try:
            _vector_store = FAISS.load_local(INDEX_PATH, _embeddings, allow_dangerous_deserialization=True)
            return
        except Exception as e:
            print(f"Failed to load FAISS index: {e}. Rebuilding...")

    docs: List[Document] = []
    
    # Pre-populate with a few core tickers
    tickers = ["AAPL", "NVDA", "MSFT"]
    
    for ticker in tickers:
        # Load generic company summaries
        excerpts = generate_10k_excerpts(ticker)
        for ex in excerpts:
            docs.append(
                Document(
                    page_content=ex["content"],
                    metadata={
                        "ticker": ticker,
                        "source": "10-K",
                        "section": ex["section"],
                        "fiscal_year": ex["fiscal_year"],
                        "doc_type": "fundamental"
                    }
                )
            )
            
        # Load actual News Headlines from DuckDuckGo
        news = generate_news(ticker, count=5)
        for article in news:
            docs.append(
                Document(
                    page_content=article["headline"],
                    metadata={
                        "ticker": ticker,
                        "source": article["source"],
                        "sentiment": article["sentiment"],
                        "published_at": article["published_at"],
                        "doc_type": "news"
                    }
                )
            )
            
    # Initialize FAISS with the real embeddings
    if docs:
        _vector_store = FAISS.from_documents(docs, _embeddings)
        _vector_store.save_local(INDEX_PATH)
    else:
        # Fallback empty store
        _vector_store = FAISS.from_texts(["Empty"], _embeddings)


def get_vector_store() -> FAISS:
    """Get the initialized FAISS vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _initialize_store()
    return _vector_store


def retrieve_context(query: str, ticker: str, k: int = 3) -> List[Dict]:
    """
    Retrieve top-k most relevant documents for a given query and ticker.
    """
    store = get_vector_store()
    
    # Filter by ticker
    filter_dict = {"ticker": ticker.upper()}
    
    # Perform similarity search
    results = store.similarity_search(query, k=k, filter=filter_dict)
    
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in results
    ]
