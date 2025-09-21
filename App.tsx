import React, { useState, useMemo } from 'react';
import Header from './components/Header';
import EarningsCalendar from './components/EarningsCalendar';
import { SkeletonLoader } from './components/SkeletonLoader';
import { useEarningsData } from './hooks/useEarningsData';
import { Company, EarningsCalendarData, LiveAnalysisData } from './types';
import { DAYS_OF_WEEK } from './constants';
import { AnalysisModal } from './components/AnalysisModal';
import { LargeCompanyAnalysis } from './components/LargeCompanyAnalysis';

const App: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const { data, loading, error, refetch } = useEarningsData();

  // State for the large company analysis
  const [showLargeAnalysis, setShowLargeAnalysis] = useState(false);
  const [liveAnalysisResult, setLiveAnalysisResult] = useState<LiveAnalysisData | null>(null);
  const [isLiveAnalysisLoading, setIsLiveAnalysisLoading] = useState(false);
  const [liveAnalysisError, setLiveAnalysisError] = useState<string | null>(null);

  const allCompanies = useMemo(() => {
    if (!data) return [];
    const companies: Company[] = [];
    for (const day of DAYS_OF_WEEK) {
      const dayData = data[day as keyof EarningsCalendarData];
      if (dayData) {
        companies.push(...dayData);
      }
    }
    return Array.from(new Map(companies.map(c => [c.ticker, c])).values());
  }, [data]);

  const handleLiveAnalysis = async (symbol: string) => {
    if (!symbol) return;
    
    setShowLargeAnalysis(true);
    setIsLiveAnalysisLoading(true);
    setLiveAnalysisError(null);
    setLiveAnalysisResult(null);

    try {
      // Use our Flask backend to get the specific company's data with fresh fetch
      const apiUrl = (import.meta as any).env?.VITE_API_URL || '/api';
      const response = await fetch(`${apiUrl}/company/${encodeURIComponent(symbol.toUpperCase())}?fetch=true`);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`${symbol.toUpperCase()} is not reporting earnings this week. Try searching for a different company.`);
        }
        throw new Error(`Failed to fetch data for ${symbol.toUpperCase()}: ${response.status}`);
      }

      const company = await response.json();

      // Format the data for the modal
      const analysisData: LiveAnalysisData = {
        symbol: company.ticker,
        article_count: company.article_count || 0,
        sentiment_score: company.sentiment_score || 0,
        confidence: Math.abs(company.sentiment_score || 0) > 5 ? 'High' : Math.abs(company.sentiment_score || 0) > 2 ? 'Medium' : 'Low',
        analysis_date: company.analysis_timestamp || new Date().toISOString(),
        date_range: `Earnings on ${company.earnings_day}, ${company.earnings_date}`,
        sources: ['Finnhub Financial News API'],
        unique_sources: 1,
        articles_analyzed: company.articles_analyzed || 0,
        total_articles_found: company.article_count || 0,
        reason: company.articles_analyzed > 0 
          ? `Sentiment analysis for ${company.ticker} based on ${company.articles_analyzed} articles analyzed from the past week.`
          : `No articles found for sentiment analysis. ${company.ticker} has ${company.article_count} news articles available but sentiment analysis is currently disabled due to API limits.`
      };

      setLiveAnalysisResult(analysisData);

    } catch (err) {
      if (err instanceof TypeError) { // Network error
        setLiveAnalysisError('Could not connect to the backend server. Please ensure the Flask server is running on http://localhost:5000.');
      } else if (err instanceof Error) {
        setLiveAnalysisError(err.message);
      } else {
        setLiveAnalysisError('An unknown error occurred during analysis.');
      }
    } finally {
      setIsLiveAnalysisLoading(false);
    }
  };


  return (
    <div className="min-h-screen font-sans">
      <div className="container mx-auto p-4 md:p-8">
        <h1 className="text-3xl font-bold text-center text-brand-primary mb-6">
          Stock Market News Sentiment Tracker
        </h1>
        <Header 
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          allCompanies={allCompanies}
          onLiveAnalysis={handleLiveAnalysis}
        />
        <main className="mt-8">
          {loading ? (
            <SkeletonLoader />
          ) : error ? (
            <div className="flex flex-col items-center justify-center text-center p-8 bg-brand-surface/80 backdrop-blur-sm border border-brand-border rounded-lg">
                <p className="text-red-400 text-lg mb-4">
                  {error}
                </p>
                <button 
                  onClick={refetch}
                  className="px-6 py-2 bg-brand-border text-brand-text font-semibold rounded-lg hover:bg-brand-surface transition-colors"
                >
                  Try Again
                </button>
            </div>
          ) : (
            <EarningsCalendar 
              data={data}
              searchTerm={searchTerm}
            />
          )}
        </main>
      </div>
      
      {/* Large Company Analysis Display */}
      {showLargeAnalysis && (
        <div>
          {isLiveAnalysisLoading && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Analyzing Company...</h3>
                  <p className="text-gray-600">Fetching latest news and sentiment data</p>
                </div>
              </div>
            </div>
          )}
          
          {liveAnalysisError && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">
                <div className="text-center">
                  <div className="text-red-500 text-4xl mb-4">⚠️</div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Analysis Error</h3>
                  <p className="text-gray-600 mb-4">{liveAnalysisError}</p>
                  <button
                    onClick={() => setShowLargeAnalysis(false)}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {liveAnalysisResult && !isLiveAnalysisLoading && !liveAnalysisError && (
            <LargeCompanyAnalysis
              company={liveAnalysisResult}
              onClose={() => setShowLargeAnalysis(false)}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default App;