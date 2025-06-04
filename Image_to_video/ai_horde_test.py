#!/usr/bin/env python3
"""
Script di test per AI Horde API
Testa la generazione di immagini usando l'API di Stable Horde
"""

import requests
import time
import json
import os
from pathlib import Path
from datetime import datetime

# La tua API key per AI Horde
API_KEY = "xbCXATE-9l8CPYqfojI9iQ"
BASE_URL = "https://stablehorde.net/api/v2"

def check_api_status():
    """Verifica lo stato dell'API e i modelli disponibili"""
    try:
        print("🔍 Controllo stato API...")
        
        # Verifica stato generale
        response = requests.get(f"{BASE_URL}/status/heartbeat")
        if response.status_code == 200:
            print("✅ API Horde online e funzionante")
        else:
            print(f"❌ Problema con l'API: {response.status_code}")
            return False
        
        # Verifica modelli disponibili
        models_response = requests.get(f"{BASE_URL}/status/models")
        if models_response.status_code == 200:
            models = models_response.json()
            active_models = [m for m in models if m.get('queued', 0) >= 0]
            print(f"📊 Modelli disponibili: {len(active_models)}")
            
            # Mostra i primi 5 modelli più popolari
            popular_models = sorted(active_models, key=lambda x: x.get('jobs', 0), reverse=True)[:5]
            print("🎨 Top 5 modelli più usati:")
            for model in popular_models:
                name = model.get('name', 'Unknown')
                jobs = model.get('jobs', 0)
                eta = model.get('eta', 0)
                print(f"  • {name} (Jobs: {jobs}, ETA: {eta}s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nel controllo API: {e}")
        return False

def check_user_info():
    """Verifica informazioni sull'utente e i kudos disponibili"""
    try:
        print("\n👤 Controllo informazioni utente...")
        
        headers = {
            "apikey": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/find_user", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Utente: {user_info.get('username', 'Anonimo')}")
            print(f"💰 Kudos disponibili: {user_info.get('kudos', 0)}")
            print(f"🏆 Contribuzioni: {user_info.get('contributions', 0)}")
            print(f"📊 Richieste completate: {user_info.get('usage', 0)}")
            return user_info.get('kudos', 0)
        else:
            print(f"⚠️ Impossibile recuperare info utente: {response.status_code}")
            print("💡 Usando modalità anonima...")
            return None
            
    except Exception as e:
        print(f"❌ Errore nel controllo utente: {e}")
        return None

def generate_image(prompt, width=512, height=512, steps=30, model="Deliberate v3"):
    """Genera un'immagine usando AI Horde"""
    try:
        print(f"\n🎨 Avvio generazione immagine...")
        print(f"📝 Prompt: {prompt}")
        print(f"📐 Dimensioni: {width}x{height}")
        print(f"🔧 Passi: {steps}")
        print(f"🤖 Modello: {model}")
        
        # Payload per la richiesta
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
            "r2": True,  # Usa R2 storage per risultati più veloci
            "shared": False,  # Non condividere l'immagine pubblicamente
            "replacement_filter": True  # Filtra contenuti inappropriati
        }
        
        headers = {
            "apikey": API_KEY,
            "Content-Type": "application/json"
        }
        
        # Invia la richiesta
        print("📤 Invio richiesta...")
        response = requests.post(f"{BASE_URL}/generate/async", json=payload, headers=headers)
        
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
        
        # Monitora il progresso
        return monitor_generation(job_id)
        
    except Exception as e:
        print(f"❌ Errore nella generazione: {e}")
        return None

def monitor_generation(job_id):
    """Monitora il progresso della generazione"""
    try:
        print(f"⏳ Monitoraggio job {job_id}...")
        
        max_wait_time = 300  # 5 minuti massimo
        start_time = time.time()
        poll_interval = 3  # Controlla ogni 3 secondi
        
        while True:
            # Controlla timeout
            if time.time() - start_time > max_wait_time:
                print("⏰ Timeout raggiunto!")
                return None
            
            # Controlla stato
            response = requests.get(f"{BASE_URL}/generate/check/{job_id}")
            
            if response.status_code != 200:
                print(f"❌ Errore nel controllo stato: {response.status_code}")
                return None
            
            status = response.json()
            
            # Mostra progresso
            queue_position = status.get("queue_position", 0)
            wait_time = status.get("wait_time", 0)
            is_possible = status.get("is_possible", True)
            
            if queue_position > 0:
                print(f"📊 Posizione in coda: {queue_position}, Tempo stimato: {wait_time}s")
            
            if not is_possible:
                print("❌ Generazione non possibile (modello non disponibile o parametri non validi)")
                return None
            
            # Controlla se completato
            if status.get("done", False):
                print("✅ Generazione completata!")
                return download_results(job_id, status)
            
            # Controlla se fallito
            if status.get("faulted", False):
                print("❌ Generazione fallita")
                return None
            
            # Aspetta prima del prossimo controllo
            time.sleep(poll_interval)
            
    except Exception as e:
        print(f"❌ Errore nel monitoraggio: {e}")
        return None

