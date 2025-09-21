import React, { useMemo } from 'react';
import DayColumn from './DayColumn';
import { EarningsCalendarData } from '../types';
import { DAYS_OF_WEEK } from '../constants';
// FIX: Updated date-fns import for v3 compatibility.
import { startOfWeek } from 'date-fns/startOfWeek';

interface EarningsCalendarProps {
  data: EarningsCalendarData | null;
  searchTerm: string;
}

const EarningsCalendar: React.FC<EarningsCalendarProps> = ({ data, searchTerm }) => {

  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) {
      return data;
    }
    if (!data) {
      return null;
    }

    const lowercasedSearchTerm = searchTerm.toLowerCase();
    const filteredResult: EarningsCalendarData = {};

    for (const day of DAYS_OF_WEEK) {
        const dayKey = day as keyof EarningsCalendarData;
        const dayData = data[dayKey];

        if (dayData) {
            const filteredCompanies = dayData.filter(
                c => c.ticker.toLowerCase().includes(lowercasedSearchTerm) ||
                     (c.name && c.name.toLowerCase().includes(lowercasedSearchTerm))
            );

            if (filteredCompanies.length > 0) {
                filteredResult[dayKey] = filteredCompanies;
            }
        }
    }
    return filteredResult;
  }, [data, searchTerm]);

  if (!filteredData) {
    return <div className="text-center p-8">No earnings data available.</div>;
  }
  
  const totalResults = DAYS_OF_WEEK.reduce((acc, day) => {
    const dayData = filteredData[day as keyof EarningsCalendarData];
    return acc + (dayData?.length || 0);
  }, 0);

  if (totalResults === 0) {
    if (searchTerm) {
      return <div className="text-center p-8 text-brand-secondary">No companies matching "{searchTerm}" found for this week.</div>;
    }
    return <div className="text-center p-8 text-brand-secondary">No companies scheduled for this week.</div>;
  }
  
  const weekStart = startOfWeek(new Date(), { weekStartsOn: 1 });

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {DAYS_OF_WEEK.map((day, index) => {
        const dayData = filteredData[day as keyof EarningsCalendarData];
        // Render DayColumn only if there's data for it after filtering
        return dayData && dayData.length > 0 ? (
          <DayColumn
            key={day}
            day={day}
            date={weekStart}
            dayIndex={index}
            data={dayData}
          />
        ) : null;
      })}
    </div>
  );
};

export default EarningsCalendar;
