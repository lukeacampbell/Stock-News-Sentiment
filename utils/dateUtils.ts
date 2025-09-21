// FIX: Updated date-fns imports for v3 compatibility.
import { startOfWeek } from 'date-fns/startOfWeek';
import { endOfWeek } from 'date-fns/endOfWeek';
import { addDays } from 'date-fns/addDays';
import { format } from 'date-fns/format';

export const getWeekDateRange = (date: Date) => {
  const start = startOfWeek(date, { weekStartsOn: 1 });
  const end = endOfWeek(date, { weekStartsOn: 1 });
  return { start, end };
};

export const getDayAndDate = (weekStart: Date, dayIndex: number): string => {
    const day = addDays(weekStart, dayIndex);
    return format(day, "d MMM");
};