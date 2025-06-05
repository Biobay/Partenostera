import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  FileText, 
  X, 
  AlertCircle, 
  CheckCircle, 
  Loader2,
  BookOpen,
  FileIcon
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { User, Project, UploadProgress } from '../../types';
import { apiService } from '../../services/api';

interface FileUploadProps {
  user: User;
  onClose: () => void;
  onSuccess: (project: Project) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ user, onClose, onSuccess }) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({ loaded: 0, total: 0, percentage: 0 });
  const [textContent, setTextContent] = useState('');
  const [projectTitle, setProjectTitle] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      if (file.size > 50 * 1024 * 1024) { // 50MB max
        toast.error('Il file è troppo grande. Dimensione massima: 50MB');
        return;
      }
      
      setUploadedFile(file);
      setProjectTitle(file.name.replace(/\.[^/.]+$/, ""));
      handleFileUpload(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/markdown': ['.md']
    },
    maxFiles: 1
  });

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const result = await apiService.uploadTextFile(file, setUploadProgress);
      setTextContent(result.textContent);
      toast.success('File caricato con successo!');
    } catch (error) {
      console.error('Errore upload:', error);
      toast.error('Errore durante il caricamento del file');
    } finally {
      setIsUploading(false);
    }
  };

  const handleTextAreaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTextContent(e.target.value);
    if (!projectTitle && e.target.value.length > 0) {
      // Usa le prime parole come titolo automatico
      const words = e.target.value.trim().split(' ').slice(0, 6);
      setProjectTitle(words.join(' ') + (e.target.value.split(' ').length > 6 ? '...' : ''));
    }
  };
  const handleSubmit = async () => {
    if (!textContent.trim()) {
      toast.error('Inserisci del testo o carica un file');
      return;
    }

    if (!projectTitle.trim()) {
      toast.error('Inserisci un titolo per il progetto');
      return;
    }

    setIsProcessing(true);
    try {
      // Prima crea il progetto
      const project = await apiService.createProject({
        userId: user.id,
        title: projectTitle,
        description: projectDescription || `Progetto generato da ${user.name}`,
        textContent: textContent
      });

      // Poi analizza il testo per estrarre le scene
      try {
        const scenes = await apiService.analyzeTextScenes(textContent);
        console.log('Scene estratte:', scenes);
        
        // Aggiorna il progetto con le scene
        if (scenes.length > 0) {
          await apiService.updateProject(project.id, { scenes });
          project.scenes = scenes;
        }
        
        toast.success(`Progetto creato con successo! ${scenes.length > 0 ? `Estratte ${scenes.length} scene.` : ''}`);
      } catch (sceneError) {
        console.warn('Errore nell\'analisi delle scene:', sceneError);
        toast.success('Progetto creato con successo! (Analisi scene fallita)');
      }

      onSuccess(project);
    } catch (error) {
      console.error('Errore creazione progetto:', error);
      toast.error('Errore durante la creazione del progetto');
    } finally {
      setIsProcessing(false);
    }
  };

  const clearFile = () => {
    setUploadedFile(null);
    setTextContent('');
    setUploadProgress({ loaded: 0, total: 0, percentage: 0 });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Carica Contenuto</h2>
          <p className="text-gray-600 mt-1">
            Carica un file di testo o inserisci manualmente il contenuto
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <div className="space-y-6">
        {/* File Upload Area */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Carica File
          </label>
          
          <div
            {...getRootProps()}
            className={`upload-zone cursor-pointer ${
              isDragActive ? 'drag-active' : ''
            } ${uploadedFile ? 'border-green-300 bg-green-50' : ''}`}
          >
            <input {...getInputProps()} />
            
            <AnimatePresence mode="wait">
              {isUploading ? (
                <motion.div
                  key="uploading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center"
                >
                  <Loader2 className="w-12 h-12 text-primary-600 mx-auto mb-4 animate-spin" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    Caricamento in corso...
                  </p>
                  <div className="progress-bar w-64 mx-auto mb-2">
                    <div 
                      className="progress-fill"
                      style={{ width: `${uploadProgress.percentage}%` }}
                    />
                  </div>
                  <p className="text-sm text-gray-600">
                    {uploadProgress.percentage}% - {formatFileSize(uploadProgress.loaded)} / {formatFileSize(uploadProgress.total)}
                  </p>
                </motion.div>
              ) : uploadedFile ? (
                <motion.div
                  key="uploaded"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center"
                >
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    File caricato con successo!
                  </p>
                  <div className="flex items-center justify-center space-x-2 mb-4">
                    <FileIcon className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600">{uploadedFile.name}</span>
                    <span className="text-sm text-gray-500">({formatFileSize(uploadedFile.size)})</span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      clearFile();
                    }}
                    className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Carica un altro file
                  </button>
                </motion.div>
              ) : (
                <motion.div
                  key="upload"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center"
                >
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    {isDragActive ? 'Rilascia il file qui' : 'Trascina un file qui'}
                  </p>
                  <p className="text-sm text-gray-600 mb-4">
                    oppure clicca per selezionare
                  </p>
                  <div className="flex flex-wrap justify-center gap-2 text-xs text-gray-500">
                    <span className="bg-gray-100 px-2 py-1 rounded">.txt</span>
                    <span className="bg-gray-100 px-2 py-1 rounded">.pdf</span>
                    <span className="bg-gray-100 px-2 py-1 rounded">.doc</span>
                    <span className="bg-gray-100 px-2 py-1 rounded">.docx</span>
                    <span className="bg-gray-100 px-2 py-1 rounded">.md</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* OR Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">oppure</span>
          </div>
        </div>

        {/* Manual Text Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Inserisci Testo Manualmente
          </label>
          <textarea
            value={textContent}
            onChange={handleTextAreaChange}
            placeholder="Incolla o scrivi qui il tuo testo..."
            className="input-field min-h-[200px] resize-y"
            rows={8}
          />
          <div className="flex justify-between items-center mt-2">
            <p className="text-sm text-gray-500">
              {textContent.length} caratteri
            </p>
            {textContent.length > 10000 && (
              <div className="flex items-center space-x-1 text-orange-600">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">Testo molto lungo - considera di dividerlo</span>
              </div>
            )}
          </div>
        </div>

        {/* Project Details */}
        {textContent && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="space-y-4 border-t border-gray-200 pt-6"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Titolo Progetto *
              </label>
              <input
                type="text"
                value={projectTitle}
                onChange={(e) => setProjectTitle(e.target.value)}
                className="input-field"
                placeholder="Inserisci un titolo per il progetto"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descrizione (opzionale)
              </label>
              <textarea
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                className="input-field"
                rows={3}
                placeholder="Aggiungi una descrizione del progetto..."
              />
            </div>

            {/* User Type Info */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                {user.type === 'veo_user' ? (
                  <BookOpen className="w-5 h-5 text-purple-600" />
                ) : (
                  <FileText className="w-5 h-5 text-blue-600" />
                )}
                <span className="font-medium text-gray-900">
                  Modalità: {user.type === 'veo_user' ? 'Veo User' : 'Image Editor'}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                {user.type === 'veo_user' 
                  ? 'Il progetto userà Veo2/3 per generare video di alta qualità direttamente dal testo.'
                  : 'Il progetto genererà immagini sequenziali e audio, poi li combinerà in un video finale.'
                }
              </p>
            </div>
          </motion.div>
        )}

        {/* Actions */}
        <div className="flex space-x-3 pt-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="btn-secondary flex-1"
            disabled={isProcessing}
          >
            Annulla
          </button>
          <button
            onClick={handleSubmit}
            disabled={!textContent.trim() || !projectTitle.trim() || isProcessing}
            className="btn-primary flex-1 flex items-center justify-center space-x-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Creazione...</span>
              </>
            ) : (
              <>
                <span>Crea Progetto</span>
                <Upload className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;