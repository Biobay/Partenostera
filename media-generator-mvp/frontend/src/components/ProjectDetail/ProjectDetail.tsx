import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Project } from '../../types';
import VideoPlayer from '../VideoPlayer/VideoPlayer';
import ProgressBar from '../ProgressBar/ProgressBar';
import { apiService } from '../../services/api';
import './ProjectDetail.css';

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'images' | 'audio' | 'video'>('overview');
  const [regeneratingContent, setRegeneratingContent] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadProject(id);
      // Setup WebSocket per aggiornamenti real-time
      setupWebSocket(id);
    }
  }, [id]);

  const loadProject = async (projectId: string) => {
    try {
      setLoading(true);      const response = await apiService.getProject(projectId);
      setProject(response.data || null);
    } catch (err) {
      setError('Errore nel caricamento del progetto');
      console.error('Error loading project:', err);
    } finally {
      setLoading(false);
    }
  };
  const setupWebSocket = (projectId: string) => {
    const ws = apiService.connectWebSocket(projectId);
    
    if (!ws) return () => {};
    
    ws.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      if (data.type === 'project_update') {
        setProject(prev => prev ? { ...prev, ...data.project } : null);
      }
    };

    return () => {
      ws.close();
    };
  };

  const handleRegenerateContent = async (type: 'images' | 'audio' | 'video') => {
    if (!project) return;

    try {
      setRegeneratingContent(type);      switch (type) {
        case 'images':
          // Analizzare il testo per ottenere i chunks
          const chunks = await apiService.analyzeText(project.textContent);
          await apiService.generateImages(project.id, chunks);
          break;
        case 'audio':
          // Analizzare il testo per ottenere i chunks
          const audioChunks = await apiService.analyzeText(project.textContent);
          await apiService.generateAudio(project.id, audioChunks);
          break;
        case 'video':
          await apiService.generateVideo(project.id);
          break;
      }
      
      // Ricarica il progetto per ottenere i nuovi dati
      await loadProject(project.id);
    } catch (err) {
      console.error(`Error regenerating ${type}:`, err);
    } finally {
      setRegeneratingContent(null);
    }
  };

  const handleDeleteProject = async () => {
    if (!project) return;
    
    if (window.confirm('Sei sicuro di voler eliminare questo progetto?')) {
      try {
        await apiService.deleteProject(project.id);
        navigate('/dashboard');
      } catch (err) {
        console.error('Error deleting project:', err);
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-blue-600 bg-blue-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completato';
      case 'processing':
        return 'In elaborazione';
      case 'error':
        return 'Errore';
      case 'draft':
        return 'Bozza';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="project-detail-loading">
        <div className="loading-spinner"></div>
        <p>Caricamento progetto...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="project-detail-error">
        <div className="error-icon">⚠️</div>
        <h2>Errore</h2>
        <p>{error || 'Progetto non trovato'}</p>
        <button onClick={() => navigate('/dashboard')} className="back-button">
          Torna alla Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="project-detail">
      <div className="project-header">
        <div className="header-content">
          <button onClick={() => navigate('/dashboard')} className="back-button">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 12H5m7-7-7 7 7 7"/>
            </svg>
            Torna alla Dashboard
          </button>
          
          <div className="project-info">
            <h1 className="project-title">{project.title}</h1>
            <p className="project-description">{project.description}</p>
            
            <div className="project-meta">
              <span className={`status-badge ${getStatusColor(project.status)}`}>
                {getStatusText(project.status)}
              </span>
              <span className="project-date">
                Creato: {new Date(project.createdAt).toLocaleDateString('it-IT')}
              </span>
              <span className="project-progress">
                Progresso: {Math.round(project.progress)}%
              </span>
            </div>
          </div>
          
          <div className="project-actions">
            <button
              onClick={() => handleRegenerateContent('video')}
              disabled={regeneratingContent === 'video'}
              className="action-button primary"
            >
              {regeneratingContent === 'video' ? 'Rigenerando...' : 'Rigenera Video'}
            </button>
            
            <button
              onClick={handleDeleteProject}
              className="action-button danger"
            >
              Elimina Progetto
            </button>
          </div>
        </div>
        
        {project.status === 'processing' && (
          <div className="progress-section">
            <ProgressBar
              progress={project.progress}
              label={project.processingStep?.currentOperation || 'Elaborazione in corso...'}
              animated={true}
              striped={true}
            />
            {project.processingStep && (
              <div className="processing-details">
                <span>
                  Step {project.processingStep.completed} di {project.processingStep.total}
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="project-content">
        <div className="content-tabs">
          <button
            onClick={() => setActiveTab('overview')}
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          >
            Panoramica
          </button>
          <button
            onClick={() => setActiveTab('images')}
            className={`tab-button ${activeTab === 'images' ? 'active' : ''}`}
          >
            Immagini ({project.generatedImages.length})
          </button>
          <button
            onClick={() => setActiveTab('audio')}
            className={`tab-button ${activeTab === 'audio' ? 'active' : ''}`}
          >
            Audio ({project.generatedAudio.length})
          </button>
          <button
            onClick={() => setActiveTab('video')}
            className={`tab-button ${activeTab === 'video' ? 'active' : ''}`}
          >
            Video Finale
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview-tab">
              <div className="overview-grid">
                <div className="overview-card">
                  <h3>Testo Originale</h3>
                  <div className="text-content">
                    <p>{project.textContent}</p>
                  </div>
                </div>
                
                <div className="overview-card">
                  <h3>Statistiche</h3>
                  <div className="stats-grid">
                    <div className="stat-item">
                      <span className="stat-value">{project.generatedImages.length}</span>
                      <span className="stat-label">Immagini Generate</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{project.generatedAudio.length}</span>
                      <span className="stat-label">File Audio</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{project.finalVideo ? '1' : '0'}</span>
                      <span className="stat-label">Video Finale</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'images' && (
            <div className="images-tab">
              <div className="tab-header">
                <h3>Immagini Generate</h3>
                <button
                  onClick={() => handleRegenerateContent('images')}
                  disabled={regeneratingContent === 'images'}
                  className="regenerate-button"
                >
                  {regeneratingContent === 'images' ? 'Rigenerando...' : 'Rigenera Immagini'}
                </button>
              </div>
              
              <div className="images-grid">
                {project.generatedImages.map((image, index) => (
                  <div key={image.id} className="image-card">
                    <div className="image-container">
                      <img src={image.url} alt={`Generated content ${index + 1}`} />
                      <div className="image-overlay">
                        <span className="image-order">#{image.order}</span>
                        <span className={`image-status ${image.status}`}>
                          {image.status === 'completed' ? '✓' : 
                           image.status === 'generating' ? '⏳' : '❌'}
                        </span>
                      </div>
                    </div>
                    <div className="image-info">
                      <p className="image-prompt">{image.prompt}</p>
                      <div className="image-validation">
                        {image.validated ? (
                          <span className="validated">✓ Validata</span>
                        ) : (
                          <span className="not-validated">⚠ Non validata</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'audio' && (
            <div className="audio-tab">
              <div className="tab-header">
                <h3>File Audio</h3>
                <button
                  onClick={() => handleRegenerateContent('audio')}
                  disabled={regeneratingContent === 'audio'}
                  className="regenerate-button"
                >
                  {regeneratingContent === 'audio' ? 'Rigenerando...' : 'Rigenera Audio'}
                </button>
              </div>
              
              <div className="audio-list">
                {project.generatedAudio.map((audio, index) => (
                  <div key={audio.id} className="audio-card">
                    <div className="audio-info">
                      <h4>Traccia Audio #{index + 1}</h4>
                      <p className="audio-text">{audio.text}</p>
                      <div className="audio-meta">
                        <span>Durata: {Math.round(audio.duration)}s</span>
                        <span className={`status ${audio.status}`}>
                          {audio.status === 'completed' ? 'Completato' : 
                           audio.status === 'generating' ? 'Generando...' : 'Errore'}
                        </span>
                      </div>
                    </div>
                    <div className="audio-player">
                      <audio controls src={audio.url}>
                        Il tuo browser non supporta l'elemento audio.
                      </audio>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'video' && (
            <div className="video-tab">
              <div className="tab-header">
                <h3>Video Finale</h3>
                {project.finalVideo && (
                  <a 
                    href={project.finalVideo.url} 
                    download={`${project.title}.mp4`}
                    className="download-button"
                  >
                    Scarica Video
                  </a>
                )}
              </div>
              
              {project.finalVideo ? (
                <div className="video-container">
                  <VideoPlayer
                    src={project.finalVideo.url}
                    title={project.title}
                    controls={true}
                  />
                  <div className="video-info">
                    <p>Durata: {Math.round(project.finalVideo.duration)}s</p>
                    <p>Creato: {new Date(project.finalVideo.createdAt).toLocaleDateString('it-IT')}</p>
                  </div>
                </div>
              ) : (
                <div className="no-video">
                  <div className="no-video-icon">🎬</div>
                  <h3>Nessun video disponibile</h3>
                  <p>Il video finale non è ancora stato generato o è in fase di elaborazione.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectDetail;
