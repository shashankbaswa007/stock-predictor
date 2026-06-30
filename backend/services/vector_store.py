"""
vector_store.py — In-Memory FAISS Vector Database for RAG
=============================================================
Manages an ephemeral, in-memory FAISS vector database.
Populates it with the deterministic mock 10-K and news data from Phase 2.
Uses a mock embedder to keep development lightning fast and completely offline.
"""

from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings

from services.mock_data import generate_10k_excerpts, generate_news


# We use FakeEmbeddings in mock-first development so we don't need to download
# heavy ML models or burn OpenAI credits just to test the RAG architecture.
# The size 384 matches common small models like all-MiniLM-L6-v2.
_mock_embeddings = FakeEmbeddings(size=384)

# Global singleton for the in-memory store
_vector_store = None


def _initialize_store():
    """Create the FAISS store and pre-load it with data for a few tickers."""
    global _vector_store
    
    docs: List[Document] = []
    
    # Pre-populate with a few core tickers
    tickers = ["AAPL", "NVDA", "MSFT"]
    
    for ticker in tickers:
        # Load 10-K Excerpts
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
            
        # Load News Headlines
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
            
    # Initialize FAISS with the mock embeddings
    if docs:
        _vector_store = FAISS.from_documents(docs, _mock_embeddings)
    else:
        # Fallback empty store
        _vector_store = FAISS.from_texts(["Empty"], _mock_embeddings)


def get_vector_store() -> FAISS:
    """Get the initialized FAISS vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _initialize_store()
    return _vector_store


def retrieve_context(query: str, ticker: str, k: int = 3) -> List[Dict]:
    """
    Retrieve top-k most relevant documents for a given query and ticker.
    
    Args:
        query: The search query
        ticker: The stock ticker to filter by
        k: Number of documents to return
        
    Returns:
        List of dictionaries with content and metadata
    """
    store = get_vector_store()
    
    # Filter by ticker (FAISS supports simple metadata filtering)
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
