#!/usr/bin/env python3
"""
Fast-start Flask App for AI-Powered Earnings Calendar
Serves the React frontend immediately using existing data, fetches news in background.
"""

import logging
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import json
import threading

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our analysis modules
import main

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app)

# Global state tracking
update_in_progress = False
last_update_time = None
last_error = None
data_ready = False

def quick_earnings_setup():
    """Quickly set up earnings data using existing files or basic earnings data"""
    global data_ready, last_update_time
    
    try:
        logger.info("Quick setup: Loading existing data...")
        
        # Check if we have existing earnings data
        earnings_file = 'earnings_news_urls.json'
        
        if os.path.exists(earnings_file):
            logger.info("Found existing earnings data, using cached data")
            data_ready = True
            last_update_time = datetime.now()
            return
        
        # If no existing data, create basic earnings data quickly
        logger.info("No existing data found, creating basic earnings structure...")
        
        # Get just the earnings data without news (fast)
        earnings_df, earnings_by_day, summary_stats = main.get_earnings_data(weeks_ahead=1)
        
        if earnings_df is not None:
            # Create basic structure with all companies but no articles yet
            companies = {}
            for date_str, day_data in earnings_by_day.items():
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                day_name = date_obj.strftime('%A')
                
                for symbol in day_data['symbols']:
                    companies[symbol] = {
                        "earnings_date": date_str,
                        "earnings_day": day_name,
                        "article_count": 0,
                        "urls": [],
                        "article_details": []
                    }
            
            # Save basic structure
            earnings_data = {
                "earnings_week": f"{min(earnings_by_day.keys())} to {max(earnings_by_day.keys())}",
                "generated_at": datetime.now().isoformat(),
                "companies": companies
            }
            
            with open(earnings_file, 'w', encoding='utf-8') as f:
                json.dump(earnings_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created basic earnings structure with {len(companies)} companies")
            data_ready = True
            last_update_time = datetime.now()
            
    except Exception as e:
        logger.error(f"Error in quick setup: {e}")
        data_ready = False

def background_news_fetch():
    """Fetch news articles in background thread"""
    global update_in_progress, last_update_time, last_error
    
    if update_in_progress:
        return
    
    try:
        update_in_progress = True
        logger.info("Background: Starting news article fetch...")
        
        # Run full analysis with news fetching
        result = main.run_full_analysis(weeks_ahead=1, run_sentiment=False)
        
        if result["success"]:
            last_update_time = datetime.now()
            last_error = None
            logger.info(f"Background news fetch completed at {last_update_time}")
        else:
            error_msg = result.get("error", "Unknown error during news fetch")
            logger.error(error_msg)
            last_error = error_msg

    except Exception as e:
        error_msg = f"Exception during news fetch: {e}"
        logger.error(error_msg)
        last_error = error_msg
    finally:
        update_in_progress = False

# API Routes
@app.route('/api/status')
def api_status():
    """API health check endpoint"""
    return jsonify({
        "status": "running",
        "data_ready": data_ready,
        "last_update": last_update_time.isoformat() if last_update_time else None,
        "update_in_progress": update_in_progress,
        "last_error": last_error
    })

@app.route('/api/earnings')
def api_earnings():
    """Get earnings data"""
    try:
        earnings_file = 'earnings_news_urls.json'
        if os.path.exists(earnings_file):
            with open(earnings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({"error": "No earnings data available"}), 404
    except Exception as e:
        logger.error(f"Error loading earnings data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sentiment')
def api_sentiment():
    """Get sentiment analysis data"""
    try:
        sentiment_file = 'earnings_sentiment_analysis.json'
        if os.path.exists(sentiment_file):
            with open(sentiment_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            # Return neutral sentiment for all companies if no sentiment data
            earnings_file = 'earnings_news_urls.json'
            if os.path.exists(earnings_file):
                with open(earnings_file, 'r', encoding='utf-8') as f:
                    earnings_data = json.load(f)
                
                companies = earnings_data.get('companies', {})
                sentiment_results = []
                for ticker in companies.keys():
                    sentiment_results.append({
                        "ticker": ticker,
                        "sentiment_score": 0,
                        "articles_analyzed": 0,
                        "total_articles_available": companies[ticker].get('article_count', 0)
                    })
                
                neutral_data = {
                    "analysis_timestamp": datetime.now().isoformat(),
                    "earnings_week": earnings_data.get('earnings_week', ''),
                    "total_companies_analyzed": len(companies),
                    "sentiment_results": sentiment_results
                }
                return jsonify(neutral_data)
            else:
                return jsonify({"error": "No data available"}), 404
    except Exception as e:
        logger.error(f"Error loading sentiment data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/company/<ticker>')
def api_company_search(ticker):
    """Search for a specific company by ticker"""
    try:
        earnings_file = 'earnings_news_urls.json'
        sentiment_file = 'earnings_sentiment_analysis.json'
        
        if not os.path.exists(earnings_file):
            return jsonify({"error": "No earnings data available"}), 404
            
        with open(earnings_file, 'r', encoding='utf-8') as f:
            earnings_data = json.load(f)
        
        companies = earnings_data.get('companies', {})
        ticker_upper = ticker.upper()
        
        if ticker_upper not in companies:
            return jsonify({"error": f"Company {ticker_upper} not found in this week's earnings schedule"}), 404
        
        company_info = companies[ticker_upper]
        
        # Load sentiment data if available
        sentiment_score = 0
        articles_analyzed = 0
        
        if os.path.exists(sentiment_file):
            try:
                with open(sentiment_file, 'r', encoding='utf-8') as f:
                    sentiment_data = json.load(f)
                
                sentiment_results = sentiment_data.get('sentiment_results', [])
                for result in sentiment_results:
                    if result.get('ticker') == ticker_upper:
                        sentiment_score = result.get('sentiment_score', 0)
                        articles_analyzed = result.get('articles_analyzed', 0)
                        break
            except Exception as e:
                logger.warning(f"Could not load sentiment data: {e}")
        
        response_data = {
            "ticker": ticker_upper,
            "earnings_date": company_info.get('earnings_date'),
            "earnings_day": company_info.get('earnings_day'),
            "article_count": company_info.get('article_count', 0),
            "urls": company_info.get('urls', []),
            "sentiment_score": sentiment_score,
            "articles_analyzed": articles_analyzed,
            "analysis_timestamp": datetime.now().isoformat(),
            "earnings_week": earnings_data.get('earnings_week', ''),
            "found": True
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error searching for company {ticker}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/companies')
def api_companies_list():
    """Get list of all companies with their data"""
    try:
        earnings_file = 'earnings_news_urls.json'
        sentiment_file = 'earnings_sentiment_analysis.json'
        
        if not os.path.exists(earnings_file):
            return jsonify({"error": "No earnings data available"}), 404
            
        with open(earnings_file, 'r', encoding='utf-8') as f:
            earnings_data = json.load(f)
        
        companies = earnings_data.get('companies', {})
        
        # Load sentiment data if available
        sentiment_map = {}
        if os.path.exists(sentiment_file):
            try:
                with open(sentiment_file, 'r', encoding='utf-8') as f:
                    sentiment_data = json.load(f)
                
                sentiment_results = sentiment_data.get('sentiment_results', [])
                for result in sentiment_results:
                    ticker = result.get('ticker')
                    if ticker:
                        sentiment_map[ticker] = {
                            'sentiment_score': result.get('sentiment_score', 0),
                            'articles_analyzed': result.get('articles_analyzed', 0)
                        }
            except Exception as e:
                logger.warning(f"Could not load sentiment data: {e}")
        
        companies_list = []
        for ticker, company_info in companies.items():
            sentiment_info = sentiment_map.get(ticker, {'sentiment_score': 0, 'articles_analyzed': 0})
            
            company_data = {
                "ticker": ticker,
                "earnings_date": company_info.get('earnings_date'),
                "earnings_day": company_info.get('earnings_day'),
                "article_count": company_info.get('article_count', 0),
                "sentiment_score": sentiment_info['sentiment_score'],
                "articles_analyzed": sentiment_info['articles_analyzed']
            }
            companies_list.append(company_data)
        
        response_data = {
            "earnings_week": earnings_data.get('earnings_week', ''),
            "total_companies": len(companies_list),
            "companies": companies_list,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error loading companies list: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/trigger-update')
def api_trigger_update():
    """Manually trigger a news fetch"""
    if update_in_progress:
        return jsonify({"status": "update already in progress"}), 409
    
    try:
        # Start background news fetch
        threading.Thread(target=background_news_fetch, daemon=True).start()
        return jsonify({"status": "news fetch started in background"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# React frontend routes
@app.route('/')
def serve_react_app():
    """Serve the React application"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.warning(f"Could not serve from dist folder: {e}")
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI-Powered Earnings Calendar</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #0a0a0a; color: #fff; }
                .container { max-width: 800px; margin: 0 auto; }
                .status { padding: 20px; background: #1a1a1a; border-radius: 8px; border: 1px solid #333; }
                .search-box { margin: 20px 0; padding: 15px; background: #1a1a1a; border-radius: 8px; border: 1px solid #333; }
                input { background: #000; color: #fff; border: 1px solid #444; padding: 10px; border-radius: 4px; width: 300px; }
                button { background: #0066cc; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; margin-left: 10px; cursor: pointer; }
                button:hover { background: #0052a3; }
                .company-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
                .company-card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 15px; }
                .company-ticker { font-weight: bold; color: #00ff88; font-size: 18px; }
                .company-date { color: #aaa; font-size: 14px; }
                .article-count { color: #ffa500; font-size: 12px; }
                a { color: #0066cc; text-decoration: none; }
                a:hover { text-decoration: underline; }
                h1 { text-align: center; color: #00ff88; }
                h2 { color: #0066cc; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 AI-Powered Earnings Calendar</h1>
                
                <div class="status">
                    <h2>🚀 System Status</h2>
                    <p>✅ Flask backend running</p>
                    <p>📊 API endpoints available:</p>
                    <ul>
                        <li><a href="/api/status">/api/status</a> - System health</li>
                        <li><a href="/api/earnings">/api/earnings</a> - Earnings data</li>
                        <li><a href="/api/sentiment">/api/sentiment</a> - Sentiment analysis</li>
                        <li><a href="/api/companies">/api/companies</a> - All companies list</li>
                    </ul>
                </div>

                <div class="search-box">
                    <h2>🔍 Company Search</h2>
                    <p>Search for any company by ticker symbol:</p>
                    <input type="text" id="searchInput" placeholder="Enter ticker (e.g., MU, COST, ACN)" onkeypress="if(event.key==='Enter') searchCompany()">
                    <button onclick="searchCompany()">Search</button>
                    <div id="searchResult" style="margin-top: 15px;"></div>
                </div>

                <div class="status">
                    <h2>📈 Featured Companies This Week</h2>
                    <div class="company-grid">
                        <div class="company-card">
                            <div class="company-ticker">MU</div>
                            <div class="company-date">Tuesday, Sep 23</div>
                            <div class="article-count">Memory Technology</div>
                        </div>
                        <div class="company-card">
                            <div class="company-ticker">COST</div>
                            <div class="company-date">Thursday, Sep 25</div>
                            <div class="article-count">Costco Wholesale</div>
                        </div>
                        <div class="company-card">
                            <div class="company-ticker">ACN</div>
                            <div class="company-date">Thursday, Sep 25</div>
                            <div class="article-count">Accenture</div>
                        </div>
                        <div class="company-card">
                            <div class="company-ticker">KBH</div>
                            <div class="company-date">Wednesday, Sep 24</div>
                            <div class="article-count">KB Home</div>
                        </div>
                    </div>
                </div>

                <div class="status">
                    <p>🔄 <strong>Background Updates:</strong> News articles are being fetched automatically</p>
                    <p>⚠️ <strong>Note:</strong> Sentiment analysis is disabled to avoid API rate limits</p>
                    <p>🌐 <strong>Data Sources:</strong> Dolthub (earnings), Finnhub (news)</p>
                </div>
            </div>

            <script>
                async function searchCompany() {
                    const input = document.getElementById('searchInput');
                    const result = document.getElementById('searchResult');
                    const ticker = input.value.trim().toUpperCase();
                    
                    if (!ticker) {
                        result.innerHTML = '<p style="color: red;">Please enter a ticker symbol</p>';
                        return;
                    }
                    
                    result.innerHTML = '<p style="color: #aaa;">Searching...</p>';
                    
                    try {
                        const response = await fetch(`/api/company/${ticker}`);
                        const data = await response.json();
                        
                        if (response.ok) {
                            result.innerHTML = `
                                <div style="background: #0a2a0a; border: 1px solid #00ff88; border-radius: 8px; padding: 15px; margin-top: 10px;">
                                    <h3 style="color: #00ff88; margin: 0 0 10px 0;">${data.ticker}</h3>
                                    <p><strong>Earnings Date:</strong> ${data.earnings_day}, ${data.earnings_date}</p>
                                    <p><strong>News Articles:</strong> ${data.article_count}</p>
                                    <p><strong>Sentiment Score:</strong> ${data.sentiment_score}</p>
                                    <p><strong>Articles Analyzed:</strong> ${data.articles_analyzed}</p>
                                    <p style="font-size: 12px; color: #aaa;">Week: ${data.earnings_week}</p>
                                </div>
                            `;
                        } else {
                            result.innerHTML = `<p style="color: red;">${data.error}</p>`;
                        }
                    } catch (error) {
                        result.innerHTML = '<p style="color: red;">Error connecting to server</p>';
                    }
                }
            </script>
        </body>
        </html>
        """)

@app.route('/<path:path>')
def serve_react_static(path):
    """Serve React static files"""
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return serve_react_app()

if __name__ == '__main__':
    logger.info("Starting fast Flask application...")
    
    # Quick setup first
    quick_earnings_setup()
    
    # Set up background scheduler for news updates
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=background_news_fetch,
        trigger=IntervalTrigger(hours=2),  # Every 2 hours
        id='news_update',
        name='Update news articles every 2 hours',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Background scheduler started - will update news every 2 hours")
    
    # Start initial background news fetch
    if data_ready:
        logger.info("Starting background news fetch...")
        threading.Thread(target=background_news_fetch, daemon=True).start()
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    # Start the Flask development server
    app.run(host='127.0.0.1', port=5000, debug=False)