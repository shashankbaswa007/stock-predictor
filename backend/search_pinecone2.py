from services.vector_store import get_vector_store
store = get_vector_store()
print(store.similarity_search("Apple latest news", k=5))
