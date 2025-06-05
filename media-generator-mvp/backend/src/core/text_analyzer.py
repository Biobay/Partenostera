"""
Text Analyzer Core Module
Integrates text-chunker functionality to analyze text and extract scenes
"""

import asyncio
import os
import json
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Scene(BaseModel):
    elementi_narrativi: str
    personaggi: str
    ambientazione: str
    mood_vibe: str
    azione_in_corso: str

class TextChunk(BaseModel):
    id: str
    content: str
    order: int
    scene: Scene
    image_prompt: str
    audio_text: str

class ScenesResponse(BaseModel):
    scenes: List[Scene]

class TextAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        self.default_model = "google/gemini-2.5-flash-preview-05-20"
        self.target_chunk_size_words = 5000
        self.word_count_slack = 500
        self.min_chunk_size_words = 1000

    async def analyze_text(self, text: str) -> List[TextChunk]:
        """
        Analyze text and return structured chunks with scenes
        """
        try:
            # First, split text into scenes
            scenes = await self._split_text_into_scenes(text)
            
            # Convert scenes to TextChunk objects
            text_chunks = []
            for i, scene in enumerate(scenes):
                # Generate image prompt from scene
                image_prompt = await self._generate_image_prompt(scene)
                
                # Generate audio text from scene
                audio_text = await self._generate_audio_text(scene)
                
                chunk = TextChunk(
                    id=f"chunk_{i+1}",
                    content=f"Scene {i+1}: {scene.azione_in_corso}",
                    order=i + 1,
                    scene=scene,
                    image_prompt=image_prompt,
                    audio_text=audio_text
                )
                text_chunks.append(chunk)
            
            return text_chunks
            
        except Exception as e:
            print(f"Error in text analysis: {e}")
            return []

    async def _split_text_into_scenes(self, text: str) -> List[Scene]:
        """
        Split text into individual scenes using the same logic as text-chunker
        """
        return await self._split_text_into_scenes_logic(text)

    async def _split_text_into_scenes_logic(self, text: str) -> List[Scene]:
        """
        Core logic for splitting text into scenes (matches text-chunker implementation)
        """
        initial_prompt = f"""
Sei un esperto analista letterario e un narratore visivo. Il tuo compito è dividere il seguente testo di narrativa in scene individuali.
Per ogni scena, immagina di scattare un'istantanea da utilizzare per un servizio di generazione di immagini.

Pertanto, per ogni scena, fornisci:
Una scomposizione dettagliata delle componenti visive e narrative della scena con le seguenti chiavi:
    *   `elementi_narrativi`: (stringa) Elementi narrativi chiave presenti (ad esempio, oggetti significativi, simboli).
    *   `personaggi`: (stringa) Personaggi coinvolti, dettagliando il loro aspetto, espressioni ed eventuali interazioni se descritte.
    *   `ambientazione`: (stringa) L'ambientazione e l'ambiente (ad esempio, luogo, ora del giorno, tempo atmosferico, dettagli specifici dell'ambiente circostante).
    *   `mood_vibe`: (stringa) L'atmosfera o il mood generale della scena (ad esempio, teso, misterioso, calmo, gioioso).
    *   `azione_in_corso`: (stringa) L'azione principale, l'evento o le pose dei personaggi che si svolgono nella scena.

Formatta la tua risposta come un array JSON. Ogni oggetto nell'array deve rappresentare una scena e contenere rigorosamente SOLO i seguenti campi: `elementi_narrativi`, `personaggi`, `ambientazione`, `mood_vibe`, e `azione_in_corso`.

Testo da analizzare:
{text}

Assicurati che le scene siano complete e non vengano interrotte a metà frase. Cerca interruzioni narrative naturali.
Concentrati sull'estrazione di dettagli visivi e descrittivi per ogni campo specificato.
NON includere il testo completo della scena nella tua risposta, ma solo i dati strutturati richiesti.
"""

        system_message = "You are a literary analyst expert at identifying scene boundaries in fiction."
        
        try:
            # Call LLM
            llm_content = await self._call_llm(initial_prompt, system_message)
            
            # Extract JSON from response
            json_payload = self._get_json_payload_from_llm_content(llm_content)
            
            # Parse and validate scenes
            scenes = self._parse_and_validate_scenes(json_payload)
            
            return scenes
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"Error in initial scene splitting: {e}")
            # Try with fixer logic if initial fails
            return await self._try_fix_scenes(text, llm_content if 'llm_content' in locals() else "", str(e))
            
        except Exception as e:
            print(f"Unexpected error in scene splitting: {e}")
            return []

    async def _try_fix_scenes(self, original_text: str, failed_llm_content: str, error_message: str) -> List[Scene]:
        """
        Attempt to fix failed scene parsing with a second LLM call
        """
        fixer_prompt = f"""
Il seguente output LLM per la divisione in scene aveva errori di formato:

Output LLM problematico:
{failed_llm_content}

Errore riportato: {error_message}

Correggi e riformatta questo output come un array JSON valido con scene che seguono rigorosamente questo schema:
- elementi_narrativi: stringa
- personaggi: stringa  
- ambientazione: stringa
- mood_vibe: stringa
- azione_in_corso: stringa

Testo originale per riferimento:
{original_text[:1000]}...

Fornisci SOLO l'array JSON corretto, senza altre spiegazioni.
"""
        
        try:
            fixer_content = await self._call_llm(fixer_prompt, "You are an AI assistant specialized in correcting malformed JSON based on a Pydantic schema.")
            json_payload = self._get_json_payload_from_llm_content(fixer_content)
            return self._parse_and_validate_scenes(json_payload)
        except Exception as e:
            print(f"Fixer also failed: {e}")
            return []

    async def _generate_image_prompt(self, scene: Scene) -> str:
        """
        Generate an optimized image prompt from scene data
        """
        prompt = f"""
Basandoti su questa scena, crea un prompt ottimizzato per generazione di immagini:

Elementi narrativi: {scene.elementi_narrativi}
Personaggi: {scene.personaggi}
Ambientazione: {scene.ambientazione}
Mood: {scene.mood_vibe}
Azione: {scene.azione_in_corso}

Crea un prompt conciso e visivo (massimo 200 caratteri) che catturi l'essenza visiva della scena.
"""
        
        try:
            response = await self._call_llm(prompt, "You are an expert at creating visual prompts for image generation.")
            return response.strip()
        except Exception as e:
            print(f"Error generating image prompt: {e}")
            # Fallback prompt
            return f"{scene.personaggi} in {scene.ambientazione}, {scene.azione_in_corso}, {scene.mood_vibe} mood"

    async def _generate_audio_text(self, scene: Scene) -> str:
        """
        Generate audio narration text from scene
        """
        prompt = f"""
Basandoti su questa scena, crea una narrazione audio di 2-3 frasi che descriva la scena:

Elementi narrativi: {scene.elementi_narrativi}
Personaggi: {scene.personaggi}
Ambientazione: {scene.ambientazione}
Mood: {scene.mood_vibe}
Azione: {scene.azione_in_corso}

Crea una narrazione fluida e coinvolgente adatta per audio.
"""
        
        try:
            response = await self._call_llm(prompt, "You are an expert narrator creating audio descriptions.")
            return response.strip()
        except Exception as e:
            print(f"Error generating audio text: {e}")
            # Fallback text
            return f"In questa scena, {scene.azione_in_corso.lower()}"

    async def _call_llm(self, prompt_content: str, system_message: str) -> str:
        """Helper function to make an API call to the LLM."""
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.default_model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt_content},
            ]
        )
        content = response.choices[0].message.content
        if content is None:
            raise Exception("LLM response content is empty.")
        return content

    def _get_json_payload_from_llm_content(self, llm_content: str) -> str:
        """Extracts the JSON array string from the LLM's raw text output."""
        json_match = re.search(r"\[.*\]", llm_content, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return llm_content

    def _parse_and_validate_scenes(self, json_payload: str) -> List[Scene]:
        """
        Parses a JSON string and validates it into a list of Scene objects.
        """
        try:
            scenes_data = json.loads(json_payload)
            
            if not isinstance(scenes_data, list):
                raise ValueError(f"Expected a JSON list/array, but got {type(scenes_data).__name__}")

            validated_scenes: List[Scene] = []
            for i, scene_item in enumerate(scenes_data):
                if not isinstance(scene_item, dict):
                    raise ValueError(f"Item at index {i} is not a dictionary")
                validated_scenes.append(Scene(**scene_item))
            
            return validated_scenes
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"Error parsing scenes: {e}")
            return []

# Factory function for easy instantiation
def create_text_analyzer() -> TextAnalyzer:
    """
    Create a text analyzer instance
        
    Returns:
        TextAnalyzer instance
    """
    return TextAnalyzer()