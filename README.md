# 🏆 AI-Powered Earnings Calendar

**Winner-Ready Hackathon Project** - An intelligent earnings calendar that combines real-time financial data with AI-powered sentiment analysis to help investors make smarter decisions.

🎯 **The Problem**: Investors struggle to track earnings and gauge market sentiment across multiple sources.

💡 **Our Solution**: One platform that aggregates earnings data and uses AI to analyze news sentiment in real-time.

## 🚀 Key Features

- **🤖 AI Sentiment Analysis**: Groq LLM analyzes thousands of news articles per company
- **� Live Earnings Data**: Real-time earnings calendar with 57+ companies
- **🔍 Smart Search**: Instant company lookup with detailed analysis
- **📱 Responsive Design**: Works perfectly on mobile and desktop
- **⚡ Real-time Updates**: Background scheduler updates data every hour
- **📈 Market Intelligence**: Comprehensive scoring based on 30+ days of news

## 🏗️ Architecture

### Backend (Flask + Python)
- **Flask API** - RESTful endpoints for data access
- **APScheduler** - Automated hourly data updates
- **Sentiment Analysis** - Groq LLM integration for news analysis
- **Data Sources** - Dolthub earnings calendar + Finnhub news APIs

### Frontend (React + TypeScript)
- **React 18** - Modern UI with hooks and context
- **TypeScript** - Type-safe development
- **Vite** - Fast development and building
- **Tailwind CSS** - Responsive styling

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+ 
- Node.js 16+
- npm or yarn

### 1. Clone and Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies  
npm install
```

### 2. Environment Setup

Copy the environment template:
```bash
cp .env.example .env.development
```

### 3. Start the Application

#### Option A: Full Development (Recommended)
```bash
# Start both backend and frontend in development mode
npm run dev:full
```

#### Option B: Backend Only
```bash
# Start Flask backend (serves both API and built frontend)
python app.py
```

#### Option C: Separate Development
```bash
# Terminal 1: Start Flask backend
python app.py

# Terminal 2: Start React development server
npm run dev
```

### 4. Build for Production

```bash
# Build React frontend
npm run build

# Start production server
python app.py
```

## 📡 API Endpoints

### Core Endpoints
- `GET /api/status` - Update status and scheduler info
- `GET /api/earnings` - Current earnings data
- `GET /api/sentiment` - Sentiment analysis results
- `GET /api/companies` - Companies with sentiment scores
- `POST /api/update` - Trigger manual data update

### Utility Endpoints
- `GET /api/health` - Health check
- `GET /api/logs` - Recent log entries
- `GET /api` - API documentation

## 🔧 Configuration

### Backend Configuration
- **Port**: 5000 (configurable in `app.py`)
- **Update Frequency**: Every hour (configurable in scheduler)
- **Data Sources**: Dolthub + Finnhub APIs
- **Log Files**: `flask_app.log`

### Frontend Configuration
- **Development Port**: 5173 (Vite default)
- **API Proxy**: Configured in `vite.config.ts`
- **Environment Variables**: `.env.development`

## 📊 Data Flow

1. **Scheduled Updates** (Every Hour)
   - Fetch earnings data from Dolthub
   - Collect news articles for reporting companies
   - Run sentiment analysis using Groq LLM
   - Save results to JSON files

2. **Frontend Display**
   - React app fetches data from Flask API
   - Interactive calendar shows companies by day
   - Sentiment scores displayed with color coding
   - Real-time status updates

## 🚀 Deployment

### Development
```bash
npm run dev:full
```
Access at: http://localhost:5173 (React dev server)

### Production
```bash
npm run build
python app.py
```
Access at: http://localhost:5000 (Flask serves everything)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**Backend not starting:**
- Ensure Python dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.9+)

**Frontend not loading:**
- Install Node dependencies: `npm install`
- Check Node version: `node --version` (requires 16+)

**API connection errors:**
- Ensure Flask backend is running on port 5000
- Check CORS configuration in `app.py`
- Verify proxy settings in `vite.config.ts`

**No data showing:**
- Wait for initial data update (runs automatically on startup)
- Trigger manual update: `POST /api/update`
- Check logs: `GET /api/logs`

### Support
For issues and questions, please check the logs at `/api/logs` or review the console output.
