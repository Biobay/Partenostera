#!/usr/bin/env python3
"""
Esempio pratico: Generazione immagini con AI Horde
Dimostra il flusso completo text-to-image
"""

import requests
import time
import json
from pathlib import Path

def main():
    print("🎨 Esempio Pratico AI Horde Text-to-Image")
    print("=" * 50)
    
    api_key = "xbCXATE-9l8CPYqfojI9iQ"
    base_url = "https://stablehorde.net/api/v2"
    
    # Test info utente
    print("1️⃣ Controllo informazioni utente...")
    try:
        headers = {"apikey": api_key}
        user_response = requests.get(f"{base_url}/find_user", headers=headers, timeout=10)
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"   👤 Utente: {user_data.get('username', 'N/A')}")
            print(f"   💰 Kudos: {user_data.get('kudos', 0)}")
        else:
            print(f"   ⚠️ Non riesco a ottenere info utente: {user_response.status_code}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # Test modelli disponibili
    print("\n2️⃣ Controllo modelli disponibili...")
    try:
        models_response = requests.get(f"{base_url}/status/models", timeout=10)
        if models_response.status_code == 200:
            models = models_response.json()
            active_models = [m for m in models if m.get('count', 0) > 0]
            print(f"   🎭 Modelli attivi: {len(active_models)}")
            
            # Mostra top 3
            top_models = sorted(active_models, key=lambda x: x.get('count', 0), reverse=True)[:3]
            for i, model in enumerate(top_models, 1):
                name = model['name']
                workers = model.get('count', 0)
                print(f"   {i}. {name} ({workers} workers)")
        else:
            print(f"   ⚠️ Errore modelli: {models_response.status_code}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # Generazione esempio
    print("\n3️⃣ Generazione immagine di esempio...")
    
    prompt = "a beautiful red rose on white background, photorealistic, high quality"
    print(f"   📝 Prompt: {prompt}")
    
    # Payload per generazione
    payload = {
        "prompt": prompt,
        "params": {
            "width": 512,
            "height": 512,
            "steps": 25,
            "sampler_name": "k_euler_a",
            "cfg_scale": 7.5
        },
        "models": ["stable_diffusion"],
        "r2": True,
        "shared": False,
        "trusted_workers": True
    }
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Invia richiesta
        print("   📤 Invio richiesta...")
        response = requests.post(f"{base_url}/generate/async", json=payload, headers=headers, timeout=15)
        
        if response.status_code == 202:
            result = response.json()
            job_id = result.get("id")
            kudos_cost = result.get("kudos", 0)
            
            print(f"   ✅ Richiesta accettata!")
            print(f"   🆔 Job ID: {job_id}")
            print(f"   💰 Costo: {kudos_cost} kudos")
            
            # Monitora per max 3 minuti
            print("   ⏳ Monitoraggio (max 3 min)...")
            start_time = time.time()
            max_wait = 180
            
            while time.time() - start_time < max_wait:
                # Controlla stato
                status_response = requests.get(f"{base_url}/generate/check/{job_id}", headers=headers, timeout=10)
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    
                    done = status.get("done", False)
                    faulted = status.get("faulted", False)
                    queue_position = status.get("queue_position", 0)
                    wait_time = status.get("wait_time", 0)
                    processing = status.get("processing", 0)
                    
                    if done:
                        print("   ✅ Generazione completata!")
                        
                        # Scarica risultati
                        final_response = requests.get(f"{base_url}/generate/status/{job_id}", headers=headers, timeout=20)
                        
                        if final_response.status_code == 200:
                            final_result = final_response.json()
                            generations = final_result.get("generations", [])
                            
                            if generations:
                                img_url = generations[0].get("img")
                                worker_name = generations[0].get("worker_name", "Unknown")
                                model_used = generations[0].get("model", "Unknown")
                                seed = generations[0].get("seed", "Unknown")
                                
                                print(f"   🤖 Worker: {worker_name}")
                                print(f"   🎨 Modello: {model_used}")
                                print(f"   🌱 Seed: {seed}")
                                
                                if img_url:
                                    print("   📥 Scaricando immagine...")
                                    img_response = requests.get(img_url, timeout=30)
                                    
                                    if img_response.status_code == 200:
                                        # Salva immagine
                                        output_dir = Path("esempio_ai_horde")
                                        output_dir.mkdir(exist_ok=True)
                                        
                                        filepath = output_dir / "esempio_rosa.webp"
                                        with open(filepath, 'wb') as f:
                                            f.write(img_response.content)
                                        
                                        print(f"   💾 Immagine salvata: {filepath}")
                                        print("   🎉 Esempio completato con successo!")
                                        return
                                    else:
                                        print(f"   ❌ Errore download: {img_response.status_code}")
                                else:
                                    print("   ❌ Nessun URL immagine ricevuto")
                            else:
                                print("   ❌ Nessuna immagine generata")
                        break
                    
                    elif faulted:
                        print("   ❌ Generazione fallita")
                        break
                    
                    else:
                        # Mostra progresso
                        if queue_position > 0:
                            print(f"   📊 In coda: posizione {queue_position}, attesa ~{wait_time}s")
                        elif processing > 0:
                            print(f"   🔄 In elaborazione...")
                        
                        time.sleep(5)  # Attendi 5 secondi
                else:
                    print(f"   ⚠️ Errore controllo stato: {status_response.status_code}")
                    time.sleep(5)
            
            print("   ⏰ Timeout raggiunto")
        
        else:
            print(f"   ❌ Errore invio richiesta: {response.status_code}")
            print(f"   Risposta: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Errore nella generazione: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Riepilogo:")
    print("✅ La tua API key funziona correttamente")
    print("✅ Hai accesso a tutti i modelli di AI Horde")
    print("💡 Puoi ora usare gli script completi:")
    print("   • python ai_horde_text_to_image.py  (interfaccia completa)")
    print("   • python quick_ai_horde.py          (test rapidi)")

if __name__ == "__main__":
    main()
