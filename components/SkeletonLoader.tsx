
import React from 'react';

const SkeletonCard: React.FC = () => (
  <div className="p-3 bg-brand-bg rounded-lg border border-brand-border">
    <div className="flex items-center space-x-3">
      <div className="w-10 h-10 rounded-full bg-brand-border animate-pulse"></div>
      <div className="flex-1 space-y-2">
        <div className="h-4 w-3/4 bg-brand-border rounded animate-pulse"></div>
        <div className="h-3 w-1/2 bg-brand-border rounded animate-pulse"></div>
      </div>
    </div>
  </div>
);

const SkeletonDayColumn: React.FC = () => (
  <div className="p-3 rounded-lg bg-brand-surface">
    <div className="flex justify-between items-center mb-4">
      <div className="h-6 w-1/3 bg-brand-border rounded animate-pulse"></div>
      <div className="h-4 w-1/4 bg-brand-border rounded animate-pulse"></div>
    </div>
    <div className="space-y-4">
      <div>
        <div className="h-4 w-1/2 bg-brand-border rounded mb-2 animate-pulse"></div>
        <div className="space-y-2">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
      <div>
        <div className="h-4 w-1/2 bg-brand-border rounded mb-2 animate-pulse"></div>
        <div className="space-y-2">
          <SkeletonCard />
        </div>
      </div>
    </div>
  </div>
);

export const SkeletonLoader: React.FC = () => (
  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
    {[...Array(5)].map((_, i) => (
      <SkeletonDayColumn key={i} />
    ))}
  </div>
);