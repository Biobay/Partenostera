#!/usr/bin/env python3
"""
AI Horde Image Generator - Script Completo
Genera immagini usando l'API di Stable Horde
"""

import requests
import time
import json
import os
from pathlib import Path
from datetime import datetime

class AIHordeGenerator:
    def __init__(self, api_key="xbCXATE-9l8CPYqfojI9iQ"):
        self.api_key = api_key
        self.base_url = "https://stablehorde.net/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "apikey": api_key,
            "Content-Type": "application/json"
        })
    
    def get_user_info(self):
        """Ottieni informazioni sull'utente"""
        try:
            response = self.session.get(f"{self.base_url}/find_user", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Errore nel recupero info utente: {e}")
            return None
    
    def get_available_models(self):
        """Ottieni lista modelli disponibili"""
        try:
            response = requests.get(f"{self.base_url}/status/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                # Filtra solo modelli attivi
                return [m for m in models if m.get('count', 0) > 0]
            return []
        except Exception as e:
            print(f"Errore nel recupero modelli: {e}")
            return []
    
    def generate_image(self, prompt, width=512, height=512, steps=25, model=None):
        """Genera un'immagine"""
        
        # Se non specificato, usa un modello popolare
        if model is None:
            models = self.get_available_models()
            if models:
                # Scegli un modello con molti worker
                popular_models = sorted(models, key=lambda x: x.get('count', 0), reverse=True)
                model = popular_models[0]['name']
            else:
                model = "stable_diffusion"  # fallback
        
        payload = {
            "prompt": prompt,
            "params": {
                "width": width,
                "height": height,
                "steps": steps,
                "sampler_name": "k_euler_a",
                "cfg_scale": 7.5,
                "seed_variation": 1,
                "post_processing": ["RealESRGAN_x4plus"]
            },
            "models": [model],
            "r2": True,
            "shared": False,
            "replacement_filter": True
        }
        
        print(f"🎨 Generando immagine...")
        print(f"📝 Prompt: {prompt}")
        print(f"📐 Dimensioni: {width}x{height}")
        print(f"🤖 Modello: {model}")
        
        try:
            # Invia richiesta
            response = self.session.post(f"{self.base_url}/generate/async", json=payload, timeout=15)
            
            if response.status_code != 202:
                print(f"❌ Errore nell'invio: {response.status_code}")
                print(f"Risposta: {response.text}")
                return None
            
            result = response.json()
            job_id = result.get("id")
            
            if not job_id:
                print("❌ Nessun job ID ricevuto")
                return None
            
            print(f"✅ Richiesta inviata! Job ID: {job_id}")
            
            # Monitora e scarica
            return self.wait_and_download(job_id)
            
        except Exception as e:
            print(f"❌ Errore nella generazione: {e}")
            return None
    
    def wait_and_download(self, job_id):
        """Attende e scarica il risultato"""
        max_wait = 300  # 5 minuti
        start_time = time.time()
        
        print("⏳ Attendendo completamento...")
        
        while time.time() - start_time < max_wait:
            try:
                # Controlla stato
                response = self.session.get(f"{self.base_url}/generate/check/{job_id}", timeout=10)
                
                if response.status_code != 200:
                    print(f"❌ Errore controllo stato: {response.status_code}")
                    return None
                
                status = response.json()
                
                # Mostra progresso
                queue_pos = status.get("queue_position", 0)
                wait_time = status.get("wait_time", 0)
                
                if queue_pos > 0:
                    print(f"📊 Posizione {queue_pos}, attesa ~{wait_time}s")
                
                # Controlla se completato
                if status.get("done", False):
                    print("✅ Generazione completata!")
                    return self.download_result(job_id)
                
                # Controlla se fallito
                if status.get("faulted", False):
                    print("❌ Generazione fallita")
                    return None
                
                time.sleep(5)  # Attende 5 secondi
                
            except Exception as e:
                print(f"❌ Errore nel monitoraggio: {e}")
                return None
        
        print("⏰ Timeout raggiunto")
        return None
    
    def download_result(self, job_id):
        """Scarica il risultato finale"""
        try:
            response = self.session.get(f"{self.base_url}/generate/status/{job_id}", timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Errore download: {response.status_code}")
                return None
            
            result = response.json()
            generations = result.get("generations", [])
            
            if not generations:
                print("❌ Nessuna immagine generata")
                return None
            
            # Crea cartella output
            output_dir = Path("ai_horde_images")
            output_dir.mkdir(exist_ok=True)
            
            downloaded_files = []
            
            for i, gen in enumerate(generations):
                img_url = gen.get("img")
                if not img_url:
                    continue
                
                # Scarica immagine
                img_response = requests.get(img_url, timeout=30)
                if img_response.status_code == 200:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"ai_horde_{timestamp}_{i}.png"
                    filepath = output_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f"💾 Salvata: {filepath}")
                    
                    # Info addizionali
                    worker = gen.get("worker_name", "Unknown")
                    model = gen.get("model", "Unknown")
                    print(f"   🤖 Worker: {worker}")
                    print(f"   🎨 Modello: {model}")
                    
                    downloaded_files.append(str(filepath))
            
            return downloaded_files
            
        except Exception as e:
            print(f"❌ Errore nel download: {e}")
            return None

def main():
    print("🎨 AI Horde Image Generator")
    print("=" * 50)
    
    # Inizializza generatore
    generator = AIHordeGenerator()
    
    # Mostra info utente
    user_info = generator.get_user_info()
    if user_info:
        username = user_info.get('username', 'Unknown')
        kudos = user_info.get('kudos', 0)
        print(f"👤 Utente: {username}")
        print(f"💰 Kudos: {kudos}")
        
        if kudos < 10:
            print("⚠️ Pochi kudos disponibili - potresti avere tempi di attesa lunghi")
    
    # Mostra modelli disponibili
    models = generator.get_available_models()
    if models:
        print(f"\n🎭 Modelli disponibili: {len(models)}")
        top_models = sorted(models, key=lambda x: x.get('count', 0), reverse=True)[:5]
        for i, model in enumerate(top_models, 1):
            name = model['name']
            workers = model.get('count', 0)
            queue = model.get('queued', 0)
            print(f"  {i}. {name} ({workers} workers, {queue} in coda)")
    
    # Menu principale
    while True:
        print("\n" + "=" * 50)
        print("📋 Opzioni:")
        print("1. Genera immagine con prompt personalizzato")
        print("2. Test rapido con prompt predefinito")
        print("3. Batch di immagini di test")
        print("4. Esci")
        
        try:
            choice = input("\n🎯 Scegli (1-4): ").strip()
            
            if choice == "1":
                prompt = input("📝 Inserisci il prompt: ").strip()
                if prompt:
                    width = int(input("📐 Larghezza (default 512): ") or "512")
                    height = int(input("📐 Altezza (default 512): ") or "512")
                    steps = int(input("🔧 Steps (default 25): ") or "25")
                    
                    result = generator.generate_image(prompt, width, height, steps)
                    if result:
                        print(f"🎉 Successo! File salvati: {len(result)}")
                    else:
                        print("❌ Generazione fallita")
                
            elif choice == "2":
                prompt = "a beautiful sunset over mountains, photorealistic, high quality"
                result = generator.generate_image(prompt)
                if result:
                    print(f"🎉 Test completato! File: {result[0]}")
                
            elif choice == "3":
                prompts = [
                    "a red apple on white background, simple, clean",
                    "a cute cat sleeping, cartoon style",
                    "abstract art with blue and orange colors"
                ]
                
                print(f"🔄 Generando {len(prompts)} immagini di test...")
                for i, prompt in enumerate(prompts, 1):
                    print(f"\n--- Test {i}/{len(prompts)} ---")
                    result = generator.generate_image(prompt, 512, 512, 20)
                    if result:
                        print(f"✅ Test {i} completato")
                    else:
                        print(f"❌ Test {i} fallito")
                
            elif choice == "4":
                print("👋 Arrivederci!")
                break
                
            else:
                print("❌ Scelta non valida!")
                
        except KeyboardInterrupt:
            print("\n🛑 Interrotto dall'utente")
            break
        except Exception as e:
            print(f"❌ Errore: {e}")

if __name__ == "__main__":
    main()
