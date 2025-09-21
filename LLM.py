import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client with environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")

client = Groq(api_key=GROQ_API_KEY)

def analyze_sentiment_for_company(company_data, ticker):
    """
    Analyze sentiment for a single company based on ALL article headlines and sources
    """
    # Get article details
    articles = company_data.get('article_details', [])
    
    if not articles:
        return {"ticker": ticker, "sentiment_score": 0, "articles_analyzed": 0}
    
    print(f"  📰 Analyzing ALL {len(articles)} article headlines for {ticker}...")
    
    # Prepare ALL articles for analysis (not just first 15)
    article_info = []
    for i, article in enumerate(articles, 1):  # Process ALL articles
        headline = article.get('headline', 'No headline')
        source = article.get('source', 'Unknown source')
        datetime_val = article.get('datetime', 0)
        
        if headline and headline != 'No headline':
            article_info.append({
                'number': i,
                'headline': headline,
                'source': source,
                'datetime': datetime_val
            })
    
    if not article_info:
        print(f"  ❌ No valid articles found for {ticker}")
        return {"ticker": ticker, "sentiment_score": 0, "articles_analyzed": 0}
    
    # Create comprehensive headline analysis prompt
    articles_list = []
    for article in article_info:
        articles_list.append(f"{article['number']}. {article['headline']} ({article['source']})")
    
    articles_text = "\n".join(articles_list)
    
    user_content = f"""
COMPANY FOR SENTIMENT ANALYSIS: {ticker}
EARNINGS DATE: {company_data.get('earnings_date', 'Unknown')}
EARNINGS DAY: {company_data.get('earnings_day', 'Unknown')}
TOTAL ARTICLES: {len(article_info)}

Analyze the sentiment toward {ticker} based on these {len(article_info)} news article headlines:

{articles_text}

ANALYSIS INSTRUCTIONS:
1. Analyze EVERY headline for sentiment indicators toward {ticker}
2. Look for positive keywords: growth, beat, strong, up, gains, bullish, upgrade, buy, outperform, exceeds, positive, rally, surge
3. Look for negative keywords: loss, miss, down, decline, falls, bearish, downgrade, sell, underperform, concerns, drops, plunge
4. Consider source credibility (Yahoo, MarketWatch, SeekingAlpha more reliable than unknown sources)
5. Weight earnings-related news more heavily than general market news
6. Consider overall volume of coverage (more articles = more market attention)

SENTIMENT SCORING GUIDELINES:
- Very Positive (+8 to +10): Multiple positive headlines, earnings beats, strong growth mentions, bullish analyst coverage
- Positive (+4 to +7): More positive than negative headlines, meeting expectations, favorable trends
- Slightly Positive (+1 to +3): Mild positive indicators, stable outlook, neutral-to-good news
- Neutral (0): Mixed headlines that balance out, or purely factual reporting
- Slightly Negative (-1 to -3): Mild concerns, cautious outlook, some disappointing news
- Negative (-4 to -7): More negative headlines, missing expectations, bearish sentiment
- Very Negative (-8 to -10): Predominantly negative headlines, major problems, very poor outlook

IMPORTANT: Analyze based ONLY on the headlines provided. Return only a single integer from -10 to +10.
"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert financial news sentiment analyst. Analyze sentiment based on news headlines and sources.

You must provide nuanced, realistic sentiment scores that reflect the actual tone of the headlines. Do NOT default to neutral (0) unless the headlines truly have no sentiment bias.

ANALYSIS PROCESS:
1. Read every headline carefully for sentiment indicators
2. Identify positive/negative keywords and phrases
3. Consider the overall tone and implications
4. Weight based on source credibility and article volume
5. Provide a meaningful sentiment score that reflects reality

SCORING REQUIREMENTS:
- Use the full range from -10 to +10
- Be specific and granular in your scoring
- Positive headlines should get positive scores
- Negative headlines should get negative scores
- Only use 0 for truly neutral or perfectly balanced coverage

Return only a single integer from -10 to +10."""
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            model="llama-3.1-8b-instant"
        )
        
        # Get the response text directly (no web browsing tools)
        response_text = chat_completion.choices[0].message.content
        if response_text:
            response_text = response_text.strip()
        else:
            response_text = "0"
        
        print(f"  💬 LLM response: {response_text[:100]}..." if len(response_text) > 100 else f"  💬 LLM response: {response_text}")
        
        # Try to extract the sentiment score from the response
        import re
        score_match = re.search(r'[+-]?\d+', response_text)
        if score_match:
            score = int(score_match.group())
            # Clamp between -10 and 10
            score = max(-10, min(10, score))
        else:
            # If no number found, try to infer from text
            response_lower = response_text.lower()
            if any(word in response_lower for word in ['positive', 'bullish', 'strong', 'good', 'up', 'gain']):
                score = 3  # Default positive
            elif any(word in response_lower for word in ['negative', 'bearish', 'weak', 'bad', 'down', 'loss']):
                score = -3  # Default negative
            else:
                score = 0
            
        print(f"  🤖 LLM analyzed {len(article_info)} headlines and returned score: {score:+d}")
            
        return {
            "ticker": ticker, 
            "sentiment_score": score,
            "articles_analyzed": len(article_info),
            "total_articles_available": len(articles)
        }
        
    except Exception as e:
        print(f"  ❌ Error analyzing {ticker}: {str(e)}")
        return {
            "ticker": ticker, 
            "sentiment_score": 0,
            "articles_analyzed": 0,
            "total_articles_available": len(articles)
        }

