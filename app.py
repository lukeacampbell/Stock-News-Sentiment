from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import json
import os
import logging
from datetime import datetime
import atexit
import traceback

# Import our existing modules
import main
from LLM import process_earnings_sentiment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:5173'])  # Enable CORS for frontend integration

# Global variables to track update status
last_update_time = None
update_in_progress = False
last_error = None

def run_earnings_update():
    """
    Run the complete earnings data update and sentiment analysis
    """
    global last_update_time, update_in_progress, last_error
    
    if update_in_progress:
        logger.warning("Update already in progress, skipping this cycle")
        return
    
    try:
        update_in_progress = True
        logger.info("Starting scheduled earnings data update...")
        
        # Run the complete analysis pipeline
        # Skip sentiment analysis if we've hit rate limits recently
        try:
            result = main.run_full_analysis(weeks_ahead=1, run_sentiment=True)
        except Exception as e:
            if "rate_limit_exceeded" in str(e) or "429" in str(e):
                logger.warning("Rate limit exceeded, running without sentiment analysis")
                result = main.run_full_analysis(weeks_ahead=1, run_sentiment=False)
            else:
                raise
        
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
        error_msg = f"Error during earnings update: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        last_error = error_msg
    finally:
        update_in_progress = False

# Initialize scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(
    func=run_earnings_update,
    trigger=IntervalTrigger(hours=1),
    id='earnings_update_job',
    name='Update earnings data every hour',
    replace_existing=True
)

@app.route('/')
def serve_react():
    """
    Serve the React frontend
    """
    try:
        return send_file('dist/index.html')
    except FileNotFoundError:
        # If React build doesn't exist, return API info
        return jsonify({
            "message": "AI-Powered Earnings Calendar Backend",
            "version": "1.0.0",
            "status": "React frontend not built. Run 'npm run build' to build the frontend.",
            "endpoints": {
                "/api/status": "GET - Check update status",
                "/api/earnings": "GET - Get current earnings data", 
                "/api/sentiment": "GET - Get sentiment analysis results",
                "/api/update": "POST - Manually trigger data update"
            },
            "last_update": last_update_time.isoformat() if last_update_time else None,
            "update_in_progress": update_in_progress
        })

@app.route('/api')
def api_home():
    """
    API information endpoint
    """
    return jsonify({
        "message": "AI-Powered Earnings Calendar Backend API",
        "version": "1.0.0",
        "endpoints": {
            "/api/status": "GET - Check update status",
            "/api/earnings": "GET - Get current earnings data", 
            "/api/sentiment": "GET - Get sentiment analysis results",
            "/api/companies": "GET - Get companies with sentiment scores",
            "/api/logs": "GET - Recent log entries",
            "/api/update": "POST - Manually trigger data update"
        },
        "last_update": last_update_time.isoformat() if last_update_time else None,
        "update_in_progress": update_in_progress
    })

@app.route('/api/status')
def get_status():
    """
    Get the current status of the data updates
    """
    return jsonify({
        "last_update": last_update_time.isoformat() if last_update_time else None,
        "update_in_progress": update_in_progress,
        "last_error": last_error,
        "scheduler_running": scheduler.running,
        "next_update": "Every hour" if scheduler.running else "Scheduler not running"
    })

@app.route('/api/earnings')
def get_earnings():
    """
    Get current earnings data
    """
    try:
        if os.path.exists("earnings_news_urls.json"):
            with open("earnings_news_urls.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({"error": "No earnings data available"}), 404
    except Exception as e:
        logger.error(f"Error reading earnings data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sentiment')
def get_sentiment():
    """
    Get current sentiment analysis results
    """
    try:
        if os.path.exists("earnings_sentiment_analysis.json"):
            with open("earnings_sentiment_analysis.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({"error": "No sentiment analysis data available"}), 404
    except Exception as e:
        logger.error(f"Error reading sentiment data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/update', methods=['POST'])
def manual_update():
    """
    Manually trigger a data update
    """
    global update_in_progress
    
    if update_in_progress:
        return jsonify({"error": "Update already in progress"}), 409
    
    try:
        # Run update in background
        scheduler.add_job(
            func=run_earnings_update,
            trigger='date',
            id='manual_update',
            name='Manual earnings update',
            replace_existing=True
        )
        return jsonify({"message": "Manual update triggered successfully"})
    except Exception as e:
        logger.error(f"Error triggering manual update: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "scheduler": scheduler.running,
            "earnings_data": os.path.exists("earnings_news_urls.json"),
            "sentiment_data": os.path.exists("earnings_sentiment_analysis.json")
        }
    })

@app.route('/api/logs')
def get_logs():
    """
    Get recent log entries (last 50 lines)
    """
    try:
        if os.path.exists("flask_app.log"):
            with open("flask_app.log", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Return last 50 lines
                recent_logs = lines[-50:] if len(lines) > 50 else lines
                return jsonify({
                    "logs": [line.strip() for line in recent_logs],
                    "total_lines": len(lines)
                })
        else:
            return jsonify({"logs": [], "total_lines": 0})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/companies')
def get_companies():
    """
    Get list of companies with their earnings dates and sentiment scores
    """
    try:
        companies_data = []
        
        # Load earnings data
        earnings_data = {}
        if os.path.exists("earnings_news_urls.json"):
            with open("earnings_news_urls.json", 'r', encoding='utf-8') as f:
                earnings_data = json.load(f)
        
        # Load sentiment data
        sentiment_data = {}
        if os.path.exists("earnings_sentiment_analysis.json"):
            with open("earnings_sentiment_analysis.json", 'r', encoding='utf-8') as f:
                sentiment_json = json.load(f)
                # Convert to dict for easier lookup
                for result in sentiment_json.get("sentiment_results", []):
                    sentiment_data[result["ticker"]] = result
        
        # Combine data
        for ticker, company_info in earnings_data.get("companies", {}).items():
            sentiment_info = sentiment_data.get(ticker, {})
            
            companies_data.append({
                "ticker": ticker,
                "earnings_date": company_info.get("earnings_date"),
                "earnings_day": company_info.get("earnings_day"),
                "article_count": company_info.get("article_count", 0),
                "sentiment_score": sentiment_info.get("sentiment_score", 0),
                "articles_analyzed": sentiment_info.get("articles_analyzed", 0)
            })
        
        # Sort by sentiment score (highest first)
        companies_data.sort(key=lambda x: x["sentiment_score"], reverse=True)
        
        return jsonify({
            "companies": companies_data,
            "total_companies": len(companies_data),
            "earnings_week": earnings_data.get("earnings_week", "Unknown")
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Catch-all route for React Router
@app.route('/<path:path>')
def serve_react_routes(path):
    """
    Serve React routes (for client-side routing)
    """
    if path.startswith('api/'):
        # This is an API call that wasn't matched, return 404
        return jsonify({"error": "API endpoint not found"}), 404
    
    try:
        # Try to serve static file first
        return send_from_directory('dist', path)
    except FileNotFoundError:
        # If file not found, serve React app (for client-side routing)
        try:
            return send_file('dist/index.html')
        except FileNotFoundError:
            return jsonify({"error": "React frontend not built. Run 'npm run build' first."}), 404

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        
        # Start the scheduler
        scheduler.start()
        logger.info("Background scheduler started - will update earnings data every hour")
        
        # Run initial update
        logger.info("Running initial earnings data update...")
        run_earnings_update()
        
        # Ensure scheduler shuts down when the app exits
        atexit.register(lambda: scheduler.shutdown())
        
        # Start Flask development server
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error(traceback.format_exc())