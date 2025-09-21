#!/usr/bin/env python3
"""
Test script to fetch fresh news data for MU using the same approach as your original code
"""

import finnhub
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
if not FINNHUB_API_KEY:
    raise ValueError("FINNHUB_API_KEY not found in environment variables. Please check your .env file.")

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

def test_mu_news():
    """Test fetching news for MU specifically"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Convert to required format (YYYY-MM-DD)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print(f"Fetching MU news from {start_str} to {end_str}")
    
    # Get company news for MU
    news = finnhub_client.company_news('MU', _from=start_str, to=end_str)
    
    if news:
        urls = []
        sources = set()
        
        for article in news:
            if 'url' in article and article['url']:
                urls.append({
                    'url': article['url'],
                    'headline': article.get('headline', 'No headline'),
                    'source': article.get('source', 'Unknown'),
                    'datetime': article.get('datetime', 0)
                })
                sources.add(article.get('source', 'Unknown'))
        
        print(f"MU: {len(urls)} articles found")
        print(f"Sources: {', '.join(sources)}")
        
        # Show first few headlines
        print("\nFirst 5 headlines:")
        for i, article in enumerate(urls[:5]):
            print(f"{i+1}. {article['headline']} ({article['source']})")
    else:
        print("No news found for MU")

if __name__ == "__main__":
    test_mu_news()