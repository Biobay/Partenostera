import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  Play, 
  Pause, 
  Clock,
  CheckCircle,
  AlertCircle,
  Eye,
  Trash2,
  Download,
  MoreVertical
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Project } from '../../types';
import { apiService } from '../../services/api';
import FileUpload from '../FileUpload/FileUpload';
import SceneViewer from '../SceneViewer/SceneViewer';
import toast from 'react-hot-toast';

interface DashboardProps {
  user: User;
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showUpload, setShowUpload] = useState(false);  useEffect(() => {
    loadProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user.id]);
  const loadProjects = useCallback(async () => {
    try {
      setIsLoading(true);
      // Carica i progetti reali dal backend
      const realProjects = await apiService.getProjects(user.id);
      
      // Se non ci sono progetti reali, usa i dati mock come esempio
      if (realProjects.length === 0) {        const mockProjects: Project[] = [
          {
            id: '1',
            userId: user.id,
            title: 'Il Piccolo Principe - Capitolo 1',
            description: 'Trasformazione del primo capitolo in video',
            status: 'completed',
            createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            textContent: 'Un tempo lontano, quando avevo sei anni...',
            generatedImages: [],
            generatedAudio: [],
            finalVideo: {
              id: 'v1',
              url: '/api/videos/project-1.mp4',
              duration: 120,
              createdAt: new Date().toISOString(),
              status: 'completed'
            },
            progress: 100,            scenes: [
              {
                id: 'scene-1-1',
                title: 'Introduzione del narratore',
                content: 'Un tempo lontano, quando avevo sei anni, ho visto una magnifica immagine in un libro sulla Foresta Vergine che si intitolava "Storie vissute".',
                summary: 'Introduzione del narratore bambino che scopre il mondo degli adulti',
                characters: ['Narratore bambino', 'Adulti misteriosi'],
                setting: 'Casa del narratore, atmosfera nostalgica',
                mood: 'nostalgico, curioso, innocente',
                themes: ['infanzia', 'scoperta', 'crescita'],
                image_generation_status: 'completed',
                image_url: '/api/images/scene-1-1.jpg'
              },
              {
                id: 'scene-1-2',
                title: 'Primo incontro con i disegni',
                content: 'Rappresentava un serpente boa che ingoiava una fiera. Eccovi la copia del disegno.',
                summary: 'Primo incontro con i disegni e la creatività',
                characters: ['Narratore bambino'],
                setting: 'Stanza luminosa con libri e fogli',
                mood: 'creativo, sognante, determinato',
                themes: ['creatività', 'immaginazione', 'arte'],
                image_generation_status: 'completed',
                image_url: '/api/images/scene-1-2.jpg'
              }
            ]
          },
          {
            id: '2',
            userId: user.id,
            title: 'Storia Personale',
            description: 'Video dalla mia biografia',
            status: 'processing',
            createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            updatedAt: new Date().toISOString(),
            textContent: 'Sono nato in una piccola città...',
            generatedImages: [],
            generatedAudio: [],
            progress: 65,
            processingStep: {
              current: 'Generazione audio',
              total: 4,
              completed: 2,
              currentOperation: 'Sintesi vocale in corso...'
            }
          },
          {
            id: '3',
            userId: user.id,
            title: 'Racconto Fantastico',
            description: 'Una storia di magia e avventura',
            status: 'draft',
            createdAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            updatedAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            textContent: 'C\'era una volta in un regno incantato...',
            generatedImages: [],
            generatedAudio: [],
            progress: 0
          }
        ];
        setProjects(mockProjects);
      } else {
        setProjects(realProjects);
      }
    } catch (error) {
      console.error('Errore caricamento progetti:', error);
      toast.error('Errore nel caricamento dei progetti');
      // In caso di errore, mostra comunque i dati mock
      setProjects([]);
    } finally {
      setIsLoading(false);
    }
  }, [user.id]);

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Pause className="w-4 h-4 text-gray-400" />;
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
      default:
        return 'Bozza';
    }
  };

  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(dateString));
  };
  const handleDeleteProject = async (projectId: string) => {
    if (!window.confirm('Sei sicuro di voler eliminare questo progetto?')) return;
    
    try {
      await apiService.deleteProject(projectId);
      setProjects(projects.filter(p => p.id !== projectId));
      toast.success('Progetto eliminato');
    } catch (error) {
      toast.error('Errore eliminazione progetto');
    }
  };

  const ProjectCard: React.FC<{ project: Project }> = ({ project }) => {
    const [showMenu, setShowMenu] = useState(false);

    return (
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="card hover:shadow-lg transition-all duration-200 group"
      >
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {project.title}
            </h3>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {project.description}
            </p>
          </div>
          
          <div className="relative ml-4">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
            >
              <MoreVertical className="w-4 h-4 text-gray-400" />
            </button>
            
            <AnimatePresence>
              {showMenu && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg z-10 w-48"
                >
                  <button
                    onClick={() => {
                      navigate(`/project/${project.id}`);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-2"
                  >
                    <Eye className="w-4 h-4" />
                    <span>Visualizza</span>
                  </button>
                  
                  {project.finalVideo && (
                    <button
                      onClick={() => {
                        window.open(project.finalVideo!.url, '_blank');
                        setShowMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-2"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download Video</span>
                    </button>
                  )}
                  
                  <button
                    onClick={() => {
                      handleDeleteProject(project.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left hover:bg-red-50 text-red-600 flex items-center space-x-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Elimina</span>
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Status */}
        <div className="flex items-center space-x-2 mb-4">
          {getStatusIcon(project.status)}
          <span className="text-sm font-medium text-gray-700">
            {getStatusText(project.status)}
          </span>
          {project.status === 'processing' && project.processingStep && (
            <span className="text-sm text-gray-500">
              - {project.processingStep.currentOperation}
            </span>
          )}
        </div>

        {/* Progress Bar */}
        {project.progress > 0 && (
          <div className="mb-4">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-gray-500">Progresso</span>
              <span className="text-xs text-gray-500">{project.progress}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${project.progress}%` }}
              />
            </div>
          </div>
        )}        {/* Footer */}
        <div className="flex justify-between items-center text-sm text-gray-500">
          <span>Creato {formatDate(project.createdAt)}</span>
          {project.finalVideo && (
            <button
              onClick={() => navigate(`/project/${project.id}`)}
              className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 font-medium"
            >
              <Play className="w-4 h-4" />
              <span>Riproduci</span>
            </button>
          )}
        </div>

        {/* Scene Preview */}
        {project.scenes && project.scenes.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <SceneViewer 
              scenes={project.scenes.slice(0, 2)} 
              title={`Scene (${project.scenes.length})`}
            />
            {project.scenes.length > 2 && (
              <button
                onClick={() => navigate(`/project/${project.id}`)}
                className="text-sm text-primary-600 hover:text-primary-700 mt-2"
              >
                Vedi tutte le {project.scenes.length} scene →
              </button>
            )}
          </div>
        )}
      </motion.div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                I Tuoi Progetti
              </h1>
              <p className="text-gray-600 mt-2">
                Gestisci e monitora i tuoi progetti di generazione multimediale
              </p>
            </div>
            
            <button
              onClick={() => setShowUpload(true)}
              className="btn-primary mt-4 md:mt-0 flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Nuovo Progetto</span>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Cerca progetti..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-10"
            />
          </div>
          
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field pl-10 pr-8"
            >
              <option value="all">Tutti gli stati</option>
              <option value="draft">Bozze</option>
              <option value="processing">In elaborazione</option>
              <option value="completed">Completati</option>
              <option value="error">Errori</option>
            </select>
          </div>
        </div>

        {/* Projects Grid */}
        {isLoading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3 mb-4"></div>
                <div className="h-2 bg-gray-200 rounded w-full mb-4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Plus className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchQuery || statusFilter !== 'all' ? 'Nessun progetto trovato' : 'Nessun progetto ancora'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchQuery || statusFilter !== 'all' 
                ? 'Prova a modificare i filtri di ricerca'
                : 'Inizia creando il tuo primo progetto multimediale'
              }
            </p>
            {!searchQuery && statusFilter === 'all' && (
              <button
                onClick={() => setShowUpload(true)}
                className="btn-primary"
              >
                Crea Primo Progetto
              </button>
            )}
          </div>
        ) : (
          <motion.div 
            layout
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            <AnimatePresence>
              {filteredProjects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Stats */}
        <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-gray-900">
              {projects.length}
            </div>
            <div className="text-sm text-gray-600">Progetti Totali</div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-green-600">
              {projects.filter(p => p.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-600">Completati</div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-yellow-600">
              {projects.filter(p => p.status === 'processing').length}
            </div>
            <div className="text-sm text-gray-600">In Elaborazione</div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-gray-600">
              {projects.filter(p => p.status === 'draft').length}
            </div>
            <div className="text-sm text-gray-600">Bozze</div>
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <FileUpload 
              user={user} 
              onClose={() => setShowUpload(false)}
              onSuccess={(project) => {
                setShowUpload(false);
                navigate(`/project/${project.id}`);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;