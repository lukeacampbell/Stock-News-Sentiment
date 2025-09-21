import React from 'react';
import { LiveAnalysisData } from '../types';

interface LargeCompanyAnalysisProps {
  company: LiveAnalysisData;
  onClose: () => void;
}

export const LargeCompanyAnalysis: React.FC<LargeCompanyAnalysisProps> = ({ company, onClose }) => {
  const getSentimentColor = (score: number) => {
    if (score >= 5) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 1) return 'text-green-500 bg-green-50 border-green-100';
    if (score <= -5) return 'text-red-600 bg-red-50 border-red-200';
    if (score <= -1) return 'text-red-500 bg-red-50 border-red-100';
    return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  };

  const getSentimentLabel = (score: number) => {
    if (score >= 7) return 'Very Positive';
    if (score >= 4) return 'Positive';
    if (score >= 1) return 'Slightly Positive';
    if (score <= -7) return 'Very Negative';
    if (score <= -4) return 'Negative';
    if (score <= -1) return 'Slightly Negative';
    return 'Neutral';
  };

  const getSentimentIcon = (score: number) => {
    if (score >= 5) return '📈';
    if (score >= 1) return '👍';
    if (score <= -5) return '📉';
    if (score <= -1) return '👎';
    return '➖';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-xl">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold mb-2">{company.symbol}</h1>
              <p className="text-blue-100 text-lg">{company.date_range}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl font-bold p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
            >
              ×
            </button>
          </div>
        </div>

        {/* Main content */}
        <div className="p-8">
          {/* Sentiment Score - Large Display */}
          <div className="text-center mb-8">
            <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full border-4 ${getSentimentColor(company.sentiment_score)} mb-4`}>
              <div className="text-center">
                <div className="text-4xl mb-1">{getSentimentIcon(company.sentiment_score)}</div>
                <div className="text-3xl font-bold">{company.sentiment_score > 0 ? '+' : ''}{company.sentiment_score}</div>
              </div>
            </div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">
              {getSentimentLabel(company.sentiment_score)}
            </h2>
            <p className="text-gray-600">Sentiment Score</p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gray-50 rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">{company.article_count}</div>
              <div className="text-gray-700 font-medium">News Articles</div>
              <div className="text-sm text-gray-500 mt-1">Found this week</div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">{company.articles_analyzed || 0}</div>
              <div className="text-gray-700 font-medium">Articles Analyzed</div>
              <div className="text-sm text-gray-500 mt-1">For sentiment</div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">{company.confidence}</div>
              <div className="text-gray-700 font-medium">Confidence</div>
              <div className="text-sm text-gray-500 mt-1">Analysis quality</div>
            </div>
          </div>

          {/* Analysis Details */}
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Analysis Details</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Analysis Date:</span>
                <span className="font-medium">{new Date(company.analysis_date).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Data Sources:</span>
                <span className="font-medium">{company.sources.join(', ')}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Unique Sources:</span>
                <span className="font-medium">{company.unique_sources}</span>
              </div>
            </div>
          </div>

          {/* Analysis Explanation */}
          <div className="bg-blue-50 border-l-4 border-blue-400 p-6 rounded-r-lg">
            <h4 className="text-lg font-semibold text-blue-900 mb-2">Analysis Summary</h4>
            <p className="text-blue-800 leading-relaxed">{company.reason}</p>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center mt-8 space-x-4">
            <button
              onClick={onClose}
              className="px-8 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium"
            >
              Close Analysis
            </button>
            <button
              onClick={() => window.open(`https://finance.yahoo.com/quote/${company.symbol}`, '_blank')}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              View on Yahoo Finance
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};