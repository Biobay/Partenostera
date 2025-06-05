import React, { useState, useEffect } from 'react';
import { Book } from '../../types';
import './BookCatalog.css';

// Mock data per i libri - in produzione questo verrebbe da API
const mockBooks: Book[] = [
  {
    id: '1',
    title: 'Il Nome della Rosa',
    author: 'Umberto Eco',
    description: 'Un mistero medievale ambientato in un monastero, ricco di simbolismo e filosofia.',
    genre: 'Mistero',
    year: 1980,
    pages: 512,
    language: 'it',
    coverUrl: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=300&h=400&fit=crop',
    difficulty: 'advanced',
    estimatedReadingTime: '8-10 ore',
    tags: ['medievale', 'filosofia', 'mistero', 'religione']
  },
  {
    id: '2',
    title: 'Cent\'anni di solitudine',
    author: 'Gabriel García Márquez',
    description: 'La saga della famiglia Buendía attraverso sette generazioni nella cittadina immaginaria di Macondo.',
    genre: 'Realismo Magico',
    year: 1967,
    pages: 448,
    language: 'es',
    coverUrl: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop',
    difficulty: 'advanced',
    estimatedReadingTime: '7-9 ore',
    tags: ['realismo magico', 'famiglia', 'latino america', 'generazioni']
  },
  {
    id: '3',
    title: '1984',
    author: 'George Orwell',
    description: 'Una distopia che esplora i temi della sorveglianza, del totalitarismo e della manipolazione della verità.',
    genre: 'Distopia',
    year: 1949,
    pages: 328,
    language: 'en',
    coverUrl: 'https://images.unsplash.com/photo-1495640388908-05fa85288e61?w=300&h=400&fit=crop',
    difficulty: 'intermediate',
    estimatedReadingTime: '5-7 ore',
    tags: ['distopia', 'politica', 'sorveglianza', 'futuro']
  },
  {
    id: '4',
    title: 'Orgoglio e Pregiudizio',
    author: 'Jane Austen',
    description: 'Una storia d\'amore classica che esplora temi di classe sociale, matrimonio e moralità nell\'Inghilterra del XIX secolo.',
    genre: 'Romanzo',
    year: 1813,
    pages: 432,
    language: 'en',
    coverUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop',
    difficulty: 'intermediate',
    estimatedReadingTime: '6-8 ore',
    tags: ['romantico', 'società', 'matrimonio', 'inghilterra']
  },
  {
    id: '5',
    title: 'Il Piccolo Principe',
    author: 'Antoine de Saint-Exupéry',
    description: 'Una favola poetica che racconta l\'incontro tra un aviatore e un piccolo principe proveniente da un altro pianeta.',
    genre: 'Favola',
    year: 1943,
    pages: 96,
    language: 'fr',
    coverUrl: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=300&h=400&fit=crop',
    difficulty: 'beginner',
    estimatedReadingTime: '2-3 ore',
    tags: ['favola', 'filosofia', 'amicizia', 'crescita']
  },
  {
    id: '6',
    title: 'Don Chisciotte',
    author: 'Miguel de Cervantes',
    description: 'Le avventure dell\'hidalgo Don Chisciotte e del suo fedele scudiero Sancho Panza.',
    genre: 'Avventura',
    year: 1605,
    pages: 863,
    language: 'es',
    coverUrl: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop',
    difficulty: 'advanced',
    estimatedReadingTime: '12-15 ore',
    tags: ['avventura', 'cavalleresco', 'spagna', 'satira']
  }
];

interface BookCatalogProps {
  onSelectBook?: (book: Book) => void;
  selectedBooks?: string[];
  multiSelect?: boolean;
  showDescription?: boolean;
  className?: string;
}

