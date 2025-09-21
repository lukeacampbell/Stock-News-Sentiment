import React from 'react';
import type { LiveAnalysisData } from '../types';

interface AnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: LiveAnalysisData | null;
  loading: boolean;
  error: string | null;
}

const getSentimentColorClass = (score: number) => {
  if (score > 3) return 'text-green-400';
  if (score < -3) return 'text-red-400';
  if (score > 0) return 'text-green-500/80';
  if (score < 0) return 'text-red-500/80';
  return 'text-brand-secondary';
};

export const AnalysisModal: React.FC<AnalysisModalProps> = ({ isOpen, onClose, data, loading, error }) => {
  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm"
      aria-modal="true"
      role="dialog"
      onClick={onClose}
    >
      <div
        className="bg-brand-surface rounded-lg border border-brand-border shadow-xl w-full max-w-md m-4 transform transition-all"
        onClick={e => e.stopPropagation()} // Prevent closing when clicking inside the modal
      >
        <div className="flex items-center justify-between p-4 border-b border-brand-border">
          <h2 className="text-lg font-bold text-brand-primary">Live Sentiment Analysis</h2>
          <button
            onClick={onClose}
            className="text-brand-secondary hover:text-brand-primary"
            aria-label="Close modal"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 min-h-[200px] flex items-center justify-center">
          {loading && (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary"></div>
              <p className="mt-4 text-brand-secondary">Analyzing live news...</p>
            </div>
          )}
          {error && (
            <div className="text-center">
              <p className="text-red-400 font-semibold mb-2">Analysis Failed</p>
              <p className="text-brand-secondary text-sm">{error}</p>
            </div>
          )}
          {data && (
            <div className="w-full">
              <div className="text-center mb-6">
                <p className="text-4xl font-bold text-brand-text">{data.symbol}</p>
                <p className={`text-6xl font-mono font-bold mt-2 ${getSentimentColorClass(data.sentiment_score)}`}>
                  {data.sentiment_score > 0 ? `+${data.sentiment_score}` : data.sentiment_score}
                </p>
                <p className="text-sm text-brand-secondary capitalize">Confidence: {data.confidence}</p>
              </div>

              <div className="text-sm space-y-2">
                <div className="flex justify-between">
                  <span className="text-brand-secondary">Reason:</span>
                  <span className="text-brand-text text-right">{data.reason}</span>
                </div>
                 <div className="flex justify-between">
                  <span className="text-brand-secondary">Articles Analyzed:</span>
                  <span className="text-brand-text">{data.articles_analyzed} / {data.total_articles_found}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-brand-secondary">Unique Sources:</span>
                  <span className="text-brand-text">{data.unique_sources}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-brand-secondary">Date Range:</span>
                  <span className="text-brand-text">{data.date_range}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};