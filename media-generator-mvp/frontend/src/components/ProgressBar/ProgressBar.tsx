import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  progress: number;
  label?: string;
  color?: 'blue' | 'green' | 'orange' | 'red';
  size?: 'sm' | 'md' | 'lg';
  showPercentage?: boolean;
  animated?: boolean;
  striped?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  label,
  color = 'blue',
  size = 'md',
  showPercentage = true,
  animated = false,
  striped = false,
}) => {
  const clampedProgress = Math.max(0, Math.min(100, progress));

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-4',
    lg: 'h-6',
  };

  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500',
  };

  const getStatusColor = (progress: number) => {
    if (progress < 25) return 'red';
    if (progress < 50) return 'orange';
    if (progress < 75) return 'orange';
    return 'green';
  };

  const statusColor = color === 'blue' ? getStatusColor(clampedProgress) : color;

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </span>
          {showPercentage && (
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {Math.round(clampedProgress)}%
            </span>
          )}
        </div>
      )}
      
      <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full ${sizeClasses[size]} overflow-hidden`}>
        <div
          className={`
            h-full transition-all duration-500 ease-out rounded-full
            ${colorClasses[statusColor]}
            ${animated ? 'progress-bar-animated' : ''}
            ${striped ? 'progress-bar-striped' : ''}
          `}
          style={{ width: `${clampedProgress}%` }}
          role="progressbar"
          aria-valuenow={clampedProgress}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          {size === 'lg' && showPercentage && (
            <div className="flex items-center justify-center h-full text-xs font-medium text-white">
              {Math.round(clampedProgress)}%
            </div>
          )}
        </div>
      </div>
      
      {clampedProgress === 100 && (
        <div className="flex items-center mt-2 text-green-600 dark:text-green-400">
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          <span className="text-sm font-medium">Completato</span>
        </div>
      )}
    </div>
  );
};

export default ProgressBar;