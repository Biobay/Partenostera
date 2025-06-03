# MediaGen MVP - Generazione Automatica di Contenuti Multimediali

Un sistema completo per la generazione automatica di contenuti multimediali (immagini, audio, video) a partire da testo. L'applicazione supporta due modalità di funzionamento: **Tool** (strumenti tradizionali) e **Veo** (pipeline avanzata Veo2/3).

## 🎯 Caratteristiche Principali

### Core Features
- **Analisi del Testo**: Estrazione automatica di sequenze narrative cronologiche
- **Generazione Immagini**: Stable Diffusion con prompt intelligenti
- **Sintesi Audio**: Text-to-Speech con Coqui TTS
- **Creazione Video**: Composizione automatica con MoviePy
- **Validazione Qualità**: Sistema di controllo e punteggio qualità
- **Dashboard Interattiva**: Monitoraggio progetti e visualizzazione risultati

### Modalità Utente
- **Tool Mode**: Generatori tradizionali (Stable Diffusion, TTS standard, MoviePy)
- **Veo Mode**: Pipeline avanzata simulata per Veo2/3

### Input Supportati
- **File di Testo**: TXT, PDF, DOCX (max 10MB)
- **Catalogo Libri**: Collezione preconfigurata di opere classiche italiane

## 🏗️ Architettura

```
media-generator-mvp/
├── backend/                 # API Python FastAPI
│   ├── src/
│   │   ├── core/           # Motori di generazione
│   │   ├── models/         # Modelli dati
│   │   ├── services/       # Logica business
│   │   └── utils/          # Utilities
│   ├── data/               # Dati persistenti
│   ├── requirements.txt    # Dipendenze Python
│   └── config.yaml         # Configurazione
├── frontend/                # UI React TypeScript
│   ├── src/
│   │   ├── components/     # Componenti React
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript definitions
│   └── package.json        # Dipendenze Node.js
└── docker-compose.yml      # Orchestrazione container
```

## 🚀 Quick Start

### Prerequisiti
- Docker & Docker Compose
- Git
- 8GB+ RAM disponibili
- GPU NVIDIA (consigliata per Stable Diffusion)

### Installazione

1. **Clone del repository**
```bash
git clone <repository-url>
cd media-generator-mvp
```

2. **Avvio con Docker**
```bash
docker-compose up --build
```

3. **Accesso all'applicazione**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- Documentazione API: http://localhost:8000/docs

### Setup Sviluppo Locale

#### Backend
```bash
cd backend

# Ambiente virtuale Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate     # Windows

# Installazione dipendenze
pip install -r requirements.txt

# Avvio server sviluppo
uvicorn src.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend

# Installazione dipendenze
npm install

# Avvio server sviluppo
npm start
```

## 💻 Utilizzo

### 1. Selezione Utente e Modalità
- Scegli l'utente attivo (Mario, Anna, Luca, Sofia)
- Seleziona la modalità di generazione:
  - **Tool**: Pipeline tradizionale
  - **Veo**: Pipeline avanzata

### 2. Caricamento Contenuto
- **File Upload**: Trascina un file TXT/PDF/DOCX
- **Catalogo**: Seleziona da opere preconfigurate

### 3. Generazione
- Inserisci titolo e descrizione progetto
- Avvia la generazione automatica
- Monitora il progresso in tempo reale

### 4. Risultati
- Visualizza video generati nella dashboard
- Scarica contenuti multimediali
- Gestisci progetti esistenti

## 🔧 Configurazione

### Backend (config.yaml)
```yaml
# Percorsi file
paths:
  books: "data/books"
  uploads: "data/uploads"
  outputs: "data/outputs"

# Modelli AI
models:
  stable_diffusion: "runwayml/stable-diffusion-v1-5"
  tts_model: "tts_models/en/ljspeech/tacotron2-DDC"

# Generazione video
video:
  fps: 24
  resolution: [1280, 720]
  duration_per_image: 3.0

# Validazione
validation:
  min_quality_score: 0.7
  content_filter: true
```

### Frontend (Environment Variables)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## 📊 API Endpoints

### Progetti
- `GET /projects/{user_id}` - Lista progetti utente
- `POST /projects` - Crea nuovo progetto
- `DELETE /projects/{project_id}` - Elimina progetto

### Generazione
- `POST /generate/file` - Genera da file
- `POST /generate/book` - Genera da catalogo
- `GET /generate/status/{project_id}` - Stato generazione

### Utilità
- `GET /books` - Lista libri disponibili
- `GET /health` - Health check sistema

Documentazione completa: http://localhost:8000/docs

## 🎨 Componenti Frontend

