import { render, screen, fireEvent } from '@testing-library/react';
import ProgressBar from '../components/ProgressBar/ProgressBar';

test('renders progress bar with correct percentage', () => {
  render(<ProgressBar progress={75} showPercentage={true} />);
  
  const percentage = screen.getByText('75%');
  expect(percentage).toBeInTheDocument();
});

test('renders progress bar with label', () => {
  render(<ProgressBar progress={50} label="Generazione in corso" showPercentage={true} />);
  
  const label = screen.getByText(/Generazione in corso/i);
  const percentage = screen.getByText('50%');
  
  expect(label).toBeInTheDocument();
  expect(percentage).toBeInTheDocument();
});

test('clamps progress value between 0 and 100', () => {
  const { rerender } = render(<ProgressBar progress={150} showPercentage={true} />);
  expect(screen.getByText('100%')).toBeInTheDocument();
  
  rerender(<ProgressBar progress={-50} showPercentage={true} />);
  expect(screen.getByText('0%')).toBeInTheDocument();
});
