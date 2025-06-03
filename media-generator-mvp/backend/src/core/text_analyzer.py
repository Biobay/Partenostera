import re
import spacy
import nltk
from typing import List, Dict, Tuple
from dataclasses import dataclass
import logging

# Download required NLTK data
try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')

@dataclass
class TextSequence:
    """Represents a narrative sequence from the text"""
    id: int
    text: str
    summary: str
    characters: List[str]
    location: str
    time_period: str
    emotions: List[str]
    action_level: float  # 0-1 scale

class TextAnalyzer:
    """Analyzes text and breaks it into coherent narrative sequences"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize spaCy model for Italian
        try:
            self.nlp = spacy.load("it_core_news_sm")
        except OSError:
            # Fallback to English if Italian model not available
            self.logger.warning("Italian spaCy model not found, using English")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.error("No spaCy models available")
                self.nlp = None
    
    def analyze_text(self, text: str, max_sequences: int = 20) -> List[TextSequence]:
        """
        Analyze text and break it into narrative sequences
        
        Args:
            text: Input text to analyze
            max_sequences: Maximum number of sequences to generate
            
        Returns:
            List of TextSequence objects
        """
        try:
            # Clean and preprocess text
            cleaned_text = self._clean_text(text)
            
            # Split into paragraphs
            paragraphs = self._split_into_paragraphs(cleaned_text)
            
            # Group paragraphs into logical sequences
            sequences = self._create_sequences(paragraphs, max_sequences)
            
            # Analyze each sequence
            analyzed_sequences = []
            for i, seq_text in enumerate(sequences):
                sequence = self._analyze_sequence(i, seq_text)
                analyzed_sequences.append(sequence)
            
            return analyzed_sequences
            
        except Exception as e:
            self.logger.error(f"Error analyzing text: {str(e)}")
            # Return a single sequence with the entire text as fallback
            return [TextSequence(
                id=0,
                text=text[:1000],  # Limit to first 1000 chars
                summary="Testo completo",
                characters=[],
                location="Non specificato",
                time_period="Non specificato",
                emotions=["neutrale"],
                action_level=0.5
            )]
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)
        
        return text.strip()
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into meaningful paragraphs"""
        # Split by double newlines or periods followed by capital letters
        paragraphs = re.split(r'\n\s*\n|(?<=\.)\s+(?=[A-Z])', text)
        
        # Filter out very short paragraphs
        meaningful_paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 50]
        
        return meaningful_paragraphs
    
    def _create_sequences(self, paragraphs: List[str], max_sequences: int) -> List[str]:
        """Group paragraphs into logical narrative sequences"""
        if len(paragraphs) <= max_sequences:
            return paragraphs
        
        # Calculate how many paragraphs per sequence
        paragraphs_per_sequence = len(paragraphs) // max_sequences
        sequences = []
        
        for i in range(0, len(paragraphs), paragraphs_per_sequence):
            sequence_paragraphs = paragraphs[i:i + paragraphs_per_sequence]
            sequence_text = ' '.join(sequence_paragraphs)
            sequences.append(sequence_text)
            
            if len(sequences) >= max_sequences:
                break
        
        return sequences
    
    def _analyze_sequence(self, sequence_id: int, text: str) -> TextSequence:
        """Analyze a single sequence to extract metadata"""
        try:
            if self.nlp is None:
                return self._fallback_analysis(sequence_id, text)
            
            doc = self.nlp(text)
            
            # Extract characters (person names)
            characters = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "PER"]]
            characters = list(set(characters))  # Remove duplicates
            
            # Extract locations
            locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
            location = locations[0] if locations else "Non specificato"
            
            # Extract time references
            time_entities = [ent.text for ent in doc.ents if ent.label_ in ["DATE", "TIME"]]
            time_period = time_entities[0] if time_entities else "Non specificato"
            
            # Generate summary (first sentence or truncated text)
            sentences = [sent.text.strip() for sent in doc.sents]
            summary = sentences[0] if sentences else text[:100] + "..."
            
            # Estimate emotions and action level
            emotions = self._estimate_emotions(text)
            action_level = self._estimate_action_level(text)
            
            return TextSequence(
                id=sequence_id,
                text=text,
                summary=summary,
                characters=characters,
                location=location,
                time_period=time_period,
                emotions=emotions,
                action_level=action_level
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing sequence {sequence_id}: {str(e)}")
            return self._fallback_analysis(sequence_id, text)
    
    def _fallback_analysis(self, sequence_id: int, text: str) -> TextSequence:
        """Fallback analysis when NLP fails"""
        summary = text[:100] + "..." if len(text) > 100 else text
        
        return TextSequence(
            id=sequence_id,
            text=text,
            summary=summary,
            characters=[],
            location="Non specificato",
            time_period="Non specificato",
            emotions=["neutrale"],
            action_level=0.5
        )
    
    def _estimate_emotions(self, text: str) -> List[str]:
        """Estimate emotions based on keywords"""
        emotion_keywords = {
            "gioia": ["felice", "gioia", "allegro", "contento", "sorriso", "ridere"],
            "tristezza": ["triste", "dolore", "piangere", "lacrime", "sofferenza"],
            "paura": ["paura", "terrore", "spavento", "ansia", "preoccupazione"],
            "rabbia": ["rabbia", "arrabbiato", "furioso", "collera", "ira"],
            "sorpresa": ["sorpresa", "stupore", "meraviglia", "incredibile"],
            "amore": ["amore", "amare", "innamorato", "affetto", "cuore"]
        }
        
        text_lower = text.lower()
        detected_emotions = []
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions if detected_emotions else ["neutrale"]
    
    def _estimate_action_level(self, text: str) -> float:
        """Estimate action level from 0 (calm) to 1 (high action)"""
        action_keywords = [
            "correre", "saltare", "combattere", "lottare", "fuggire", "inseguire",
            "veloce", "rapido", "fretta", "urgenza", "pericolo", "battaglia",
            "esplosione", "gridare", "urlare"
        ]
        
        text_lower = text.lower()
        action_count = sum(1 for keyword in action_keywords if keyword in text_lower)
        
        # Normalize to 0-1 scale
        max_expected_keywords = 5
        action_level = min(action_count / max_expected_keywords, 1.0)
        
        return action_level
