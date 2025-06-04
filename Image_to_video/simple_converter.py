#!/usr/bin/env python3
"""
Script completo per convertire scene del libro in video
Integra: Scene Parser + CSV Generator + Video Converter
"""

import os
import replicate
import requests
import glob
import csv
from pathlib import Path
from dotenv import load_dotenv
from scene_parser import SceneToVideoPromptGenerator, Scene
from book_scenes import get_book_scenes  # Integrazione con il sistema del tuo compagno

# Carica le variabili d'ambiente
load_dotenv()

def convert_image_to_video(image_path, prompt="a video", output_dir="videos"):
    """Converte un'immagine in video e lo salva nella cartella output"""
    
    # Configura Replicate
    api_token = os.getenv("REPLICATE_API_TOKEN")
    
    if not api_token:
        print("❌ REPLICATE_API_TOKEN non trovato nel file .env")
        return None
    
    # Imposta il token per la sessione
    os.environ["REPLICATE_API_TOKEN"] = api_token
    
    try:
        print(f"🎬 Conversione immagine: {image_path}")
        print(f"📝 Prompt: {prompt}")
        
        # Prepara l'input
        input_data = {
            "image": open(image_path, "rb"),
            "prompt": prompt
        }
        
        print("⏳ Invio richiesta a Replicate...")
        
        # Chiama l'API
        output = replicate.run(
            "wavespeedai/wan-2.1-i2v-480p",
            input=input_data
        )
        
        print("📥 Ricevuto output da Replicate, salvando video...")
        
        # Salva il video direttamente
        return save_video_output(output, image_path, output_dir)
                
    except Exception as e:
        print(f"❌ Errore: {e}")
        return None

def save_video_output(output, original_image_path, output_dir):
    """Salva l'output video da Replicate"""
    try:
        # Crea la cartella di output se non esiste
        Path(output_dir).mkdir(exist_ok=True)
        
        # Genera nome file per il video
        image_name = Path(original_image_path).stem
        video_filename = f"{image_name}_converted.mp4"
        video_path = Path(output_dir) / video_filename
        
        print(f"💾 Salvando video in: {video_path}")
        
        # Salva il video
        with open(video_path, 'wb') as f:
            f.write(output.read())
        
        print(f"✅ Video salvato in: {video_path}")
        return str(video_path)
        
    except Exception as e:
        print(f"❌ Errore nel salvataggio: {e}")
        return None

def download_video(video_url, original_image_path, output_dir):
    """Scarica il video dall'URL e lo salva localmente"""
    try:
        # Crea la cartella di output se non esiste
        Path(output_dir).mkdir(exist_ok=True)
        
        # Genera nome file per il video
        image_name = Path(original_image_path).stem
        video_filename = f"{image_name}_converted.mp4"
        video_path = Path(output_dir) / video_filename
        
        print(f"📥 Scaricamento video da: {video_url}")
        
        # Scarica il video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Video salvato in: {video_path}")
        return str(video_path)
        
    except Exception as e:
        print(f"❌ Errore nel download: {e}")
        return video_url  # Ritorna almeno l'URL

def find_images(images_dir="Images"):
    """Trova tutte le immagini nella cartella specificata"""
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.gif']
    image_files = []
    
    for ext in image_extensions:
        # Cerca solo una volta per ogni estensione, case-insensitive
        pattern = os.path.join(images_dir, ext)
        found_files = glob.glob(pattern, recursive=False)
        image_files.extend(found_files)
        
        # Cerca anche le estensioni maiuscole solo se non già trovate
        pattern_upper = os.path.join(images_dir, ext.upper())
        found_upper = glob.glob(pattern_upper, recursive=False)
        for file in found_upper:
            if file not in image_files:  # Evita duplicati
                image_files.append(file)
    
    # Rimuovi eventuali duplicati
    return list(set(image_files))

def process_all_images(images_dir="Images", videos_dir="Videos", scene_prompts=None):
    """Processa tutte le immagini nella cartella specificata"""
    
    # Trova tutte le immagini
    image_files = find_images(images_dir)
    
    if not image_files:
        print(f"❌ Nessuna immagine trovata nella cartella '{images_dir}'")
        print(f"💡 Aggiungi delle immagini (.jpg, .png, etc.) nella cartella '{images_dir}' e riprova")
        return []
    
    print(f"📸 Trovate {len(image_files)} immagini da convertire")
    
    results = []
    for i, image_path in enumerate(image_files, 1):
        print(f"\n🎯 Processando immagine {i}/{len(image_files)}: {os.path.basename(image_path)}")
        
        # Ottieni il prompt specifico per questa immagine
        prompt_data = get_prompt_for_image(image_path, scene_prompts or {})
        scene_description = prompt_data['scene_description']
        video_prompt = prompt_data['video_prompt']
        
        print(f"📖 Scena: {scene_description}")
        print(f"🎬 Prompt Video: {video_prompt}")
        
        video_path = convert_image_to_video(image_path, video_prompt, videos_dir)
        results.append({
            'image': image_path,
            'video': video_path,
            'scene_description': scene_description,
            'video_prompt': video_prompt,
            'success': video_path is not None
        })
        
        if video_path:
            print(f"✅ Completato: {os.path.basename(video_path)}")
        else:
            print(f"❌ Fallito: {os.path.basename(image_path)}")
    
    return results

