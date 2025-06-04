import os
import replicate
from dotenv import load_dotenv
from PIL import Image
import base64
import io

# Carica le variabili d'ambiente
load_dotenv()

class ImageToVideoConverter:
    def __init__(self):
        """Inizializza il convertitore con il token API di Replicate"""
        self.client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))
        
    def image_to_base64(self, image_path):
        """Converte un'immagine in base64"""
        try:
            with Image.open(image_path) as img:
                # Converti in RGB se necessario
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Converti in base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG')
                img_data = base64.b64encode(buffer.getvalue()).decode()
                return f"data:image/jpeg;base64,{img_data}"
        except Exception as e:
            print(f"Errore nella conversione dell'immagine: {e}")
            return None
    
    def convert_image_to_video(self, image_path, prompt="", seed=-1):
        """
        Converte un'immagine in video usando CogVideo di Replicate
        
        Args:
            image_path (str): Percorso dell'immagine
            prompt (str): Prompt per guidare la generazione del video
            seed (int): Seed per la generazione (-1 per random)
        
        Returns:
            str: URL del video generato
        """
        try:
            # Controlla se il file esiste
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"File immagine non trovato: {image_path}")
            
            # Converte l'immagine in base64
            base64_image = self.image_to_base64(image_path)
            if not base64_image:
                raise ValueError("Impossibile convertire l'immagine")
            
            print(f"Avvio conversione dell'immagine: {image_path}")
            print(f"Prompt: {prompt}")
            print(f"Seed: {seed}")
            
            # Prepara l'input per l'API
            input_data = {
                "image": base64_image,
                "prompt": prompt,
                "seed": str(seed)
            }
            
            print("Invio richiesta a Replicate...")
            
            # Chiama l'API di Replicate in streaming
            for event in replicate.stream(
                "nightmareai/cogvideo:00b1c7885c5f1d44b51bcb56c378abc8f141eeacf94c1e64998606515fe63a8d",
                input=input_data
            ):
                print(f"Evento ricevuto: {event}")
                
                # Se l'evento è un URL, ritornalo
                if isinstance(event, str) and event.startswith("http"):
                    print(f"✅ Video generato con successo: {event}")
                    return event
            
        except Exception as e:
            print(f"❌ Errore durante la conversione: {e}")
            return None
    
    def convert_multiple_images(self, image_folder, prompt="", seed=-1):
        """
        Converte multiple immagini in video
        
        Args:
            image_folder (str): Cartella contenente le immagini
            prompt (str): Prompt per guidare la generazione
            seed (int): Seed per la generazione
        
        Returns:
            list: Lista degli URL dei video generati
        """
        video_urls = []
        
        # Estensioni immagine supportate
        supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
        
        try:
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(supported_extensions):
                    image_path = os.path.join(image_folder, filename)
                    print(f"\n📸 Processando: {filename}")
                    
                    video_url = self.convert_image_to_video(image_path, prompt, seed)
                    if video_url:
                        video_urls.append({
                            'image': filename,
                            'video_url': video_url
                        })
                    else:
                        print(f"❌ Errore nella conversione di {filename}")
            
            return video_urls
            
        except Exception as e:
            print(f"Errore nella processazione delle immagini: {e}")
            return []

def main():
    """Funzione principale per testare il convertitore"""
    converter = ImageToVideoConverter()
    
    # Esempio di utilizzo con un'immagine singola
    image_path = input("Inserisci il percorso dell'immagine: ").strip()
    
    if not image_path:
        print("Percorso immagine non fornito. Uscita.")
        return
    
    prompt = input("Inserisci un prompt (opzionale): ").strip()
    
    try:
        seed_input = input("Inserisci un seed (-1 per random): ").strip()
        seed = int(seed_input) if seed_input else -1
    except ValueError:
        seed = -1
    
    # Converte l'immagine in video
    video_url = converter.convert_image_to_video(image_path, prompt, seed)
    
    if video_url:
        print(f"\n🎉 Conversione completata!")
        print(f"📹 URL del video: {video_url}")
    else:
        print("\n❌ Conversione fallita")

if __name__ == "__main__":
    main()
