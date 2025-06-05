#!/usr/bin/env python3
"""
Media Generator MVP - Startup Script
Avvia il backend e il frontend in modo coordinato
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path

# Colori per il terminale
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.OKGREEN):
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message):
    print_colored(f"\n{'='*60}", Colors.HEADER)
    print_colored(f"  {message}", Colors.HEADER)
    print_colored(f"{'='*60}", Colors.HEADER)

def check_requirements():
    """Controlla se Python e Node.js sono installati"""
    try:
        # Verifica Python
        python_version = subprocess.check_output([sys.executable, "--version"], text=True).strip()
        print_colored(f"✓ {python_version}", Colors.OKGREEN)
    except Exception as e:
        print_colored(f"✗ Python non trovato: {e}", Colors.FAIL)
        return False
    
    try:
        # Verifica Node.js
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print_colored(f"✓ Node.js {node_version}", Colors.OKGREEN)
    except Exception as e:
        print_colored(f"✗ Node.js non trovato: {e}", Colors.FAIL)
        print_colored("Installa Node.js da https://nodejs.org/", Colors.WARNING)
        return False
        
    try:
        # Verifica npm
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        print_colored(f"✓ npm {npm_version}", Colors.OKGREEN)
    except Exception as e:
        print_colored(f"✗ npm non trovato: {e}", Colors.FAIL)
        return False
    
    return True

def setup_backend():
    """Configura il backend"""
    print_header("Configurazione Backend")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_colored("✗ Directory backend non trovata", Colors.FAIL)
        return False
    
    os.chdir(backend_dir)
    
    # Controlla se .env esiste
    if not Path(".env").exists():
        print_colored("⚠ File .env non trovato, creando un template...", Colors.WARNING)
        env_content = """# Configura la tua API key qui
OPENAI_API_KEY=your_openai_api_key_here

# Database settings
DATABASE_URL=sqlite:///./data/app.db

# Application settings
DEBUG=true
HOST=0.0.0.0
PORT=8000
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print_colored("Template .env creato. Configura la tua OPENAI_API_KEY!", Colors.WARNING)
    
    # Installa dipendenze Python
    try:
        print_colored("Installazione dipendenze Python...", Colors.OKBLUE)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_colored("✓ Dipendenze Python installate", Colors.OKGREEN)
    except subprocess.CalledProcessError as e:
        print_colored(f"✗ Errore installazione dipendenze: {e}", Colors.FAIL)
        return False
    
    os.chdir("..")
    return True

def setup_frontend():
    """Configura il frontend"""
    print_header("Configurazione Frontend")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_colored("✗ Directory frontend non trovata", Colors.FAIL)
        return False
    
    os.chdir(frontend_dir)
    
    # Installa dipendenze Node.js
    try:
        print_colored("Installazione dipendenze Node.js...", Colors.OKBLUE)
        subprocess.run(["npm", "install"], check=True)
        print_colored("✓ Dipendenze Node.js installate", Colors.OKGREEN)
    except subprocess.CalledProcessError as e:
        print_colored(f"✗ Errore installazione dipendenze: {e}", Colors.FAIL)
        return False
    
    os.chdir("..")
    return True

def start_backend():
    """Avvia il server backend"""
    print_colored("🚀 Avvio del server backend...", Colors.OKBLUE)
    os.chdir("backend")
    
    # Usa uvicorn per avviare FastAPI
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "src.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])
    
    os.chdir("..")
    return process

def start_frontend():
    """Avvia il server frontend"""
    print_colored("🚀 Avvio del server frontend...", Colors.OKBLUE)
    os.chdir("frontend")
    
    # Usa npm start per React
    process = subprocess.Popen(["npm", "start"])
    
    os.chdir("..")
    return process

def main():
    """Funzione principale"""
    print_header("MEDIA GENERATOR MVP - AVVIO AUTOMATICO")
    
    # Controlla requisiti
    if not check_requirements():
        print_colored("❌ Requisiti non soddisfatti. Uscita.", Colors.FAIL)
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print_colored("❌ Errore nella configurazione del backend. Uscita.", Colors.FAIL)
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print_colored("❌ Errore nella configurazione del frontend. Uscita.", Colors.FAIL)
        sys.exit(1)
    
    print_header("AVVIO SERVIZI")
    
    # Lista per i processi
    processes = []
    
    try:
        # Avvia backend
        backend_process = start_backend()
        processes.append(backend_process)
        print_colored("✓ Backend avviato su http://localhost:8000", Colors.OKGREEN)
        
        # Aspetta un po' per dare tempo al backend di avviarsi
        time.sleep(3)
        
        # Avvia frontend
        frontend_process = start_frontend()
        processes.append(frontend_process)
        print_colored("✓ Frontend in avvio su http://localhost:3000", Colors.OKGREEN)
        
        print_header("SERVIZI ATTIVI")
        print_colored("🌐 Frontend: http://localhost:3000", Colors.OKCYAN)
        print_colored("🚀 Backend API: http://localhost:8000", Colors.OKCYAN)
        print_colored("📖 API Docs: http://localhost:8000/docs", Colors.OKCYAN)
        print_colored("\nPremi Ctrl+C per fermare tutti i servizi", Colors.WARNING)
        
        # Aspetta finché l'utente non interrompe
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print_colored("\n\n🛑 Interruzione richiesta. Chiusura servizi...", Colors.WARNING)
        
        # Termina tutti i processi
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print_colored("✓ Tutti i servizi sono stati fermati", Colors.OKGREEN)
        sys.exit(0)

if __name__ == "__main__":
    main()