def download_results(job_id, status):
    """Scarica i risultati della generazione"""
    try:
        print("📥 Download risultati...")
        
        # Ottieni i risultati finali
        response = requests.get(f"{BASE_URL}/generate/status/{job_id}")
        
        if response.status_code != 200:
            print(f"❌ Errore nel download: {response.status_code}")
            return None
        
        result = response.json()
        generations = result.get("generations", [])
        
        if not generations:
            print("❌ Nessuna immagine generata")
            return None
        
        # Crea cartella per i risultati
        output_dir = Path("ai_horde_results")
        output_dir.mkdir(exist_ok=True)
        
        downloaded_files = []
        
        for i, gen in enumerate(generations):
            img_url = gen.get("img")
            if not img_url:
                continue
            
            # Scarica l'immagine
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                # Genera nome file con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ai_horde_{job_id}_{i}_{timestamp}.png"
                filepath = output_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"✅ Salvata: {filepath}")
                downloaded_files.append(str(filepath))
                
                # Mostra info addizionali
                worker_name = gen.get("worker_name", "Unknown")
                worker_id = gen.get("worker_id", "Unknown")
                model = gen.get("model", "Unknown")
                print(f"   Worker: {worker_name} (ID: {worker_id})")
                print(f"   Modello: {model}")
        
        return downloaded_files
        
    except Exception as e:
        print(f"❌ Errore nel download: {e}")
        return None

def test_basic_generation():
    """Test di base con prompt semplice"""
    prompt = "a beautiful landscape with mountains and a lake, photorealistic, high quality"
    return generate_image(prompt, width=512, height=512, steps=25)

def test_advanced_generation():
    """Test avanzato con prompt più complesso"""
    prompt = ("a cyberpunk cityscape at night, neon lights reflecting on wet streets, "
              "futuristic buildings, highly detailed, cinematic lighting, 8k resolution")
    return generate_image(prompt, width=768, height=512, steps=30, model="Realistic Vision v5.0")

def main():
    """Funzione principale di test"""
    print("🚀 AI Horde API Test Script")
    print("=" * 50)
    
    # Controlla stato API
    if not check_api_status():
        print("❌ API non disponibile. Termino il test.")
        return
    
    # Controlla informazioni utente
    kudos = check_user_info()
    
    if kudos is not None and kudos < 10:
        print(f"⚠️ Pochi kudos disponibili ({kudos}). Potresti avere tempi di attesa lunghi.")
    
    # Menu di scelta
    print("\n📋 Scegli il tipo di test:")
    print("1. Test base (512x512, 25 steps)")
    print("2. Test avanzato (768x512, 30 steps)")
    print("3. Test personalizzato")
    print("4. Esci")
    
    try:
        choice = input("\n🎯 Inserisci la tua scelta (1-4): ").strip()
        
        if choice == "1":
            result = test_basic_generation()
        elif choice == "2":
            result = test_advanced_generation()
        elif choice == "3":
            # Test personalizzato
            custom_prompt = input("📝 Inserisci il prompt: ").strip()
            if custom_prompt:
                result = generate_image(custom_prompt)
            else:
                print("❌ Prompt vuoto!")
                return
        elif choice == "4":
            print("👋 Arrivederci!")
            return
        else:
            print("❌ Scelta non valida!")
            return
        
        # Mostra risultati
        if result:
            print(f"\n🎉 Test completato con successo!")
            print(f"📁 File salvati: {len(result)}")
            for file in result:
                print(f"   • {file}")
        else:
            print("\n❌ Test fallito!")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrotto dall'utente")
    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")

if __name__ == "__main__":
    main()
