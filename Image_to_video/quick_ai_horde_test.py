#!/usr/bin/env python3
"""
Test veloce per AI Horde API - Versione semplificata
"""

import requests
import time
import json

# La tua API key
API_KEY = "xbCXATE-9l8CPYqfojI9iQ"
BASE_URL = "https://stablehorde.net/api/v2"

def quick_test():
    print("🚀 Test veloce AI Horde API")
    print("=" * 40)
    
    # 1. Test connessione
    print("🔍 Test connessione...")
    try:
        response = requests.get(f"{BASE_URL}/status/heartbeat", timeout=10)
        if response.status_code == 200:
            print("✅ API online!")
        else:
            print(f"❌ API problema: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return
    
    # 2. Test informazioni utente
    print("\n👤 Test informazioni utente...")
    try:
        headers = {"apikey": API_KEY}
        response = requests.get(f"{BASE_URL}/find_user", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Utente: {user_info.get('username', 'N/A')}")
            print(f"💰 Kudos: {user_info.get('kudos', 0)}")
        else:
            print(f"⚠️ Info utente non disponibili: {response.status_code}")
            print("Dettagli risposta:", response.text[:200])
    except Exception as e:
        print(f"❌ Errore info utente: {e}")
    
    # 3. Test modelli disponibili
    print("\n🎨 Test modelli disponibili...")
    try:
        response = requests.get(f"{BASE_URL}/status/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            active_models = [m for m in models if m.get('count', 0) > 0]
            print(f"✅ Modelli attivi: {len(active_models)}")
            
            # Mostra i primi 3 modelli
            for i, model in enumerate(active_models[:3]):
                name = model.get('name', 'Unknown')
                count = model.get('count', 0)
                queued = model.get('queued', 0)
                print(f"  {i+1}. {name} (Workers: {count}, Queue: {queued})")
        else:
            print(f"❌ Errore modelli: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore modelli: {e}")
    
    # 4. Test generazione semplice
    print("\n🎨 Test generazione immagine...")
    try:
        payload = {
            "prompt": "a simple red apple on a white background",
            "params": {
                "width": 512,
                "height": 512,
                "steps": 20,
                "sampler_name": "k_euler"
            },
            "models": ["stable_diffusion"],
            "r2": True,
            "shared": False
        }
        
        headers = {
            "apikey": API_KEY,
            "Content-Type": "application/json"
        }
        
        print("📤 Invio richiesta...")
        response = requests.post(f"{BASE_URL}/generate/async", json=payload, headers=headers, timeout=15)
        
        if response.status_code == 202:
            result = response.json()
            job_id = result.get("id")
            print(f"✅ Richiesta inviata! Job ID: {job_id}")
            
            # Verifica stato iniziale
            status_response = requests.get(f"{BASE_URL}/generate/check/{job_id}", timeout=10)
            if status_response.status_code == 200:
                status = status_response.json()
                queue_pos = status.get("queue_position", "N/A")
                wait_time = status.get("wait_time", "N/A")
                print(f"📊 Posizione coda: {queue_pos}")
                print(f"⏰ Tempo stimato: {wait_time}s")
                print("💡 Job creato con successo! (Non aspetto il completamento)")
            else:
                print(f"⚠️ Errore controllo stato: {status_response.status_code}")
        else:
            print(f"❌ Errore generazione: {response.status_code}")
            print("Risposta:", response.text[:200])
            
    except Exception as e:
        print(f"❌ Errore generazione: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Test completato!")
    print("💡 Se tutti i test sono ✅, la tua API key funziona correttamente!")

if __name__ == "__main__":
    quick_test()
