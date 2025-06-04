#!/usr/bin/env python3
"""
AI Horde Text-to-Image Generator
Genera immagini da testo usando l'API ufficiale di AI Horde
Basato sulla documentazione API v2
"""

import requests
import time
import json
import base64
import os
from pathlib import Path
from datetime import datetime

class AIHordeTextToImage:
    def __init__(self, api_key="xbCXATE-9l8CPYqfojI9iQ"):
        self.api_key = api_key
        self.base_url = "https://stablehorde.net/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "apikey": api_key,
            "Content-Type": "application/json",
            "Client-Agent": "AIHorde-Python-Script:1.0"
        })
    
    def get_available_models(self):
        """Ottieni modelli disponibili per la generazione di immagini"""
        try:
            response = requests.get(f"{self.base_url}/status/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                # Filtra solo modelli attivi per generazione immagini
                image_models = []
                for model in models:
                    if model.get('count', 0) > 0 and model.get('type') != 'text':
                        image_models.append(model)
                return image_models
            return []
        except Exception as e:
            print(f"Errore nel recupero modelli: {e}")
            return []
    
    def get_user_info(self):
        """Ottieni informazioni sull'utente e kudos disponibili"""
        try:
            response = self.session.get(f"{self.base_url}/find_user", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Errore nel recupero info utente: {e}")
            return None
    
    def estimate_kudos_cost(self, width=512, height=512, steps=30, models=None):
        """Stima il costo in kudos per la generazione"""
        # Formula base: width * height * steps / 1000000 * 5.2
        base_cost = (width * height * steps) / 1000000 * 5.2
        
        # Aggiusta per modelli specifici (alcuni costano di più)
        if models and any('xl' in model.lower() for model in models):
            base_cost *= 1.5  # SDXL costa di più
        
        return round(base_cost, 2)
    
    def generate_image(self, prompt, **kwargs):
        """
        Genera un'immagine da testo usando AI Horde
        
        Args:
            prompt (str): Il prompt per generare l'immagine
            **kwargs: Parametri opzionali:
                - width (int): Larghezza immagine (default: 512)
                - height (int): Altezza immagine (default: 512) 
                - steps (int): Passi di generazione (default: 30)
                - cfg_scale (float): Scala CFG (default: 7.5)
                - sampler_name (str): Sampler (default: "k_euler_a")
                - models (list): Lista modelli (default: auto)
                - nsfw (bool): Contenuto NSFW (default: False)
                - seed (str): Seed per riproducibilità (default: None)
                - post_processing (list): Post-processing (default: ["RealESRGAN_x4plus"])
        """
        
        # Parametri di default
        params = {
            "width": kwargs.get("width", 512),
            "height": kwargs.get("height", 512),
            "steps": kwargs.get("steps", 30),
            "cfg_scale": kwargs.get("cfg_scale", 7.5),
            "sampler_name": kwargs.get("sampler_name", "k_euler_a"),
            "post_processing": kwargs.get("post_processing", ["RealESRGAN_x4plus"])
        }
        
        # Aggiungi seed se specificato
        if kwargs.get("seed"):
            params["seed"] = str(kwargs["seed"])
        
        # Scegli modelli
        models = kwargs.get("models")
        if not models:
            # Auto-seleziona i migliori modelli disponibili
            available_models = self.get_available_models()
            if available_models:
                # Ordina per popolarità (più worker = più veloce)
                popular_models = sorted(available_models, 
                                      key=lambda x: x.get('count', 0), 
                                      reverse=True)
                # Prendi i top 3 modelli per aumentare le possibilità
                models = [m['name'] for m in popular_models[:3]]
            else:
                models = ["stable_diffusion"]  # fallback
        
        # Costruisci payload secondo la documentazione API
        payload = {
            "prompt": prompt,
            "params": params,
            "nsfw": kwargs.get("nsfw", False),
            "trusted_workers": kwargs.get("trusted_workers", True),
            "slow_workers": kwargs.get("slow_workers", True),
            "censor_nsfw": kwargs.get("censor_nsfw", False),
            "models": models,
            "r2": True,  # Usa Cloudflare R2 per download più veloci
            "shared": False,  # Non condividere pubblicamente
            "replacement_filter": True,  # Filtra contenuti inappropriati
            "dry_run": False
        }
        
        # Stima costo
        estimated_cost = self.estimate_kudos_cost(
            params["width"], params["height"], params["steps"], models
        )
        
        print(f"🎨 Generazione immagine da testo")
        print(f"📝 Prompt: {prompt}")
        print(f"📐 Dimensioni: {params['width']}x{params['height']}")
        print(f"🔧 Steps: {params['steps']}")
        print(f"🤖 Modelli: {', '.join(models)}")
        print(f"💰 Costo stimato: {estimated_cost} kudos")
        
        try:
            # Invia richiesta di generazione asincrona
            print("📤 Invio richiesta...")
            response = self.session.post(
                f"{self.base_url}/generate/async", 
                json=payload, 
                timeout=20
            )
            
            if response.status_code != 202:
                print(f"❌ Errore nell'invio: {response.status_code}")
                print(f"Risposta: {response.text}")
                return None
            
            result = response.json()
            job_id = result.get("id")
            
            if not job_id:
                print("❌ Nessun job ID ricevuto")
                return None
            
            print(f"✅ Richiesta accettata! Job ID: {job_id}")
            
            # Monitora e ottieni risultati
            return self.monitor_and_download(job_id)
            
        except Exception as e:
            print(f"❌ Errore nella generazione: {e}")
            return None
    
    def monitor_and_download(self, job_id):
        """Monitora la generazione e scarica i risultati"""
        max_wait = 600  # 10 minuti max
        start_time = time.time()
        
        print("⏳ Monitoraggio generazione...")
        
        while time.time() - start_time < max_wait:
            try:
                # Controlla stato senza immagini (più veloce)
                response = self.session.get(
                    f"{self.base_url}/generate/check/{job_id}", 
                    timeout=10
                )
                
                if response.status_code != 200:
                    print(f"❌ Errore controllo stato: {response.status_code}")
                    return None
                
                status = response.json()
                
                # Mostra progresso
                done = status.get("done", False)
                faulted = status.get("faulted", False)
                processing = status.get("processing", 0)
                restarted = status.get("restarted", 0)
                waiting = status.get("waiting", 0)
                queue_position = status.get("queue_position", 0)
                wait_time = status.get("wait_time", 0)
                is_possible = status.get("is_possible", True)
                
                if not is_possible:
                    print("❌ Generazione non possibile (parametri non validi o modelli non disponibili)")
                    return None
                
                if faulted:
                    print("❌ Generazione fallita")
                    return None
                
                if done:
                    print("✅ Generazione completata!")
                    return self.download_results(job_id)
                
                # Mostra stato corrente
                if queue_position > 0:
                    print(f"📊 In coda: posizione {queue_position}, attesa ~{wait_time}s")
                elif processing > 0:
                    print(f"🔄 In elaborazione: {processing} worker(s)")
                elif waiting > 0:
                    print(f"⏳ In attesa: {waiting} richiesta(e)")
                
                if restarted > 0:
                    print(f"🔄 Riavviata {restarted} volta(e)")
                
                # Attendi prima del prossimo controllo
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Errore nel monitoraggio: {e}")
                time.sleep(5)
                continue
        
        print("⏰ Timeout raggiunto")
        return None
    
    def download_results(self, job_id):
        """Scarica i risultati finali della generazione"""
        try:
            # Ottieni risultati completi con immagini
            response = self.session.get(
                f"{self.base_url}/generate/status/{job_id}", 
                timeout=30
            )
            
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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, generation in enumerate(generations):
                try:
                    # Ottieni immagine (può essere URL o base64)
                    img_data = generation.get("img")
                    if not img_data:
                        continue
                    
                    filename = f"ai_horde_{job_id}_{i}_{timestamp}.webp"
                    filepath = output_dir / filename
                    
                    # Se è un URL, scarica
                    if img_data.startswith("http"):
                        img_response = requests.get(img_data, timeout=30)
                        if img_response.status_code == 200:
                            with open(filepath, 'wb') as f:
                                f.write(img_response.content)
                        else:
                            print(f"⚠️ Errore download immagine {i}: {img_response.status_code}")
                            continue
                    else:
                        # Se è base64, decodifica
                        try:
                            img_bytes = base64.b64decode(img_data)
                            with open(filepath, 'wb') as f:
                                f.write(img_bytes)
                        except Exception as e:
                            print(f"⚠️ Errore decodifica base64 immagine {i}: {e}")
                            continue
                    
                    print(f"💾 Salvata: {filepath}")
                    
                    # Mostra metadata
                    worker_name = generation.get("worker_name", "Unknown")
                    worker_id = generation.get("worker_id", "Unknown")
                    model = generation.get("model", "Unknown")
                    seed = generation.get("seed", "Unknown")
                    censored = generation.get("censored", False)
                    
                    print(f"   🤖 Worker: {worker_name}")
                    print(f"   🎨 Modello: {model}")
                    print(f"   🌱 Seed: {seed}")
                    if censored:
                        print(f"   ⚠️ Immagine censurata")
                    
                    downloaded_files.append({
                        'filepath': str(filepath),
                        'worker_name': worker_name,
                        'model': model,
                        'seed': seed,
                        'censored': censored
                    })
                    
                except Exception as e:
                    print(f"⚠️ Errore nel salvataggio immagine {i}: {e}")
                    continue
            
            return downloaded_files
            
        except Exception as e:
            print(f"❌ Errore nel download risultati: {e}")
            return None

def main():
    """Interfaccia principale"""
    print("🎨 AI Horde Text-to-Image Generator")
    print("=" * 60)
    
    # Inizializza generatore
    generator = AIHordeTextToImage()
    
    # Mostra info utente
    user_info = generator.get_user_info()
    if user_info:
        username = user_info.get('username', 'Unknown')
        kudos = user_info.get('kudos', 0)
        print(f"👤 Utente: {username}")
        print(f"💰 Kudos disponibili: {kudos}")
        
        if kudos < 25:
            print("⚠️ Pochi kudos disponibili - tempi di attesa potrebbero essere lunghi")
    else:
        print("⚠️ Impossibile recuperare info utente")
    
    # Mostra modelli disponibili
    models = generator.get_available_models()
    if models:
        print(f"\n🎭 Modelli disponibili: {len(models)}")
        top_models = sorted(models, key=lambda x: x.get('count', 0), reverse=True)[:5]
        for i, model in enumerate(top_models, 1):
            name = model['name']
            workers = model.get('count', 0)
            queued = model.get('queued', 0)
            print(f"  {i}. {name} ({workers} workers, {queued} in coda)")
    
    # Menu principale
    while True:
        print("\n" + "=" * 60)
        print("📋 Opzioni:")
        print("1. Genera immagine con prompt personalizzato")
        print("2. Genera con parametri avanzati")
        print("3. Batch di immagini di test")
        print("4. Mostra esempi di prompt")
        print("5. Esci")
        
        try:
            choice = input("\n🎯 Scegli (1-5): ").strip()
            
            if choice == "1":
                prompt = input("📝 Inserisci il prompt: ").strip()
                if prompt:
                    results = generator.generate_image(prompt)
                    if results:
                        print(f"\n🎉 Successo! Generate {len(results)} immagini:")
                        for result in results:
                            print(f"  📁 {result['filepath']}")
                    else:
                        print("❌ Generazione fallita")
                
            elif choice == "2":
                prompt = input("📝 Prompt: ").strip()
                if not prompt:
                    continue
                
                print("\n🔧 Parametri avanzati (premi Enter per default):")
                width = int(input("📐 Larghezza (512): ") or "512")
                height = int(input("📐 Altezza (512): ") or "512")
                steps = int(input("🔧 Steps (30): ") or "30")
                cfg_scale = float(input("⚖️ CFG Scale (7.5): ") or "7.5")
                
                sampler = input("🎲 Sampler (k_euler_a): ").strip() or "k_euler_a"
                seed = input("🌱 Seed (vuoto per random): ").strip() or None
                
                nsfw = input("🔞 NSFW? (y/n): ").strip().lower() == 'y'
                
                # Modelli personalizzati
                model_input = input("🤖 Modelli (vuoto per auto): ").strip()
                models = [m.strip() for m in model_input.split(",")] if model_input else None
                
                results = generator.generate_image(
                    prompt,
                    width=width,
                    height=height,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    sampler_name=sampler,
                    seed=seed,
                    nsfw=nsfw,
                    models=models
                )
                
                if results:
                    print(f"\n🎉 Successo! Generate {len(results)} immagini")
                else:
                    print("❌ Generazione fallita")
                
            elif choice == "3":
                test_prompts = [
                    "a beautiful sunset over mountains, photorealistic",
                    "a cute cat sleeping on a sofa, digital art",
                    "abstract geometric patterns in blue and gold",
                    "a cyberpunk cityscape at night, neon lights"
                ]
                
                print(f"🔄 Generando {len(test_prompts)} immagini di test...")
                for i, prompt in enumerate(test_prompts, 1):
                    print(f"\n--- Test {i}/{len(test_prompts)} ---")
                    results = generator.generate_image(prompt, steps=20)
                    if results:
                        print(f"✅ Test {i} completato")
                    else:
                        print(f"❌ Test {i} fallito")
                
            elif choice == "4":
                print("\n💡 Esempi di prompt efficaci:")
                examples = [
                    "a majestic lion in the savanna, golden hour lighting, photorealistic",
                    "cyberpunk street scene with neon signs, rain reflections, cinematic",
                    "beautiful landscape painting, mountains and lake, impressionist style",
                    "cute robot character, 3D render, Pixar style animation",
                    "abstract art with flowing colors, digital painting, vibrant",
                    "vintage car on empty road, sunset background, film photography",
                    "magical forest with glowing mushrooms, fantasy art, ethereal",
                    "modern architecture building, minimalist design, black and white"
                ]
                
                for i, example in enumerate(examples, 1):
                    print(f"  {i}. {example}")
                
            elif choice == "5":
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
