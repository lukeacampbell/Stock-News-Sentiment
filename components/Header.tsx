import React, { useState, useEffect } from 'react';
import { Company } from '../types';

interface HeaderProps {
  searchTerm: string;
  onSearchChange: (term: string) => void;
  allCompanies: Company[];
  onLiveAnalysis: (symbol: string) => void;
}

const Header: React.FC<HeaderProps> = ({ searchTerm, onSearchChange, allCompanies, onLiveAnalysis }) => {
  const [ghostText, setGhostText] = useState('');
  const [activeSuggestion, setActiveSuggestion] = useState('');

  useEffect(() => {
    if (searchTerm) {
      const lowercasedTerm = searchTerm.toLowerCase();
      const found = allCompanies.find(
        company => company.ticker.toLowerCase().startsWith(lowercasedTerm)
      );
      
      if (found) {
        const matchedString = found.ticker;
        setActiveSuggestion(matchedString);
        const ghost = searchTerm + matchedString.slice(searchTerm.length);
        setGhostText(ghost);
      } else {
        setActiveSuggestion('');
        setGhostText('');
      }
    } else {
      setActiveSuggestion('');
      setGhostText('');
    }
  }, [searchTerm, allCompanies]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if ((e.key === 'Tab' || e.key === 'ArrowRight') && activeSuggestion) {
      if (e.currentTarget.selectionStart === searchTerm.length) {
        e.preventDefault();
        onSearchChange(activeSuggestion);
      }
    }
  };
  
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onLiveAnalysis(searchTerm);
  };

  return (
    <header className="relative">
      <form onSubmit={handleSubmit} className="flex items-center p-3 bg-brand-surface rounded-lg border border-brand-border sticky top-4 z-20 h-[50px]">
        <span className="text-brand-primary font-mono text-xl mr-2 select-none">&gt;</span>
        <div className="relative flex-grow h-full">
          <input
            type="text"
            disabled
            value={ghostText}
            className="absolute inset-0 w-full h-full bg-transparent text-brand-secondary/50 placeholder-transparent focus:outline-none text-lg pointer-events-none"
            aria-hidden="true"
          />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search by ticker or name... (Press Enter to Analyze)"
            className="relative w-full h-full bg-transparent text-brand-text placeholder-brand-secondary/50 focus:outline-none text-lg"
            aria-label="Search for a company"
          />
        </div>
      </form>
    </header>
  );
};

export default Header;