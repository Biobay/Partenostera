import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  progress: number; // 0-100
  showPercentage?: boolean;
  label?: string;
  color?: string;
  height?: string;
  animated?: boolean;
  striped?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  showPercentage = false,
  label,
  color = '#4CAF50',
  height = '20px',
  animated = false,
  striped = false
}) => {
  // Assicurati che il progresso sia tra 0 e 100
  const clampedProgress = Math.max(0, Math.min(100, progress));
  
  const getProgressColor = (progress: number): string => {
    if (color !== '#4CAF50') return color;
    
    if (progress < 25) return '#F44336';
    if (progress < 50) return '#FF9800';
    if (progress < 75) return '#2196F3';
    return '#4CAF50';
  };

  const progressColor = getProgressColor(clampedProgress);

  return (
    <div className="progress-bar-container">
      {label && (
        <div className="progress-label">
          <span>{label}</span>
          {showPercentage && (
            <span className="progress-percentage">{clampedProgress.toFixed(0)}%</span>
          )}
        </div>
      )}
      
      <div 
        className="progress-bar-track"
        style={{ height }}
      >
        <div
          className={`progress-bar-fill ${striped ? 'striped' : ''} ${animated ? 'animated' : ''}`}
          style={{
            width: `${clampedProgress}%`,
            backgroundColor: progressColor,
            transition: 'width 0.3s ease, background-color 0.3s ease'
          }}
        >
          {showPercentage && !label && (
            <span className="progress-text">
              {clampedProgress.toFixed(0)}%
            </span>
          )}
        </div>
      </div>
      
      {!label && showPercentage && (
        <div className="progress-percentage-below">
          {clampedProgress.toFixed(0)}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
