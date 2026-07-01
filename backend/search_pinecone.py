from services.vector_store import get_vector_store, retrieve_context
print(retrieve_context("Apple latest news", "AAPL", k=5))
