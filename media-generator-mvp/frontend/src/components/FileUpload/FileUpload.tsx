import React, { useState, useRef } from 'react';
import { apiService } from '../../services/api';
import './FileUpload.css';

interface FileUploadProps {
  onUploadSuccess: (response: any) => void;
  onUploadError: (error: string) => void;
  currentUser: string;
  userMode: 'tool' | 'veo';
}

interface BookOption {
  title: string;
  author: string;
  description: string;
  filename: string;
}

const FileUpload: React.FC<FileUploadProps> = ({ 
  onUploadSuccess, 
  onUploadError, 
  currentUser, 
  userMode 
}) => {
  const [uploadType, setUploadType] = useState<'file' | 'book'>('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedBook, setSelectedBook] = useState<string>('');
  const [projectTitle, setProjectTitle] = useState<string>('');
  const [projectDescription, setProjectDescription] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [availableBooks, setAvailableBooks] = useState<BookOption[]>([]);
  const [booksLoaded, setBooksLoaded] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const bookOptions: BookOption[] = [
    {
      title: "Il Piccolo Principe",
      author: "Antoine de Saint-Exupéry",
      description: "La celebre storia del piccolo principe e delle sue avventure tra i pianeti.",
      filename: "il_piccolo_principe.txt"
    },
    {
      title: "Alice nel Paese delle Meraviglie",
      author: "Lewis Carroll",
      description: "Le fantastiche avventure di Alice in un mondo surreale e magico.",
      filename: "alice_nel_paese_delle_meraviglie.txt"
    },
    {
      title: "La Divina Commedia - Inferno",
      author: "Dante Alighieri",
      description: "Il primo cantico del capolavoro dantesco, il viaggio nell'Inferno.",
      filename: "inferno_dante.txt"
    }
  ];

  const loadAvailableBooks = async () => {
    if (booksLoaded) return;
    
    try {
      // Simula il caricamento dei libri disponibili
      // In un'implementazione reale, questo chiamerebbe l'API
      setAvailableBooks(bookOptions);
      setBooksLoaded(true);
    } catch (error) {
      console.error('Error loading books:', error);
    }
  };

  const handleFileSelect = (file: File) => {
    const allowedTypes = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      onUploadError('Tipo di file non supportato. Usa TXT, PDF o DOCX.');
      return;
    }

    if (file.size > maxSize) {
      onUploadError('File troppo grande. Dimensione massima: 10MB.');
      return;
    }

    setSelectedFile(file);
    if (!projectTitle) {
      setProjectTitle(file.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setDragOver(false);
    
    const file = event.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleBookSelect = (bookFilename: string) => {
    setSelectedBook(bookFilename);
    const book = bookOptions.find(b => b.filename === bookFilename);
    if (book && !projectTitle) {
      setProjectTitle(book.title);
      setProjectDescription(book.description);
    }
  };

  const handleSubmit = async () => {
    if (uploadType === 'file' && !selectedFile) {
      onUploadError('Seleziona un file da caricare.');
      return;
    }

    if (uploadType === 'book' && !selectedBook) {
      onUploadError('Seleziona un libro dal catalogo.');
      return;
    }

    if (!projectTitle.trim()) {
      onUploadError('Inserisci un titolo per il progetto.');
      return;
    }

    setUploading(true);

    try {
      let response;
      
      if (uploadType === 'file') {
        response = await apiService.uploadFile(
          selectedFile!,
          projectTitle,
          projectDescription,
          currentUser,
          userMode
        );
      } else {
        response = await apiService.generateFromBook(
          selectedBook,
          projectTitle,
          projectDescription,
          currentUser,
          userMode
        );
      }

      onUploadSuccess(response);
      
      // Reset form
      setSelectedFile(null);
      setSelectedBook('');
      setProjectTitle('');
      setProjectDescription('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      onUploadError('Errore durante il caricamento. Riprova.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <div className="upload-header">
        <h3>Crea Nuovo Progetto</h3>
        <p>Carica un file di testo o seleziona un libro dal nostro catalogo</p>
      </div>

      <div className="upload-type-selector">
        <button
          className={`type-button ${uploadType === 'file' ? 'active' : ''}`}
          onClick={() => setUploadType('file')}
        >
          Carica File
        </button>
        <button
          className={`type-button ${uploadType === 'book' ? 'active' : ''}`}
          onClick={() => {
            setUploadType('book');
            loadAvailableBooks();
          }}
        >
          Seleziona dal Catalogo
        </button>
      </div>

      {uploadType === 'file' ? (
        <div className="file-upload-section">
          <div
            className={`drop-zone ${dragOver ? 'drag-over' : ''} ${selectedFile ? 'has-file' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileChange}
              accept=".txt,.pdf,.docx"
              style={{ display: 'none' }}
            />
            
            {selectedFile ? (
              <div className="file-selected">
                <div className="file-icon">📄</div>
                <div className="file-info">
                  <h4>{selectedFile.name}</h4>
                  <p>{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button
                  className="remove-file"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = '';
                    }
                  }}
                >
                  ✕
                </button>
              </div>
            ) : (
              <div className="drop-zone-content">
                <div className="upload-icon">⬆️</div>
                <h4>Trascina qui il tuo file o clicca per selezionare</h4>
                <p>Formati supportati: TXT, PDF, DOCX (max 10MB)</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="book-selection-section">
          <h4>Libri Disponibili</h4>
          <div className="books-grid">
            {availableBooks.map((book) => (
              <div
                key={book.filename}
                className={`book-card ${selectedBook === book.filename ? 'selected' : ''}`}
                onClick={() => handleBookSelect(book.filename)}
              >
                <div className="book-icon">📚</div>
                <div className="book-info">
                  <h5>{book.title}</h5>
                  <p className="book-author">di {book.author}</p>
                  <p className="book-description">{book.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="project-details">
        <div className="form-group">
          <label htmlFor="project-title">Titolo Progetto *</label>
          <input
            id="project-title"
            type="text"
            value={projectTitle}
            onChange={(e) => setProjectTitle(e.target.value)}
            placeholder="Inserisci il titolo del progetto"
            maxLength={100}
          />
        </div>

        <div className="form-group">
          <label htmlFor="project-description">Descrizione (opzionale)</label>
          <textarea
            id="project-description"
            value={projectDescription}
            onChange={(e) => setProjectDescription(e.target.value)}
            placeholder="Descrivi brevemente il contenuto o l'obiettivo del progetto"
            maxLength={500}
            rows={3}
          />
        </div>
      </div>

      <div className="upload-actions">
        <button
          className="generate-button"
          onClick={handleSubmit}
          disabled={uploading || (!selectedFile && !selectedBook) || !projectTitle.trim()}
        >
          {uploading ? (
            <>
              <div className="button-spinner"></div>
              Elaborazione in corso...
            </>
          ) : (
            `Genera Contenuto (${userMode.toUpperCase()})`
          )}
        </button>
      </div>

      <div className="upload-info">
        <p><strong>Modalità attuale:</strong> {userMode === 'tool' ? 'Tool (Tradizionale)' : 'Veo (Avanzata)'}</p>
        <p>Il processo di generazione può richiedere alcuni minuti a seconda della lunghezza del testo.</p>
      </div>
    </div>
  );
};

export default FileUpload;
