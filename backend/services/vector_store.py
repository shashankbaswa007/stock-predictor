"""
vector_store.py — Pinecone Vector Database for RAG (Phase 7)
============================================================
Manages a Pinecone Serverless vector database.
Uses HuggingFace embeddings (384 dimensions).
Automatically creates the index if it doesn't exist.
"""

import os
from typing import List, Dict
import time
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from config import settings
from services.mock_data import generate_10k_excerpts, generate_news

# Use HuggingFace embeddings (384 dims for all-MiniLM-L6-v2)
_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Global singleton for the vector store
_vector_store = None

def _initialize_store():
    """Connect to Pinecone, create index if missing, and return the store."""
    global _vector_store
    
    if not settings.pinecone_api_key:
        print("WARNING: No PINECONE_API_KEY found. RAG will fail.")
        return
        
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index_name = settings.pinecone_index_name
    
    # Check if index exists, create if not
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        print(f"Creating Pinecone index '{index_name}'... This may take a moment.")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws", 
                region="us-east-1"
            )
        )
        # Wait for index to be ready
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
            
        print("Index created successfully. Populating initial data...")
        # Pre-populate with a few core tickers
        docs: List[Document] = []
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
                
            # Load actual News Headlines
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
                
        # Initialize and populate store
        if docs:
            _vector_store = PineconeVectorStore.from_documents(
                docs, 
                _embeddings, 
                index_name=index_name,
                pinecone_api_key=settings.pinecone_api_key
            )
        else:
            _vector_store = PineconeVectorStore(index_name=index_name, embedding=_embeddings, pinecone_api_key=settings.pinecone_api_key)
    else:
        # Index already exists, just connect
        _vector_store = PineconeVectorStore(index_name=index_name, embedding=_embeddings, pinecone_api_key=settings.pinecone_api_key)


def get_vector_store() -> PineconeVectorStore:
    """Get the initialized Pinecone vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _initialize_store()
    return _vector_store


def retrieve_context(query: str, ticker: str, k: int = 3) -> List[Dict]:
    """
    Retrieve top-k most relevant documents for a given query and ticker.
    """
    store = get_vector_store()
    if not store:
        return []
        
    # Filter by ticker (Pinecone metadata filtering)
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