def load_scene_prompts(csv_file="scene_prompts.csv"):
    """Carica i prompt delle scene dal file CSV"""
    prompts = {}
    
    if not os.path.exists(csv_file):
        print(f"⚠️ File {csv_file} non trovato. Creando file di esempio...")
        create_example_csv(csv_file)
        return prompts
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                image_name = row['image_name'].strip()
                scene_description = row['scene_description'].strip()
                video_prompt = row['video_prompt'].strip()
                
                prompts[image_name] = {
                    'scene_description': scene_description,
                    'video_prompt': video_prompt
                }
        
        print(f"📋 Caricati {len(prompts)} prompt dal file {csv_file}")
        return prompts
        
    except Exception as e:
        print(f"❌ Errore nel leggere {csv_file}: {e}")
        return prompts

def create_example_csv(csv_file="scene_prompts.csv"):
    """Crea un file CSV di esempio"""
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['image_name', 'scene_description', 'video_prompt'])
            writer.writerow([
                'esempio_immagine.jpg',
                'Descrizione della scena dal libro',
                'Prompt specifico per creare il video cinematografico'
            ])
        print(f"✅ Creato file di esempio: {csv_file}")
        print("💡 Modifica il file CSV con le tue scene e prompt specifici")
    except Exception as e:
        print(f"❌ Errore nel creare {csv_file}: {e}")

def get_prompt_for_image(image_path, scene_prompts):
    """Ottiene il prompt specifico per un'immagine"""
    image_name = os.path.basename(image_path)
    
    if image_name in scene_prompts:
        return scene_prompts[image_name]
    
    # Fallback: prompt generico se non trovato
    return {
        'scene_description': 'Scena generica dal libro',
        'video_prompt': 'a cinematic video with smooth motion and professional lighting'
    }

def generate_csv_from_scenes(scenes_data, images_dir="Images", csv_output="scene_prompts.csv"):
    """
    Genera automaticamente il CSV dalle scene del libro
    """
    # Inizializza il generatore di scene
    generator = SceneToVideoPromptGenerator()
    
    # Carica le scene dal formato del tuo compagno
    if isinstance(scenes_data, str):
        # Se è una stringa, carica da stringa
        generator.load_scenes_from_string(scenes_data)
    elif isinstance(scenes_data, list):
        # Se è già una lista di Scene
        generator.scenes = scenes_data
    else:
        print("❌ Formato scene non riconosciuto")
        return False
    
    # Trova le immagini nella cartella
    image_files = find_images(images_dir)
    image_names = [os.path.basename(img) for img in image_files]
    
    if not image_names:
        print(f"❌ Nessuna immagine trovata in {images_dir}")
        return False
    
    # Genera il CSV
    success = generator.generate_csv_for_images(image_names, csv_output)
    if success:
        # Salva anche le scene dettagliate per debug
        generator.save_detailed_scenes("detailed_scenes.json")
    
    return success

# Carica le variabili d'ambiente
load_dotenv()

if __name__ == "__main__":
    print("🚀 Convertitore Scene Libro -> Video")
    print("=" * 40)
    
    # Opzione 1: Usa le scene dal sistema del tuo compagno
    print("📚 Caricamento scene dal libro...")
    book_scenes = get_book_scenes()
    
    if book_scenes:
        print(f"✅ Caricate {len(book_scenes)} scene dal libro")
        
        # Genera automaticamente il CSV dalle scene
        csv_generated = generate_csv_from_scenes(
            scenes_data=book_scenes,
            images_dir="Images",
            csv_output="scene_prompts.csv"
        )
    else:
        # Fallback: usa scene di esempio
        print("⚠️ Nessuna scena trovata, usando scene di esempio...")
        example_scenes_str = """[Scene(elementi_narrativi='Pane fresco, impasto, forno, arredo semplice di una panetteria del villaggio.', personaggi="Elena: una giovane panettiera, con mani forse un po' infuocate, viso concentrato ma tranquillo, espressione diligente.", ambientazione="Un piccolo villaggio tra colline ondulate e una foresta sussurrante. L'interno di una panetteria accogliente, prima dell'alba, con una luce soffusa e un'atmosfera calda, permeata dall'aroma del pane.", mood_vibe='Calmo, laborioso, confortante, tradizionale.', azione_in_corso="Elena si alza prima dell'alba e impasta il pane, riempiendo il suo negozio con il caldo aroma del pane fresco.")]"""
        
        csv_generated = generate_csv_from_scenes(
            scenes_data=example_scenes_str,
            images_dir="Images", 
            csv_output="scene_prompts.csv"
        )
    
    if not csv_generated:
        print("❌ Errore nella generazione del CSV dalle scene")
        print("💡 Controlla che ci siano immagini nella cartella Images/")
        exit(1)
    
    # Carica i prompt delle scene dal file CSV generato
    scene_prompts = load_scene_prompts("scene_prompts.csv")
    
    # Processa tutte le immagini nella cartella 'Images'
    results = process_all_images(
        images_dir="Images",
        videos_dir="Videos", 
        scene_prompts=scene_prompts
    )
    
    # Riepilogo risultati
    print("\n" + "=" * 40)
    print("📊 RIEPILOGO CONVERSIONI:")
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    if results:
        print(f"✅ Successi: {successful}/{total}")
        print(f"❌ Fallimenti: {total - successful}/{total}")
        
        print("\n📁 Video creati:")
        for result in results:
            if result['success']:
                video_name = os.path.basename(result['video'])
                print(f"  • {video_name}")
                print(f"    📖 Scena: {result['scene_description']}")
                print(f"    🎬 Prompt: {result['video_prompt'][:80]}...")
                print()
    else:
        print("💡 Per iniziare:")
        print("   1. Aggiungi immagini nella cartella 'Images/'")
        print("   2. Assicurati di avere REPLICATE_API_TOKEN nel file .env")
        print("   3. Esegui di nuovo lo script")