def process_earnings_sentiment(json_filename="earnings_news_urls.json"):
    """
    Process all companies from the earnings JSON file and calculate sentiment scores
    """
    print(f"Loading earnings data from {json_filename}...")
    
    # Load the earnings data
    with open(json_filename, 'r', encoding='utf-8') as f:
        earnings_data = json.load(f)
    
    companies = earnings_data.get('companies', {})
    print(f"Found {len(companies)} companies to analyze")
    
    sentiment_results = []
    
    # Filter companies with articles for deep analysis
    companies_with_articles = {ticker: data for ticker, data in companies.items() 
                             if data.get('article_count', 0) > 0}
    
    print(f"Companies with articles for deep analysis: {len(companies_with_articles)}")
    print(f"Companies without articles (will receive neutral score): {len(companies) - len(companies_with_articles)}")
    
    for i, (ticker, company_data) in enumerate(companies.items(), 1):
        print(f"\n🔍 Analyzing {ticker}... ({i}/{len(companies)})")
        
        if company_data.get('article_count', 0) == 0:
            print(f"  📄 No articles found for {ticker}, assigning neutral score")
            result = {
                "ticker": ticker, 
                "sentiment_score": 0,
                "articles_analyzed": 0,
                "total_articles_available": 0
            }
        else:
            # Perform deep analysis with full article content
            result = analyze_sentiment_for_company(company_data, ticker)
        
        sentiment_results.append(result)
        
        print(f"  📊 Final score for {ticker}: {result['sentiment_score']:+d}")
        
        # Add delay to be respectful to APIs
        time.sleep(2)
    
    # Save results to file
    output_filename = "earnings_sentiment_analysis.json"
    output_data = {
        "analysis_date": earnings_data.get('generated_at'),
        "earnings_week": earnings_data.get('earnings_week'),
        "total_companies_analyzed": len(sentiment_results),
        "sentiment_results": sentiment_results
    }
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Calculate analysis statistics
    total_articles_fetched = sum(r.get('articles_fetched', 0) for r in sentiment_results)
    total_articles_analyzed = sum(r.get('articles_analyzed', 0) for r in sentiment_results)
    companies_with_data = len([r for r in sentiment_results if r.get('articles_analyzed', 0) > 0])
    
    print(f"\n✅ Deep sentiment analysis complete!")
    print(f"📊 Companies analyzed: {len(sentiment_results)}")
    print(f"📰 Companies with article content: {companies_with_data}")
    print(f"📥 Total articles fetched: {total_articles_fetched}")
    print(f"� Total articles analyzed: {total_articles_analyzed}")
    print(f"�💾 Results saved to '{output_filename}'")
    
    # Print detailed summary
    print("\n" + "="*80)
    print("DEEP SENTIMENT ANALYSIS RESULTS")
    print("="*80)
    
    # Sort by sentiment score
    sorted_results = sorted(sentiment_results, key=lambda x: x['sentiment_score'], reverse=True)
    
    print(f"\n🟢 MOST POSITIVE SENTIMENT:")
    for result in sorted_results[:10]:
        if result['sentiment_score'] > 0:
            articles_info = f"({result.get('articles_analyzed', 0)} articles analyzed)" if result.get('articles_analyzed', 0) > 0 else "(no articles)"
            print(f"  {result['ticker']}: {result['sentiment_score']:+d} {articles_info}")
    
    print(f"\n🔴 MOST NEGATIVE SENTIMENT:")
    negative_results = [r for r in sorted_results if r['sentiment_score'] < 0]
    for result in negative_results[-10:]:
        articles_info = f"({result.get('articles_analyzed', 0)} articles analyzed)" if result.get('articles_analyzed', 0) > 0 else "(no articles)"
        print(f"  {result['ticker']}: {result['sentiment_score']:+d} {articles_info}")
    
    print(f"\n📊 NEUTRAL (0 score): {len([r for r in sentiment_results if r['sentiment_score'] == 0])} companies")
    print(f"📈 ANALYSIS DEPTH: {total_articles_analyzed} full articles word-by-word analyzed")
    
    return {result['ticker']: result for result in sentiment_results}

if __name__ == "__main__":
    """
    Test the Groq API with a simple example first
    """
    print("Testing Groq API connection...")
    
    try:
        # Test API connection
        test_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Explain the importance of fast language models in one sentence.",
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        print("✅ Groq API connection successful!")
        print(f"Response: {test_completion.choices[0].message.content}")
        print()
        
    except Exception as e:
        print(f"❌ Error connecting to Groq API: {e}")
        print("Please check your API key and internet connection.")
        exit(1)
    
    # Process earnings sentiment analysis
    try:
        print("Starting earnings sentiment analysis...")
        results = process_earnings_sentiment()
        print("\n🎉 Analysis completed successfully!")
        
    except FileNotFoundError:
        print("❌ earnings_news_urls.json not found. Please run main.py first to generate the data.")
    except Exception as e:
        print(f"❌ Error during sentiment analysis: {e}")
