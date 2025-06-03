import React from 'react';
import './UserSelector.css';

interface UserSelectorProps {
  currentUser: string;
  userMode: 'tool' | 'veo';
  onUserChange: (user: string) => void;
  onModeChange: (mode: 'tool' | 'veo') => void;
}

const UserSelector: React.FC<UserSelectorProps> = ({
  currentUser,
  userMode,
  onUserChange,
  onModeChange
}) => {
  const users = [
    { id: 'mario', name: 'Mario', avatar: '👨‍💻' },
    { id: 'anna', name: 'Anna', avatar: '👩‍🎨' },
    { id: 'luca', name: 'Luca', avatar: '👨‍🏫' },
    { id: 'sofia', name: 'Sofia', avatar: '👩‍💼' }
  ];

  const modes = [
    {
      id: 'tool' as const,
      name: 'Tool',
      description: 'Modalità tradizionale con strumenti di base',
      icon: '🔧',
      features: ['Stable Diffusion', 'TTS Standard', 'MoviePy']
    },
    {
      id: 'veo' as const,
      name: 'Veo',
      description: 'Modalità avanzata con pipeline Veo2/3',
      icon: '🚀',
      features: ['Veo2/3 Pipeline', 'TTS Avanzato', 'Editing Intelligente']
    }
  ];

  return (
    <div className="user-selector">
      <div className="selector-section">
        <h3>Seleziona Utente</h3>
        <div className="users-grid">
          {users.map((user) => (
            <div
              key={user.id}
              className={`user-card ${currentUser === user.id ? 'selected' : ''}`}
              onClick={() => onUserChange(user.id)}
            >
              <div className="user-avatar">{user.avatar}</div>
              <div className="user-name">{user.name}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="selector-section">
        <h3>Modalità di Generazione</h3>
        <div className="modes-grid">
          {modes.map((mode) => (
            <div
              key={mode.id}
              className={`mode-card ${userMode === mode.id ? 'selected' : ''}`}
              onClick={() => onModeChange(mode.id)}
            >
              <div className="mode-header">
                <div className="mode-icon">{mode.icon}</div>
                <div className="mode-info">
                  <h4>{mode.name}</h4>
                  <p>{mode.description}</p>
                </div>
              </div>
              
              <div className="mode-features">
                <h5>Caratteristiche:</h5>
                <ul>
                  {mode.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>

              {userMode === mode.id && (
                <div className="mode-selected-indicator">
                  ✓ Selezionato
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="selection-summary">
        <div className="summary-card">
          <h4>Configurazione Attuale</h4>
          <div className="summary-details">
            <div className="summary-item">
              <span className="summary-label">Utente:</span>
              <span className="summary-value">
                {users.find(u => u.id === currentUser)?.avatar} {users.find(u => u.id === currentUser)?.name}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Modalità:</span>
              <span className="summary-value">
                {modes.find(m => m.id === userMode)?.icon} {modes.find(m => m.id === userMode)?.name}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserSelector;
