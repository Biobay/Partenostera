import os
import json
import uuid
import logging
import shutil
from typing import List, Dict, Optional, Any
from datetime import datetime
from fastapi import UploadFile
import PyPDF2
import docx

class FileHandler:
    """Handles file operations for the media generator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        self.books_path = "data/books"
        self.outputs_path = "data/outputs"
        self.temp_path = "data/temp"
        
        for path in [self.books_path, self.outputs_path, self.temp_path]:
            os.makedirs(path, exist_ok=True)
        
        # Initialize with sample books if none exist
        self._initialize_sample_books()
    
    async def process_uploaded_file(self, file: UploadFile) -> str:
        """Process uploaded file and extract text content"""
        try:
            # Validate file
            if not file.filename:
                raise ValueError("No filename provided")
            
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            if file_extension not in ['.txt', '.pdf', '.docx']:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Save uploaded file temporarily
            temp_filename = f"{uuid.uuid4()}{file_extension}"
            temp_filepath = os.path.join(self.temp_path, temp_filename)
            
            with open(temp_filepath, 'wb') as temp_file:
                content = await file.read()
                temp_file.write(content)
            
            # Extract text based on file type
            text_content = self._extract_text_from_file(temp_filepath, file_extension)
            
            # Cleanup temp file
            os.remove(temp_filepath)
            
            return text_content
            
        except Exception as e:
            self.logger.error(f"Error processing uploaded file: {str(e)}")
            raise ValueError(f"Failed to process file: {str(e)}")
    
    def _extract_text_from_file(self, filepath: str, file_extension: str) -> str:
        """Extract text from different file formats"""
        try:
            if file_extension == '.txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_extension == '.pdf':
                text = ""
                with open(filepath, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            
            elif file_extension == '.docx':
                doc = docx.Document(filepath)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            
            else:
                raise ValueError(f"Unsupported file extension: {file_extension}")
                
        except Exception as e:
            self.logger.error(f"Error extracting text from {filepath}: {str(e)}")
            raise ValueError(f"Failed to extract text: {str(e)}")
    
    def get_available_books(self) -> List[Dict[str, Any]]:
        """Get list of available books from catalog"""
        try:
            books = []
            catalog_file = os.path.join(self.books_path, "catalog.json")
            
            if os.path.exists(catalog_file):
                with open(catalog_file, 'r', encoding='utf-8') as f:
                    catalog = json.load(f)
                    books = catalog.get('books', [])
            
            # Add file existence check
            available_books = []
            for book in books:
                book_path = os.path.join(self.books_path, book.get('file_path', ''))
                if os.path.exists(book_path):
                    available_books.append(book)
            
            return available_books
            
        except Exception as e:
            self.logger.error(f"Error getting available books: {str(e)}")
            return []
    
    def get_book_content(self, book_id: str) -> str:
        """Get content of a specific book by ID"""
        try:
            books = self.get_available_books()
            book = next((b for b in books if b['id'] == book_id), None)
            
            if not book:
                raise ValueError(f"Book with ID {book_id} not found")
            
            book_path = os.path.join(self.books_path, book['file_path'])
            file_extension = os.path.splitext(book_path)[1].lower()
            
            return self._extract_text_from_file(book_path, file_extension)
            
        except Exception as e:
            self.logger.error(f"Error getting book content for {book_id}: {str(e)}")
            raise ValueError(f"Failed to get book content: {str(e)}")
    
    def save_project(self, project_data: Dict[str, Any]) -> str:
        """Save project data and return project ID"""
        try:
            project_id = project_data.get('project_id', str(uuid.uuid4()))
            project_dir = os.path.join(self.outputs_path, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # Save project metadata
            metadata_file = os.path.join(project_dir, "metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, default=str)
            
            return project_id
            
        except Exception as e:
            self.logger.error(f"Error saving project: {str(e)}")
            raise ValueError(f"Failed to save project: {str(e)}")
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all saved projects"""
        try:
            projects = []
            
            if not os.path.exists(self.outputs_path):
                return projects
            
            for project_dir in os.listdir(self.outputs_path):
                project_path = os.path.join(self.outputs_path, project_dir)
                
                if os.path.isdir(project_path):
                    metadata_file = os.path.join(project_path, "metadata.json")
                    
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                project_data = json.load(f)
                                
                            # Add summary info
                            project_summary = {
                                'id': project_dir,
                                'title': project_data.get('title', 'Untitled'),
                                'status': project_data.get('status', 'unknown'),
                                'created_at': project_data.get('created_at'),
                                'mode': project_data.get('mode', 'tool'),
                                'video_path': project_data.get('video_path'),
                                'quality_score': project_data.get('quality_score')
                            }
                            
                            projects.append(project_summary)
                            
                        except Exception as e:
                            self.logger.warning(f"Error reading project {project_dir}: {str(e)}")
            
            # Sort by creation date (newest first)
            projects.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return projects
            
        except Exception as e:
            self.logger.error(f"Error getting all projects: {str(e)}")
            return []
    
    def get_project_details(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific project"""
        try:
            project_path = os.path.join(self.outputs_path, project_id)
            metadata_file = os.path.join(project_path, "metadata.json")
            
            if not os.path.exists(metadata_file):
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Add file URLs for web access
            if project_data.get('video_path'):
                relative_path = os.path.relpath(project_data['video_path'], self.outputs_path)
                project_data['video_url'] = f"/static/{relative_path}"
            
            return project_data
            
        except Exception as e:
            self.logger.error(f"Error getting project details for {project_id}: {str(e)}")
            return None
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all its files"""
        try:
            project_path = os.path.join(self.outputs_path, project_id)
            
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
                self.logger.info(f"Deleted project {project_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting project {project_id}: {str(e)}")
            return False
    
    def _initialize_sample_books(self):
        """Initialize with sample books if catalog doesn't exist"""
        catalog_file = os.path.join(self.books_path, "catalog.json")
        
        if not os.path.exists(catalog_file):
            # Create sample books
            sample_books = [
                {
                    "id": "sample_1",
                    "title": "La Piccola Storia",
                    "author": "Autore Demo",
                    "description": "Una breve storia di esempio per testare il sistema",
                    "language": "it",
                    "word_count": 150,
                    "file_path": "sample_1.txt"
                },
                {
                    "id": "sample_2", 
                    "title": "Avventura Fantastica",
                    "author": "Scrittore Virtuale",
                    "description": "Un'avventura fantasy per dimostrare le capacità narrative",
                    "language": "it",
                    "word_count": 200,
                    "file_path": "sample_2.txt"
                }
            ]
            
            # Save catalog
            catalog = {"books": sample_books}
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            
            # Create sample book files
            sample_1_content = """C'era una volta, in un piccolo villaggio di montagna, una giovane ragazza di nome Luna. 
            
Luna aveva sempre sognato di esplorare il mondo oltre le montagne che circondavano il suo villaggio. Un giorno, mentre raccoglieva erbe medicinali nel bosco, trovò una mappa misteriosa nascosta in un vecchio tronco d'albero.

La mappa mostrava un sentiero segreto che conduceva a una valle nascosta, dove si diceva crescesse un fiore magico in grado di realizzare i desideri. Luna decise di seguire la mappa e iniziò la sua avventura.

Dopo giorni di cammino attraverso sentieri impervi, Luna raggiunse finalmente la valle nascosta. Lì, al centro di un prato fiorito, trovò il fiore magico che brillava di una luce dorata.

Con il cuore pieno di speranza, Luna espresse il suo desiderio: portare prosperità e felicità al suo villaggio. Il fiore si dissolse in una pioggia di stelle dorate, e Luna sapeva che il suo desiderio si sarebbe avverato."""
            
            sample_2_content = """In un regno lontano, il giovane mago Elias si preparava per la sua prima missione importante. 
            
Il Re aveva chiesto a tutti i maghi del regno di trovare il Cristallo della Saggezza, un artefatto perduto che poteva proteggere il regno dall'oscurità che si stava avvicinando.

Elias partì con il suo fedele drago Azzurro, volando sopra foreste incantate e montagne ghiacciate. Durante il viaggio, incontrarono una strega antica che li mise alla prova con tre enigmi difficili.

"Solo chi possiede vera saggezza può trovare il cristallo," disse la strega. Elias risolse tutti gli enigmi usando non solo la magia, ma anche la gentilezza e l'intelligenza.

Impressionata, la strega rivelò la posizione del cristallo: era nascosto nel cuore della Foresta di Cristallo, protetto da un guardiano benevolo. Elias e Azzurro si diressero verso la foresta, pronti per l'ultima parte della loro avventura.

Nel profondo della foresta, trovarono il guardiano, un unicorno dorato che custodiva il Cristallo della Saggezza. L'unicorno, riconoscendo la purezza del cuore di Elias, gli consegnò il cristallo.

Elias tornò al regno come un eroe, e il Cristallo della Saggezza protesse tutti dall'oscurità per molti anni a venire."""
            
            # Save sample books
            with open(os.path.join(self.books_path, "sample_1.txt"), 'w', encoding='utf-8') as f:
                f.write(sample_1_content)
            
            with open(os.path.join(self.books_path, "sample_2.txt"), 'w', encoding='utf-8') as f:
                f.write(sample_2_content)
            
            self.logger.info("Initialized sample books")
