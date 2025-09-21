#!/usr/bin/env python3
"""
Simple Flask App for AI-Powered Earnings Calendar
Serves the React frontend and provides API endpoints for earnings data.
Skips sentiment analysis to avoid rate limits.
"""

import logging
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template_string, send_from_directory, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import json

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

def run_earnings_update():
    """Update earnings data and fetch news articles"""
    global update_in_progress, last_update_time, last_error
    
    if update_in_progress:
        logger.warning("Update already in progress, skipping this cycle")
        return
    
    try:
        update_in_progress = True
        logger.info("Starting scheduled earnings data update...")
        
        # Run FULL analysis including news fetching, but skip sentiment analysis to avoid rate limits
        # This will ensure we get all the news articles for companies
        result = main.run_full_analysis(weeks_ahead=1, run_sentiment=False)
        
        if result["success"]:
            # Update success tracking
            last_update_time = datetime.now()
            last_error = None
            logger.info(f"Earnings update completed successfully at {last_update_time}")
        else:
            # Handle failure
            error_msg = result.get("error", "Unknown error during analysis")
            logger.error(error_msg)
            last_error = error_msg

    except Exception as e:
        error_msg = f"Exception during earnings update: {e}"
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
        "last_update": last_update_time.isoformat() if last_update_time else None,
        "update_in_progress": update_in_progress,
        "last_error": last_error
    })

@app.route('/api/earnings')
def api_earnings():
    """Get earnings data"""
    try:
        # Load earnings data from JSON file
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
        # Load sentiment data from JSON file
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
                
                # Create neutral sentiment for all companies
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

@app.route('/api/trigger-update')
def api_trigger_update():
    """Manually trigger an earnings data update"""
    if update_in_progress:
        return jsonify({"status": "update already in progress"}), 409
    
    try:
        # Run update in background
        run_earnings_update()
        return jsonify({"status": "update triggered"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/company/<ticker>')
def api_company_search(ticker):
    """Search for a specific company by ticker and optionally fetch fresh data"""
    try:
        ticker_upper = ticker.upper()
        
        # Check if we should fetch fresh data for this ticker
        fetch_fresh = request.args.get('fetch', 'false').lower() == 'true'
        
        if fetch_fresh and not update_in_progress:
            logger.info(f"🎯 Fetching fresh data for {ticker_upper}")
            try:
                # Run analysis for specific ticker
                result = main.run_full_analysis(weeks_ahead=1, run_sentiment=False, specific_ticker=ticker_upper)
                if not result["success"]:
                    logger.error(f"Failed to fetch data for {ticker_upper}: {result.get('error')}")
            except Exception as e:
                logger.error(f"Error fetching fresh data for {ticker_upper}: {e}")
        
        # Load earnings data from JSON file
        earnings_file = 'earnings_news_urls.json'
        sentiment_file = 'earnings_sentiment_analysis.json'
        
        if not os.path.exists(earnings_file):
            return jsonify({"error": "No earnings data available"}), 404
            
        # Load earnings data
        with open(earnings_file, 'r', encoding='utf-8') as f:
            earnings_data = json.load(f)
        
        companies = earnings_data.get('companies', {})
        
        # Find the company
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
        
        # Return comprehensive company data
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
        # Load earnings data from JSON file
        earnings_file = 'earnings_news_urls.json'
        sentiment_file = 'earnings_sentiment_analysis.json'
        
        if not os.path.exists(earnings_file):
            return jsonify({"error": "No earnings data available"}), 404
            
        # Load earnings data
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
        
        # Combine earnings and sentiment data
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

# React frontend routes
@app.route('/')
def serve_react_app():
    """Serve the React application"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        # Fallback if dist folder doesn't exist
        logger.warning(f"Could not serve from dist folder: {e}")
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI-Powered Earnings Calendar</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .status { padding: 20px; background: #f0f0f0; border-radius: 8px; }
            </style>
        </head>
        <body>
            <h1>AI-Powered Earnings Calendar</h1>
            <div class="status">
                <h2>Backend Status</h2>
                <p>✅ Flask server is running</p>
                <p>📊 API endpoints available at:</p>
                <ul>
                    <li><a href="/api/status">/api/status</a></li>
                    <li><a href="/api/earnings">/api/earnings</a></li>
                    <li><a href="/api/sentiment">/api/sentiment</a></li>
                </ul>
                <p>🔄 Earnings data updates every hour</p>
                <p>⚠️ Sentiment analysis disabled to avoid rate limits</p>
            </div>
        </body>
        </html>
        """)

@app.route('/<path:path>')
def serve_react_static(path):
    """Serve React static files"""
    try:
        return send_from_directory(app.static_folder, path)
    except:
        # Fallback to index.html for client-side routing
        return serve_react_app()

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    
    # Set up background scheduler for hourly updates
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=run_earnings_update,
        trigger=IntervalTrigger(hours=1),
        id='earnings_update',
        name='Update earnings data every hour',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Background scheduler started - will update earnings data every hour")
    logger.info("First earnings data update will run in 1 hour")
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    # Skip initial update - wait for the first scheduled run in 1 hour
    logger.info("Skipping initial update - first update will occur in 1 hour")
    
    # Start the Flask development server
    app.run(host='127.0.0.1', port=5000, debug=False)