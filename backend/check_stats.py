from config import settings
from pinecone import Pinecone
pc = Pinecone(api_key=settings.pinecone_api_key)
index = pc.Index(settings.pinecone_index_name)
print(index.describe_index_stats())
