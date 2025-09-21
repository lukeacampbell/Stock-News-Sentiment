import React from 'react';
import CompanyCard from './CompanyCard';
import { DayEarnings } from '../types';
import { getDayAndDate } from '../utils/dateUtils';

interface DayColumnProps {
  day: string;
  date: Date;
  dayIndex: number;
  data?: DayEarnings;
}

const DayColumn: React.FC<DayColumnProps> = ({ day, date, dayIndex, data }) => {
    const formattedDate = getDayAndDate(date, dayIndex);
    const hasEarnings = (data?.length ?? 0) > 0;

  return (
    <div className={`p-3 rounded-lg ${hasEarnings ? 'bg-brand-surface border border-brand-border' : 'bg-transparent'}`}>
      <div className="flex justify-between items-center mb-4 select-none">
        <h2 className="font-bold text-lg">{day}</h2>
        <span className="text-sm text-brand-secondary">{formattedDate}</span>
      </div>
      <div className="space-y-2">
        {hasEarnings && data ? (
            data.map((company) => (
                <CompanyCard key={company.ticker} company={company} />
            ))
        ) : (
            <div className="text-center py-10">
                <p className="text-sm text-brand-secondary">No earnings scheduled.</p>
            </div>
        )}
      </div>
    </div>
  );
};

export default DayColumn;