import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { User } from './types';
import { apiService } from './services/api';

// Components
import Layout from './components/Layout/Layout';
import HomePage from './components/HomePage/HomePage';
import Dashboard from './components/Dashboard/Dashboard';
import ProjectDetail from './components/ProjectDetail';
import BookCatalog from './components/BookCatalog';
import UserSelector from './components/UserSelector/UserSelector';

import './App.css';

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Carica utenti mock al primo avvio
    const loadInitialData = async () => {
      try {
        const users = await apiService.getUsers();
        if (users.length === 0) {
          // Se non ci sono utenti, ne creiamo due mock
          console.log('Nessun utente trovato, usando utenti mock');
          const mockUsers: User[] = [
            {
              id: '1',
              name: 'Marco Rossi',
              email: 'marco.rossi@example.com',
              type: 'image_editor',
              avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Marco'
            },
            {
              id: '2', 
              name: 'Elena Bianchi',
              email: 'elena.bianchi@example.com',
              type: 'veo_user',
              avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Elena'
            }
          ];
          // Per ora salviamo in localStorage
          localStorage.setItem('mockUsers', JSON.stringify(mockUsers));
        }

        // Controlla se c'è un utente salvato
        const savedUserId = localStorage.getItem('currentUserId');
        if (savedUserId) {
          const user = await apiService.getUserById(savedUserId);
          if (user) {
            setCurrentUser(user);
          }
        }
      } catch (error) {
        console.error('Errore nel caricamento iniziale:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, []);

  const handleUserSelect = (user: User) => {
    setCurrentUser(user);
    localStorage.setItem('currentUserId', user.id);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUserId');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Caricamento...</p>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gray-50">
        <UserSelector onUserSelect={handleUserSelect} />
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Layout user={currentUser} onLogout={handleLogout}>
          <Routes>
            <Route path="/" element={<HomePage user={currentUser} />} />
            <Route path="/dashboard" element={<Dashboard user={currentUser} />} />            <Route path="/project/:id" element={<ProjectDetail />} />
            <Route path="/catalog" element={<BookCatalog />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              style: {
                background: '#10B981',
              },
            },
            error: {
              style: {
                background: '#EF4444',
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;