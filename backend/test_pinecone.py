from config import settings
from pinecone import Pinecone
pc = Pinecone(api_key=settings.pinecone_api_key)
print(pc.list_indexes())
