from services.vector_store import populate_vector_store, get_vector_store
from services.mock_data import generate_news, get_company_profile
import asyncio

async def main():
    print("Fetching AAPL news...")
    news = await generate_news("AAPL")
    
    print("Fetching AAPL profile...")
    profile = await get_company_profile("AAPL")

    docs = []
    
    # 1. 10-K Mock (Profile info)
    desc = profile.get("description", "Apple Inc. designs, manufactures, and markets smartphones...")
    docs.append({
        "text": f"Apple (AAPL) Business Overview: {desc}. Industry: {profile.get('finnhubIndustry')}",
        "metadata": {"ticker": "AAPL", "source": "10-K_Mock"}
    })

    # 2. News Docs
    for article in news.get("articles", []):
        docs.append({
            "text": f"Headline: {article['headline']}. Summary: {article['summary']}",
            "metadata": {"ticker": "AAPL", "source": "News", "date": article['published_at']}
        })
    
    print(f"Populating Pinecone with {len(docs)} documents...")
    populate_vector_store(docs)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
