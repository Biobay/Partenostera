import React, { useState, useEffect } from 'react';
import { Project, GenerationStatus } from '../../types';
import { apiService } from '../../services/api';
import VideoPlayer from '../VideoPlayer/VideoPlayer';
import ProgressBar from '../ProgressBar/ProgressBar';
import './Dashboard.css';

interface DashboardProps {
  currentUser: string;
}

const Dashboard: React.FC<DashboardProps> = ({ currentUser }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, [currentUser]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const userProjects = await apiService.getUserProjects(currentUser);
      setProjects(userProjects);
    } catch (err) {
      setError('Errore nel caricamento dei progetti');
      console.error('Error loading projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (projectId: string) => {
    if (!window.confirm('Sei sicuro di voler eliminare questo progetto?')) {
      return;
    }

    try {
      await apiService.deleteProject(projectId);
      setProjects(projects.filter(p => p.id !== projectId));
      if (selectedProject?.id === projectId) {
        setSelectedProject(null);
      }
    } catch (err) {
      setError('Errore nell\'eliminazione del progetto');
      console.error('Error deleting project:', err);
    }
  };

  const getStatusColor = (status: GenerationStatus): string => {
    switch (status) {
      case 'completed': return '#4CAF50';
      case 'processing': return '#FF9800';
      case 'failed': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusText = (status: GenerationStatus): string => {
    switch (status) {
      case 'completed': return 'Completato';
      case 'processing': return 'In Elaborazione';
      case 'failed': return 'Fallito';
      default: return 'In Attesa';
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Caricamento progetti...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p>{error}</p>
        <button onClick={loadProjects} className="retry-button">
          Riprova
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>I Tuoi Progetti</h2>
        <button onClick={loadProjects} className="refresh-button">
          Aggiorna
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="no-projects">
          <p>Nessun progetto trovato. Inizia creando il tuo primo contenuto multimediale!</p>
        </div>
      ) : (
        <div className="dashboard-content">
          <div className="projects-list">
            <h3>Progetti ({projects.length})</h3>
            {projects.map(project => (
              <div 
                key={project.id} 
                className={`project-card ${selectedProject?.id === project.id ? 'selected' : ''}`}
                onClick={() => setSelectedProject(project)}
              >
                <div className="project-header">
                  <h4>{project.title}</h4>
                  <span 
                    className="project-status"
                    style={{ backgroundColor: getStatusColor(project.status) }}
                  >
                    {getStatusText(project.status)}
                  </span>
                </div>
                
                <div className="project-info">
                  <p><strong>Modalità:</strong> {project.userMode}</p>
                  <p><strong>Sequenze:</strong> {project.sequences.length}</p>
                  <p><strong>Creato:</strong> {new Date(project.createdAt).toLocaleDateString('it-IT')}</p>
                </div>

                {project.status === 'processing' && (
                  <ProgressBar 
                    progress={project.progress || 0}
                    showPercentage={true}
                  />
                )}

                <div className="project-actions">
                  {project.status === 'completed' && project.outputPath && (
                    <button 
                      className="view-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedProject(project);
                      }}
                    >
                      Visualizza Video
                    </button>
                  )}
                  <button 
                    className="delete-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteProject(project.id);
                    }}
                  >
                    Elimina
                  </button>
                </div>
              </div>
            ))}
          </div>

          {selectedProject && selectedProject.status === 'completed' && selectedProject.outputPath && (
            <div className="video-preview">
              <h3>Anteprima Video</h3>
              <VideoPlayer
                src={selectedProject.outputPath}
                title={selectedProject.title}
              />
              <div className="video-details">
                <h4>Dettagli Progetto</h4>
                <p><strong>Titolo:</strong> {selectedProject.title}</p>
                <p><strong>Descrizione:</strong> {selectedProject.description || 'Nessuna descrizione'}</p>
                <p><strong>Sequenze generate:</strong> {selectedProject.sequences.length}</p>
                <p><strong>Modalità utente:</strong> {selectedProject.userMode}</p>
                <p><strong>Completato il:</strong> {new Date(selectedProject.updatedAt).toLocaleString('it-IT')}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
