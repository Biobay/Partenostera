import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders app title', () => {
  render(<App />);
  const titleElement = screen.getByText(/MediaGen MVP/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders navigation buttons', () => {
  render(<App />);
  
  const userButton = screen.getByText(/Utente/i);
  const uploadButton = screen.getByText(/Carica/i);
  const dashboardButton = screen.getByText(/Dashboard/i);
  
  expect(userButton).toBeInTheDocument();
  expect(uploadButton).toBeInTheDocument();
  expect(dashboardButton).toBeInTheDocument();
});

test('shows user selector by default', () => {
  render(<App />);
  const selectorTitle = screen.getByText(/Seleziona Utente/i);
  expect(selectorTitle).toBeInTheDocument();
});
