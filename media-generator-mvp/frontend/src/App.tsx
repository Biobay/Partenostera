import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard/Dashboard';
import FileUpload from './components/FileUpload/FileUpload';
import UserSelector from './components/UserSelector/UserSelector';
import { apiService } from './services/api';
import './App.css';

type AppView = 'selector' | 'upload' | 'dashboard';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>('selector');
  const [currentUser, setCurrentUser] = useState<string>('mario');
  const [userMode, setUserMode] = useState<'tool' | 'veo'>('tool');
  const [notification, setNotification] = useState<{
    type: 'success' | 'error' | 'info';
    message: string;
  } | null>(null);

  useEffect(() => {
    // Carica le preferenze utente salvate dal localStorage
    const savedUser = localStorage.getItem('selectedUser');
    const savedMode = localStorage.getItem('userMode');
    
    if (savedUser) {
      setCurrentUser(savedUser);
    }
    if (savedMode && (savedMode === 'tool' || savedMode === 'veo')) {
      setUserMode(savedMode);
    }
  }, []);

  const handleUserChange = (user: string) => {
    setCurrentUser(user);
    localStorage.setItem('selectedUser', user);
  };

  const handleModeChange = (mode: 'tool' | 'veo') => {
    setUserMode(mode);
    localStorage.setItem('userMode', mode);
  };

  const handleUploadSuccess = (response: any) => {
    setNotification({
      type: 'success',
      message: 'Generazione avviata con successo! Controlla la dashboard per il progresso.'
    });
    setCurrentView('dashboard');
  };

  const handleUploadError = (error: string) => {
    setNotification({
      type: 'error',
      message: error
    });
  };

  const showNotification = (type: 'success' | 'error' | 'info', message: string) => {
    setNotification({ type, message });
  };

  // Auto-hide notifications dopo 5 secondi
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setNotification(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const dismissNotification = () => {
    setNotification(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="app-title">
              <span className="app-icon">🎬</span>
              MediaGen MVP
            </h1>
            <p className="app-subtitle">Generazione Automatica di Contenuti Multimediali</p>
          </div>
          
          <nav className="header-nav">
            <button
              className={`nav-button ${currentView === 'selector' ? 'active' : ''}`}
              onClick={() => setCurrentView('selector')}
            >
              👤 Utente
            </button>
            <button
              className={`nav-button ${currentView === 'upload' ? 'active' : ''}`}
              onClick={() => setCurrentView('upload')}
            >
              ⬆️ Carica
            </button>
            <button
              className={`nav-button ${currentView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentView('dashboard')}
            >
              📊 Dashboard
            </button>
          </nav>
        </div>
      </header>

      {notification && (
        <div className={`notification notification-${notification.type}`}>
          <div className="notification-content">
            <span className="notification-icon">
              {notification.type === 'success' ? '✅' : 
               notification.type === 'error' ? '❌' : 'ℹ️'}
            </span>
            <span className="notification-message">{notification.message}</span>
            <button 
              className="notification-close"
              onClick={dismissNotification}
            >
              ✕
            </button>
          </div>
        </div>
      )}

      <main className="app-main">
        {currentView === 'selector' && (
          <UserSelector
            currentUser={currentUser}
            userMode={userMode}
            onUserChange={handleUserChange}
            onModeChange={handleModeChange}
          />
        )}

        {currentView === 'upload' && (
          <FileUpload
            currentUser={currentUser}
            userMode={userMode}
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        )}

        {currentView === 'dashboard' && (
          <Dashboard currentUser={currentUser} />
        )}
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-info">
            <p>
              <strong>Utente attivo:</strong> {currentUser} | 
              <strong> Modalità:</strong> {userMode.toUpperCase()}
            </p>
          </div>
          <div className="footer-links">
            <a href="#help" onClick={(e) => {
              e.preventDefault();
              showNotification('info', 'Documentazione disponibile nel repository GitHub del progetto.');
            }}>
              Aiuto
            </a>
            <a href="#about" onClick={(e) => {
              e.preventDefault();
              showNotification('info', 'MediaGen MVP v1.0 - Sistema di generazione automatica di contenuti multimediali');
            }}>
              Info
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
