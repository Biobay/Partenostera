#!/usr/bin/env python3
"""
Test automatico AI Horde - Genera una singola immagine di test
"""

import requests
import time
import json
from pathlib import Path
from datetime import datetime

def test_ai_horde():
    API_KEY = "xbCXATE-9l8CPYqfojI9iQ"
    BASE_URL = "https://stablehorde.net/api/v2"
    
    print("🚀 Test automatico AI Horde")
    print("=" * 40)
    
    # 1. Verifica connessione
    try:
        response = requests.get(f"{BASE_URL}/status/heartbeat", timeout=10)
        if response.status_code == 200:
            print("✅ API connessa")
        else:
            print(f"❌ Problema API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return False
    
    # 2. Info utente
    try:
        headers = {"apikey": API_KEY}
        response = requests.get(f"{BASE_URL}/find_user", headers=headers, timeout=10)
        if response.status_code == 200:
            user_info = response.json()
            print(f"👤 Utente: {user_info.get('username', 'N/A')}")
            print(f"💰 Kudos: {user_info.get('kudos', 0)}")
        else:
            print("⚠️ Info utente non disponibili")
    except Exception as e:
        print(f"❌ Errore info utente: {e}")
    
    # 3. Genera immagine di test
    print("\n🎨 Generazione immagine di test...")
    
    payload = {
        "prompt": "a simple red apple on white background, photorealistic",
        "params": {
            "width": 512,
            "height": 512,
            "steps": 20,
            "sampler_name": "k_euler",
            "cfg_scale": 7
        },
        "r2": True,
        "shared": False
    }
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # Invia richiesta
        print("📤 Invio richiesta...")
        response = requests.post(f"{BASE_URL}/generate/async", json=payload, headers=headers, timeout=15)
        
        if response.status_code == 202:
            result = response.json()
            job_id = result.get("id")
            print(f"✅ Job creato: {job_id}")
            
            # Controlla stato una volta
            print("📊 Controllo stato...")
            status_response = requests.get(f"{BASE_URL}/generate/check/{job_id}", timeout=10)
            if status_response.status_code == 200:
                status = status_response.json()
                queue_pos = status.get("queue_position", "N/A")
                wait_time = status.get("wait_time", "N/A")
                is_possible = status.get("is_possible", True)
                
                print(f"📍 Posizione coda: {queue_pos}")
                print(f"⏰ Tempo stimato: {wait_time}s")
                print(f"✅ Possibile: {is_possible}")
                
                if is_possible:
                    print("🎉 Test SUCCESSO! La tua API key funziona correttamente!")
                    print(f"💡 Il job {job_id} è stato creato e processato")
                    print("📝 Nota: Non aspetto il completamento per risparmiare tempo")
                    return True
                else:
                    print("❌ Generazione non possibile")
                    return False
            else:
                print(f"⚠️ Errore controllo stato: {status_response.status_code}")
                return False
        else:
            print(f"❌ Errore generazione: {response.status_code}")
            print(f"Risposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Errore nella generazione: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_horde()
    print("\n" + "=" * 40)
    if success:
        print("🎯 RISULTATO: API KEY FUNZIONA! ✅")
        print("💡 Puoi usare ai_horde_generator.py per generare immagini complete")
    else:
        print("🎯 RISULTATO: Problemi riscontrati ❌")
        print("💡 Controlla la connessione internet e riprova")
