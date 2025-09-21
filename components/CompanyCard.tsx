import React from 'react';
import { Company } from '../types';

interface CompanyCardProps {
  company: Company;
}

// Function to map sentiment score to a color on a red-yellow-green gradient.
// Scores are clamped between -10 and 10 for color calculation.
const getSentimentColor = (score: number): string => {
  const clampedScore = Math.max(-10, Math.min(10, score));
  let hue: number;

  if (clampedScore <= 0) {
    // Interpolate from red (0) to yellow (60)
    // As score goes from -10 to 0, hue goes from 0 to 60
    hue = 60 * (clampedScore + 10) / 10;
  } else {
    // Interpolate from yellow (60) to green (120)
    // As score goes from 0 to 10, hue goes from 60 to 120
    hue = 60 + (60 * clampedScore / 10);
  }

  // Using HSL for smooth color transition.
  return `hsl(${hue}, 70%, 45%)`;
};


const CompanyCard: React.FC<CompanyCardProps> = ({ company }) => {
  const hasSentiment = company.sentimentScore !== undefined;
  const scoreText = hasSentiment ? (company.sentimentScore > 0 ? `+${company.sentimentScore}` : `${company.sentimentScore}`) : '';
  
  // Create a more reliable search query for Google that will lead to the correct finance page.
  const searchQuery = `Google Finance ${company.ticker} ${company.name || ''}`;
  const stockUrl = `https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`;

  return (
    <a
      href={stockUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center justify-between bg-brand-bg rounded-lg border border-brand-border transition-all duration-200 p-4 min-h-[72px] hover:scale-105 hover:border-brand-primary select-none cursor-pointer"
      aria-label={`View details for ${company.name || company.ticker}`}
    >
      <div className="flex-1 min-w-0 pr-4">
        <p className="text-base font-bold text-brand-text truncate">{company.ticker}</p>
        {company.name && <p className="text-sm text-brand-secondary truncate">{company.name}</p>}
        {company.total_articles_available !== undefined && (
          <p className="text-xs text-brand-secondary/70 truncate pt-1">
            {company.total_articles_available} news articles
          </p>
        )}
      </div>
      {hasSentiment && (
        <div
          className="flex items-center justify-center w-14 h-14 rounded-md flex-shrink-0"
          style={{ backgroundColor: getSentimentColor(company.sentimentScore as number) }}
          aria-label={`Sentiment score: ${scoreText}`}
        >
          <span className="text-white font-bold text-lg font-mono">
            {scoreText}
          </span>
        </div>
      )}
    </a>
  );
};

export default CompanyCard;