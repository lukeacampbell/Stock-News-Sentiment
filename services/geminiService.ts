import type { EarningsCalendarData, Company } from "../types";
import { DAYS_OF_WEEK } from '../constants';

// Configuration for API endpoints
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '/api';

export const getEarningsData = async (): Promise<EarningsCalendarData> => {
  try {
    // Fetch sentiment data from Flask backend
    const sentimentResponse = await fetch(`${API_BASE_URL}/sentiment`);
    
    if (!sentimentResponse.ok) {
      if (sentimentResponse.status === 404) {
        throw new Error("No earnings data available yet. The backend may still be processing data.");
      }
      throw new Error(`Failed to fetch sentiment data: ${sentimentResponse.status}`);
    }
    
    // Fetch company names data
    const namesResponse = await fetch('./data/company-names.json');
    if (!namesResponse.ok) {
      console.warn('Could not fetch company names, will use tickers instead');
    }
    
    const sentimentData = await sentimentResponse.json();
    const namesData = namesResponse.ok ? await namesResponse.json() : {};
    
    const namesMap: Record<string, string> = namesData;

    if (!sentimentData || !sentimentData.sentiment_results) {
      throw new Error("Invalid data format in earnings sentiment data");
    }

    // Create calendar data structure organized by actual earnings days
    const calendarData: EarningsCalendarData = {
      Monday: [],
      Tuesday: [],
      Wednesday: [],
      Thursday: [],
      Friday: [],
    };

    // Fetch earnings data to get actual earnings days
    let earningsData: any = {};
    try {
      const earningsResponse = await fetch(`${API_BASE_URL}/earnings`);
      if (earningsResponse.ok) {
        earningsData = await earningsResponse.json();
      }
    } catch (e) {
      console.warn('Could not fetch earnings calendar data');
    }

    const sentimentResults = sentimentData.sentiment_results;

    sentimentResults.forEach((companySentiment: any) => {
      // Try to get actual earnings day from earnings data, fallback to random distribution
      let day: keyof EarningsCalendarData = 'Monday'; // default
      
      if (earningsData.companies && earningsData.companies[companySentiment.ticker]) {
        const earningsDay = earningsData.companies[companySentiment.ticker].earnings_day;
        if (earningsDay && DAYS_OF_WEEK.includes(earningsDay)) {
          day = earningsDay as keyof EarningsCalendarData;
        }
      } else {
        // Fallback: distribute across days based on ticker hash for consistency
        const hash = companySentiment.ticker.split('').reduce((a: number, b: string) => {
          a = ((a << 5) - a) + b.charCodeAt(0);
          return a & a;
        }, 0);
        const dayIndex = Math.abs(hash) % DAYS_OF_WEEK.length;
        day = DAYS_OF_WEEK[dayIndex] as keyof EarningsCalendarData;
      }

      const company: Company = {
        ticker: companySentiment.ticker,
        name: namesMap[companySentiment.ticker] || 'Unknown Company',
        sentimentScore: companySentiment.sentiment_score,
        articles_analyzed: companySentiment.articles_analyzed,
        total_articles_available: companySentiment.total_articles_available,
      };
      
      calendarData[day]?.push(company);
    });

    // Sort companies within each day by article count (most articles first), then by sentiment
    for (const day of DAYS_OF_WEEK) {
      const dayKey = day as keyof EarningsCalendarData;
      if (calendarData[dayKey]) {
        calendarData[dayKey]?.sort((a, b) => {
          // Primary sort: total articles (descending) - most articles at top
          const articlesA = a.total_articles_available || 0;
          const articlesB = b.total_articles_available || 0;
          if (articlesB !== articlesA) {
            return articlesB - articlesA;
          }
          // Secondary sort: sentiment score (descending)
          return b.sentimentScore - a.sentimentScore;
        });
      }
    }

    return calendarData;
    
  } catch (error) {
    console.error('Error fetching earnings data:', error);
    throw error;
  }
};

// New function to get backend status
export const getBackendStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/status`);
    if (!response.ok) {
      throw new Error(`Backend status check failed: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Backend status check failed:', error);
    throw new Error('Could not connect to backend. Please ensure the Flask server is running on port 5000.');
  }
};

// New function to trigger manual update
export const triggerManualUpdate = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/update`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Update failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Manual update failed:', error);
    throw error;
  }
};