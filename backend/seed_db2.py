from services.vector_store import get_vector_store
from services.mock_data import generate_news
from langchain_core.documents import Document

def main():
    store = get_vector_store()
    for ticker in ["AAPL", "NVDA", "MSFT"]:
        print(f"Fetching {ticker} news...")
        news_list = generate_news(ticker)
        
        docs = []
        # If it returns a dict wrapper
        if isinstance(news_list, dict):
            news_list = news_list.get("articles", [])
            
        for article in news_list:
            headline = article.get('headline', '')
            summary = article.get('summary', '')
            docs.append(Document(
                page_content=f"Headline: {headline}. Summary: {summary}",
                metadata={"ticker": ticker, "source": "News"}
            ))
        
        print(f"Populating Pinecone with {len(docs)} documents for {ticker}...")
        store.add_documents(docs)
        print(f"Done {ticker}!")

if __name__ == "__main__":
    main()