const BookCatalog: React.FC<BookCatalogProps> = ({
  onSelectBook,
  selectedBooks = [],
  multiSelect = false,
  showDescription = true,
  className = '',
}) => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'title' | 'author' | 'year' | 'pages'>('title');
  useEffect(() => {
    // Simula il caricamento dei libri
    setTimeout(() => {
      setBooks(mockBooks);
      setLoading(false);
    }, 1000);
  }, []);

  const categories = Array.from(new Set(books.map(book => book.genre)));
  
  const filteredBooks = books.filter(book => {
    const matchesSearch = book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         book.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         book.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || book.genre === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const sortedBooks = [...filteredBooks].sort((a, b) => {
    switch (sortBy) {
      case 'title':
        return a.title.localeCompare(b.title);
      case 'author':
        return a.author.localeCompare(b.author);
      case 'year':
        return b.year - a.year;
      case 'pages':
        return a.pages - b.pages;
      default:
        return 0;
    }
  });

  const handleSelectBook = (book: Book) => {
    onSelectBook?.(book);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'Principiante';
      case 'intermediate':
        return 'Intermedio';
      case 'advanced':
        return 'Avanzato';
      default:
        return difficulty;
    }
  };

  if (loading) {
    return (
      <div className="book-catalog-loading">
        <div className="loading-spinner"></div>
        <p>Caricamento catalogo libri...</p>
      </div>
    );
  }

  return (
    <div className={`book-catalog ${className}`}>
      <div className="catalog-header">
        <h2 className="catalog-title">Catalogo Libri</h2>
        <p className="catalog-subtitle">
          Scegli i libri da cui generare i tuoi video. Abbiamo {books.length} libri disponibili.
        </p>
      </div>

      <div className="catalog-filters">
        <div className="search-box">
          <svg className="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="M21 21l-4.35-4.35"></path>
          </svg>
          <input
            type="text"
            placeholder="Cerca per titolo, autore o tag..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-controls">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="category-select"
          >
            <option value="all">Tutti i generi</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="sort-select"
          >
            <option value="title">Ordina per Titolo</option>
            <option value="author">Ordina per Autore</option>
            <option value="year">Ordina per Anno</option>
            <option value="pages">Ordina per Pagine</option>
          </select>
        </div>
      </div>

      <div className="books-grid">
        {sortedBooks.map(book => (
          <div
            key={book.id}
            className={`book-card ${selectedBooks.includes(book.id) ? 'selected' : ''}`}
            onClick={() => handleSelectBook(book)}
          >
            <div className="book-cover">
              <img src={book.coverUrl} alt={book.title} />
              <div className="book-overlay">
                <button className="select-button">
                  {selectedBooks.includes(book.id) ? 'Selezionato' : 'Seleziona'}
                </button>
              </div>
            </div>

            <div className="book-info">
              <h3 className="book-title">{book.title}</h3>
              <p className="book-author">di {book.author}</p>
              
              <div className="book-meta">
                <span className="book-year">{book.year}</span>
                <span className="book-pages">{book.pages} pagine</span>
                <span className="book-time">{book.estimatedReadingTime}</span>
              </div>

              <div className="book-tags">
                <span className={`difficulty-tag ${getDifficultyColor(book.difficulty)}`}>
                  {getDifficultyLabel(book.difficulty)}
                </span>
                <span className="genre-tag">{book.genre}</span>
              </div>

              {showDescription && (
                <p className="book-description">{book.description}</p>
              )}

              <div className="book-language">
                <span className="language-flag">
                  {book.language === 'it' ? '🇮🇹' : 
                   book.language === 'en' ? '🇬🇧' : 
                   book.language === 'es' ? '🇪🇸' : 
                   book.language === 'fr' ? '🇫🇷' : '🌍'}
                </span>
                <span className="language-name">
                  {book.language === 'it' ? 'Italiano' : 
                   book.language === 'en' ? 'Inglese' : 
                   book.language === 'es' ? 'Spagnolo' : 
                   book.language === 'fr' ? 'Francese' : book.language}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {sortedBooks.length === 0 && (
        <div className="no-results">
          <div className="no-results-icon">📚</div>
          <h3>Nessun libro trovato</h3>
          <p>Prova a modificare i filtri di ricerca per trovare altri libri.</p>
        </div>
      )}
    </div>
  );
};

export default BookCatalog;