### Dashboard
- Visualizzazione progetti utente
- Player video integrato
- Gestione progresso generazione
- Eliminazione progetti

### FileUpload
- Drag & drop file
- Selezione catalogo libri
- Validazione input
- Feedback utente

### UserSelector
- Selezione utente attivo
- Modalità generazione
- Configurazione preferenze

### VideoPlayer
- Controlli personalizzati
- Fullscreen support
- Download video
- Responsive design

## 🔍 Tecnologie Utilizzate

### Backend
- **FastAPI**: Framework web asincrono
- **PyTorch**: ML framework per Stable Diffusion
- **Diffusers**: Libreria Hugging Face per diffusion models
- **Coqui TTS**: Sintesi vocale avanzata
- **MoviePy**: Editing video programmatico
- **spaCy/NLTK**: Elaborazione linguaggio naturale
- **Pydantic**: Validazione dati
- **AsyncIO**: Programmazione asincrona

### Frontend
- **React 18**: Libreria UI con hooks
- **TypeScript**: Type safety e developer experience
- **CSS3**: Styling moderno con Grid/Flexbox
- **Fetch API**: Comunicazione client-server

### Infrastructure
- **Docker**: Containerizzazione applicazione
- **Docker Compose**: Orchestrazione multi-container
- **Nginx**: Web server e reverse proxy
- **Redis**: Cache e sessioni (opzionale)

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📈 Performance e Scalabilità

### Ottimizzazioni Implementate
- Generazione asincrona in background
- Cache risultati intermedi
- Compressione immagini automatica
- Lazy loading componenti React
- Nginx gzip compression

### Monitoring
- Health checks container
- Logging strutturato
- Metriche performance API
- Error tracking frontend

### Scalabilità
- Architettura microservizi ready
- Cache Redis per sessioni
- Load balancer ready
- Storage esterno configurabile

## 🔒 Sicurezza

### Implementate
- Validazione input rigorosa
- Content filtering per contenuti inappropriati
- CORS policy configurata
- Rate limiting API
- Sanitizzazione file upload
- Security headers HTTP

### Raccomandazioni Produzione
- HTTPS obbligatorio
- Autenticazione JWT
- Database sicuro
- Backup automatici
- Monitoring sicurezza

## 🐛 Troubleshooting

### Problemi Comuni

**Errore GPU non disponibile**
```bash
# Verifica GPU
nvidia-smi
# Installa CUDA Toolkit se necessario
```

**Memoria insufficiente**
```bash
# Ridurre dimensioni batch nei config
# Aumentare swap system
# Usare CPU mode per test
```

**Porte già in uso**
```bash
# Cambia porte in docker-compose.yml
# Verifica processi attivi
lsof -i :8000
```

**Problemi npm**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🤝 Contribuire

### Development Workflow
1. Fork del repository
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

### Coding Standards
- Python: PEP 8, type hints obbligatori
- TypeScript: ESLint + Prettier
- Commit: Conventional Commits
- Testing: 80%+ coverage richiesta

## 📝 Roadmap

### v1.1 (Q1 2024)
- [ ] Autenticazione utenti
- [ ] Upload multipli batch
- [ ] Temi UI personalizzabili
- [ ] Export formati multipli

### v1.2 (Q2 2024)
- [ ] Integrazione Veo2/3 reale
- [ ] Editor video avanzato
- [ ] Collaborazione multi-utente
- [ ] API mobile SDK

### v2.0 (Q3 2024)
- [ ] ML personalizzazione stili
- [ ] Streaming generazione real-time
- [ ] Plugin system
- [ ] Marketplace template

## 📄 Licenza

Questo progetto è sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per dettagli.

## 👥 Team

- **Mario** - Lead Developer & System Architecture
- **Anna** - UI/UX Design & Frontend Development  
- **Luca** - ML Engineering & Backend API
- **Sofia** - DevOps & Infrastructure

## 📞 Supporto

- **Issues**: [GitHub Issues](https://github.com/yourorg/media-generator-mvp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourorg/media-generator-mvp/discussions)
- **Email**: support@mediagen-mvp.com
- **Discord**: [Community Server](https://discord.gg/mediagen)

---

⭐ **Se questo progetto ti è utile, lascia una stella su GitHub!**

## 🙏 Ringraziamenti

- [Hugging Face](https://huggingface.co/) per i modelli pre-allenati
- [Stability AI](https://stability.ai/) per Stable Diffusion
- [Coqui](https://coqui.ai/) per TTS models
- Community open source per framework e librerie

---

*Generazione automatica di contenuti multimediali - Portare le storie alla vita attraverso l'AI* 🎬✨
