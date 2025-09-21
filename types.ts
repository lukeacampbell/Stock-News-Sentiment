export interface Company {
  ticker: string;
  name?: string;
  marketCap?: string;
  sentimentScore?: number;
  articles_analyzed?: number;
  total_articles_available?: number;
}

export type DayEarnings = Company[];

export type EarningsCalendarData = {
  Monday?: DayEarnings;
  Tuesday?: DayEarnings;
  Wednesday?: DayEarnings;
  Thursday?: DayEarnings;
  Friday?: DayEarnings;
};

export interface LiveAnalysisData {
  symbol: string;
  article_count: number;
  sentiment_score: number;
  confidence: string;
  analysis_date: string;
  date_range: string;
  sources: string[];
  unique_sources: number;
  articles_analyzed: number;
  total_articles_found: number;
  reason: string;
}