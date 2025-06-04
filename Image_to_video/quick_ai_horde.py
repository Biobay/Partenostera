#!/usr/bin/env python3
"""
AI Horde - Test Rapido Text-to-Image
Script semplificato per test veloci
"""

import requests
import time
import json
from pathlib import Path
from datetime import datetime

def quick_text_to_image(prompt, api_key="xbCXATE-9l8CPYqfojI9iQ"):
    """Genera rapidamente un'immagine da testo"""
    
    base_url = "https://stablehorde.net/api/v2"
    
    # Payload semplificato per test rapido
    payload = {
        "prompt": prompt,
        "params": {
            "width": 512,
            "height": 512,
            "steps": 20,  # Meno steps = più veloce
            "sampler_name": "k_euler",
            "cfg_scale": 7.0
        },
        "models": ["stable_diffusion"],  # Modello base più veloce
        "r2": True,
        "shared": False,
        "trusted_workers": True
    }
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"🎨 Generando: '{prompt}'")
    
    try:
        # 1. Invia richiesta
        print("📤 Invio richiesta...")
        response = requests.post(f"{base_url}/generate/async", json=payload, headers=headers, timeout=15)
        
        if response.status_code != 202:
            print(f"❌ Errore: {response.status_code} - {response.text}")
            return None
        
        job_id = response.json().get("id")
        print(f"✅ Job ID: {job_id}")
        
        # 2. Monitora (max 5 minuti)
        print("⏳ Attendendo completamento...")
        max_wait = 300
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Controlla stato
            status_response = requests.get(f"{base_url}/generate/check/{job_id}", headers=headers, timeout=10)
            
            if status_response.status_code == 200:
                status = status_response.json()
                
                if status.get("done"):
                    print("✅ Completato!")
                    break
                elif status.get("faulted"):
                    print("❌ Generazione fallita")
                    return None
                else:
                    queue_pos = status.get("queue_position", 0)
                    if queue_pos > 0:
                        print(f"📊 In coda: posizione {queue_pos}")
            
            time.sleep(5)
        else:
            print("⏰ Timeout")
            return None
        
        # 3. Scarica risultato
        print("📥 Scaricando immagine...")
        result_response = requests.get(f"{base_url}/generate/status/{job_id}", headers=headers, timeout=20)
        
        if result_response.status_code == 200:
            result = result_response.json()
            generations = result.get("generations", [])
            
            if generations:
                img_url = generations[0].get("img")
                if img_url:
                    # Scarica immagine
                    img_response = requests.get(img_url, timeout=30)
                    if img_response.status_code == 200:
                        # Salva file
                        output_dir = Path("quick_images")
                        output_dir.mkdir(exist_ok=True)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"quick_{timestamp}.webp"
                        filepath = output_dir / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        
                        print(f"💾 Salvata: {filepath}")
                        return str(filepath)
        
        print("❌ Nessuna immagine ricevuta")
        return None
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return None

def main():
    print("🚀 AI Horde - Test Rapido")
    print("=" * 40)
    
    # Test con prompt predefiniti
    test_prompts = [
        "a red apple on white background",
        "beautiful mountain landscape",
        "cute cartoon cat"
    ]
    
    print("Scegli:")
    print("1. Test automatico con prompt predefiniti")
    print("2. Prompt personalizzato")
    
    choice = input("\nScelta (1-2): ").strip()
    
    if choice == "1":
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n--- Test {i}/{len(test_prompts)} ---")
            result = quick_text_to_image(prompt)
            if result:
                print(f"✅ Successo: {result}")
            else:
                print("❌ Fallito")
                
    elif choice == "2":
        custom_prompt = input("\n📝 Inserisci il tuo prompt: ").strip()
        if custom_prompt:
            result = quick_text_to_image(custom_prompt)
            if result:
                print(f"🎉 Immagine generata: {result}")
            else:
                print("❌ Generazione fallita")
    else:
        print("❌ Scelta non valida")

if __name__ == "__main__":
    main()
