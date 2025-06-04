#!/usr/bin/env python3
"""
Parser per le scene del libro e generatore di prompt video
"""

import os
import csv
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Scene:
    """Classe per rappresentare una scena del libro"""
    elementi_narrativi: str
    personaggi: str
    ambientazione: str
    mood_vibe: str
    azione_in_corso: str

class SceneToVideoPromptGenerator:
    """Converte le scene del libro in prompt per la generazione video"""
    
    def __init__(self):
        self.scenes = []
        
    def load_scenes_from_string(self, scenes_string: str) -> List[Scene]:
        """
        Carica le scene da una stringa Python (per test)
        Nella versione finale, questo sarà sostituito dal codice del tuo compagno
        """
        try:
            # Valuta la stringa come codice Python per ottenere la lista di Scene
            scenes_list = eval(scenes_string)
            self.scenes = scenes_list
            print(f"✅ Caricate {len(self.scenes)} scene")
            return self.scenes
        except Exception as e:
            print(f"❌ Errore nel parsing delle scene: {e}")
            return []
    
    def load_scenes_from_file(self, filepath: str) -> List[Scene]:
        """
        Carica le scene da un file (formato da definire con il tuo compagno)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.load_scenes_from_string(content)
        except Exception as e:
            print(f"❌ Errore nel leggere il file {filepath}: {e}")
            return []
    
    def scene_to_video_prompt(self, scene: Scene, scene_number: int) -> Dict[str, str]:
        """
        Converte una singola scena in prompt per video cinematografico
        """
        # Estrai elementi chiave dalla scena
        ambientazione = scene.ambientazione.strip()
        personaggi = scene.personaggi.strip()
        azione = scene.azione_in_corso.strip()
        mood = scene.mood_vibe.strip()
        elementi = scene.elementi_narrativi.strip()
        
        # Crea una descrizione della scena combinata
        scene_description = f"Scena {scene_number}: {azione}"
        
        # Genera un prompt video cinematografico
        video_prompt = self._generate_cinematic_prompt(
            ambientazione, personaggi, azione, mood, elementi
        )
        
        return {
            'scene_number': scene_number, # type: ignore
            'scene_description': scene_description,
            'video_prompt': video_prompt,
            'full_scene': {
                'elementi_narrativi': elementi,
                'personaggi': personaggi,
                'ambientazione': ambientazione,
                'mood_vibe': mood,
                'azione_in_corso': azione
            }
        }
    
    def _generate_cinematic_prompt(self, ambientazione: str, personaggi: str, 
                                 azione: str, mood: str, elementi: str) -> str:
        """
        Genera un prompt cinematografico basato sui dettagli della scena
        """
        # Estrai parole chiave per il mood
        mood_keywords = self._extract_mood_keywords(mood)
        
        # Estrai setting principale
        setting_main = self._extract_main_setting(ambientazione)
        
        # Estrai azione principale
        action_main = self._extract_main_action(azione)
        
        # Costruisci il prompt cinematografico
        prompt = f"{action_main}, {setting_main}, {mood_keywords}, cinematic lighting, professional camera movement, high quality, detailed, atmospheric"
        
        return prompt
    
    def _extract_mood_keywords(self, mood: str) -> str:
        """Estrae e converte le parole chiave del mood"""
        mood_mapping = {
            'calmo': 'calm and peaceful',
            'laborioso': 'industrious atmosphere',
            'confortante': 'comforting warmth',
            'tradizionale': 'traditional setting',
            'misterioso': 'mysterious ambiance',
            'curioso': 'curious discovery',
            'soprannaturale': 'supernatural elements',
            'miracoloso': 'miraculous transformation',
            'sorprendente': 'surprising revelation',
            'speranzoso': 'hopeful mood',
            'grave': 'serious tone',
            'preoccupato': 'worried atmosphere',
            'solenne': 'solemn moment',
            'coraggioso': 'brave determination'
        }
        
        # Converti mood italiano in inglese cinematografico
        mood_lower = mood.lower()
        english_moods = []
        
        for italian, english in mood_mapping.items():
            if italian in mood_lower:
                english_moods.append(english)
        
        return ', '.join(english_moods) if english_moods else 'dramatic atmosphere'
    
    def _extract_main_setting(self, ambientazione: str) -> str:
        """Estrae il setting principale"""
        # Semplifica l'ambientazione per il prompt video
        if 'panetteria' in ambientazione.lower():
            return 'cozy bakery interior'
        elif 'villaggio' in ambientazione.lower():
            return 'charming village setting'
        elif 'camera' in ambientazione.lower():
            return 'intimate bedroom scene'
        else:
            return 'atmospheric interior scene'
    
    def _extract_main_action(self, azione: str) -> str:
        """Estrae l'azione principale"""
        # Semplifica l'azione per il prompt video
        azione_lower = azione.lower()
        
        if 'impasta' in azione_lower or 'pane' in azione_lower:
            return 'person kneading dough and baking bread'
        elif 'luccica' in azione_lower or 'brilla' in azione_lower:
            return 'magical flour glowing with supernatural light'
        elif 'offre' in azione_lower or 'morde' in azione_lower:
            return 'elderly person eating magical bread and transforming'
        elif 'rende conto' in azione_lower:
            return 'person realizing the cost of magical power'
        elif 'decisione' in azione_lower or 'pensier' in azione_lower:
            return 'person in deep contemplation making difficult decision'
        else:
            return 'character performing meaningful action'
    
    def generate_csv_for_images(self, image_names: List[str], output_file: str = "scene_prompts.csv") -> bool:
        """
        Genera il file CSV che associa immagini a scene e prompt video
        """
        if not self.scenes:
            print("❌ Nessuna scena caricata")
            return False
        
        if len(image_names) != len(self.scenes):
            print(f"⚠️ Numero di immagini ({len(image_names)}) diverso dal numero di scene ({len(self.scenes)})")
            print("🔄 Procedendo con il minimo tra i due...")
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['image_name', 'scene_description', 'video_prompt'])
                
                min_count = min(len(image_names), len(self.scenes))
                
                for i in range(min_count):
                    scene_data = self.scene_to_video_prompt(self.scenes[i], i + 1)
                    writer.writerow([
                        image_names[i],
                        scene_data['scene_description'],
                        scene_data['video_prompt']
                    ])
            
            print(f"✅ File CSV generato: {output_file}")
            print(f"📋 Processate {min_count} scene")
            return True
            
        except Exception as e:
            print(f"❌ Errore nella generazione del CSV: {e}")
            return False
    
    def save_detailed_scenes(self, output_file: str = "detailed_scenes.json") -> bool:
        """Salva le scene complete in formato JSON per debug"""
        try:
            scenes_data = []
            for i, scene in enumerate(self.scenes):
                scene_data = self.scene_to_video_prompt(scene, i + 1)
                scenes_data.append(scene_data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(scenes_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Scene dettagliate salvate in: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Errore nel salvare le scene: {e}")
            return False

def main():
    """Funzione di test"""
    # Esempio di scene (dal tuo messaggio)
    example_scenes = """[Scene(elementi_narrativi='Pane fresco, impasto, forno, arredo semplice di una panetteria del villaggio.', personaggi="Elena: una giovane panettiera, con mani forse un po' infuocate, viso concentrato ma tranquillo, espressione diligente.", ambientazione="Un piccolo villaggio tra colline ondulate e una foresta sussurrante. L'interno di una panetteria accogliente, prima dell'alba, con una luce soffusa e un'atmosfera calda, permeata dall'aroma del pane.", mood_vibe='Calmo, laborioso, confortante, tradizionale.', azione_in_corso="Elena si alza prima dell'alba e impasta il pane, riempiendo il suo negozio con il caldo aroma del pane fresco."),
 Scene(elementi_narrativi='Farina che luccica con una luce ultraterrena, ciotole, strumenti da panettiere, candele tremolanti.', personaggi="Elena: viso sorpreso e curioso, occhi aperti, un po' scettica inizialmente, poi profondamente incuriosita e meravigliata.", ambientazione="L'interno della panetteria di Elena, una mattina particolarmente nebbiosa. La luce delle candele è l'unica fonte, rendendo l'ambiente misterioso e suggestivo.", mood_vibe='Misterioso, curioso, soprannaturale, di scoperta.', azione_in_corso='Elena sta preparando il suo solito pane quando nota la farina luccicare e brillare sempre più intensamente mentre la lavora.'),
 Scene(elementi_narrativi='Un filone di pane appena sfornato, il bancone della panetteria, piccole monete (facoltative).', personaggi="Elena: titubante mentre offre il pane, poi sbalordita; il vecchio Signor Henrick: inizialmente con un viso 'increspato' e occhi stanchi, che si trasformano immediatamente in un viso più liscio e occhi che brillano di rinnovato vigore e giovinezza.", ambientazione="La panetteria di Elena, durante l'orario di apertura del mattino, con la luce che filtra dall'esterno. L'ambiente è caldo e invitante.", mood_vibe='Miracoloso, sorprendente, speranzoso, di stupore.', azione_in_corso='Elena offre un pane fatto con la farina misteriosa al Signor Henrick, che lo morde e sperimenta una trasformazione visibile e immediata.'),
 Scene(elementi_narrativi='Forno, pasta, una sensazione di stanchezza o un leggero pallore sul viso di Elena.', personaggi="Elena: visibilmente affaticata o con un'ombra di preoccupazione sul viso, gli occhi che riflettono una nuova consapevolezza, sola o in un momento di introspezione.", ambientazione="La panetteria di Elena, forse nel tardo pomeriggio o la sera, dopo una giornata intensa. L'ambiente è più buio o ha una luce più fioca, riflettendo il mood. Potrebbe esserci un disordine creativo di farina e utensili.", mood_vibe='Grave, di realizzazione, proccupato, di tristezza.', azione_in_corso="Elena si rende conto, forse mentre impasta o dopo aver infornato l'ennesimo pane, che ogni pagnotta magica le sottrae un po' della sua forza vitale."),
 Scene(elementi_narrativi="Nessun elemento narrativo specifico, l'attenzione è tutta sulla persona e la sua scelta.", personaggi='Elena: una figura decisa ma pensierosa, il suo viso mostra il peso della scelta ma anche una profonda compassione e risolutezza. Potrebbe avere le mani giunte o essere in una posa di profonda riflessione.', ambientazione="Un luogo intimo e quieto, come l'angolo tranquillo della sua panetteria o la sua semplice camera da letto, nella penombra. L'ambiente dovrebbe trasmettere solitudine e gravità.", mood_vibe='Solenne, coraggioso, pesante, di profonda compassione, di risoluzione.', azione_in_corso='Elena è immobile, persa nei suoi pensieri, mentre prende una difficile e altruistica decisione: continuare a usare il suo dono per aiutare gli altri, anche se ciò le costerà la vita stessa.')]"""
    
    generator = SceneToVideoPromptGenerator()
    
    # Carica le scene di esempio
    generator.load_scenes_from_string(example_scenes)
    
    # Genera nomi immagini di esempio
    image_names = [
        'scene1_elena_baking.jpg',
        'scene2_magical_flour.jpg', 
        'scene3_transformation.jpg',
        'scene4_realization.jpg',
        'scene5_decision.jpg'
    ]
    
    # Genera il CSV
    generator.generate_csv_for_images(image_names)
    
    # Salva scene dettagliate per debug
    generator.save_detailed_scenes()

if __name__ == "__main__":
    main()
