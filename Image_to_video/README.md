# Image to Video Converter + AI Horde Text-to-Image

Questo progetto include:
1. **Conversione immagini in video** utilizzando l'API di Replicate
2. **Generazione immagini da testo** utilizzando AI Horde (gratuito)
3. **Pipeline completa** da scene testuali a video cinematografici

## Setup

1. **Installa le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configura i token API:**
   
   **Per Replicate (image-to-video):**
   - Crea un account su [Replicate](https://replicate.com)
   - Ottieni il tuo API token
   - Modifica il file `.env`:
     ```
     REPLICATE_API_TOKEN=your_actual_token_here
     ```
   
   **Per AI Horde (text-to-image):**
   - Registrati su [AI Horde](https://stablehorde.net/)
   - La API key è già configurata nel progetto
   - Accesso gratuito con sistema kudos

## Utilizzo

### 🎨 Generazione Immagini da Testo (AI Horde)

#### Script Completo
```bash
python ai_horde_text_to_image.py
```

#### Test Rapido
```bash
python quick_ai_horde.py
```

#### Esempio Dimostrativo
```bash
python esempio_ai_horde.py
```

**Caratteristiche AI Horde:**
- ✅ **Completamente gratuito** con sistema kudos
- ✅ **50+ modelli** (Stable Diffusion, SDXL, Realistic Vision, etc.)
- ✅ **API ufficiale** stabile e veloce
- ✅ **Parametri avanzati**: resolution, steps, sampler, CFG scale
- ✅ **Download automatico** in formato WebP
- ✅ **Metadati completi**: worker, model, seed, etc.

**Esempi di prompt efficaci:**
```
"a beautiful sunset over mountains, photorealistic, high quality"
"cyberpunk cityscape at night, neon lights, cinematic lighting"
"cute cat sleeping on sofa, digital art, warm colors"
"abstract geometric patterns in blue and gold, modern art"
"vintage car on empty road, film photography, golden hour"
"magical forest with glowing mushrooms, fantasy art, ethereal"
```

**Modelli popolari disponibili:**
- `Realistic Vision v5.0` - Fotorealismo avanzato
- `Deliberate v3` - Stile artistico bilanciato  
- `SDXL 1.0` - Alta risoluzione e qualità
- `Anything v3` - Stile anime/manga
- `stable_diffusion` - Modello base veloce

### 🎬 Conversione Immagine in Video
```bash
python simple_converter.py
```
Modifica il file per inserire il percorso della tua immagine e il prompt.

### Metodo 2: Script interattivo
```bash
python image_to_video.py
```
Segui le istruzioni per inserire:
- Percorso dell'immagine
- Prompt (opzionale)
- Seed (opzionale, -1 per random)

### Metodo 3: Importa come modulo
```python
from image_to_video import ImageToVideoConverter

converter = ImageToVideoConverter()
video_url = converter.convert_image_to_video(
    "path/to/image.jpg", 
    "a beautiful video", 
    seed=-1
)
print(video_url)
```

## Formati supportati
- JPG/JPEG
- PNG
- BMP
- TIFF
- WebP

## Esempi di prompt
- "a black cat moving gracefully"
- "waves crashing on the shore"
- "clouds moving across the sky"
- "a person walking in a garden"

## Note
- La conversione può richiedere alcuni minuti
- Il video generato sarà in formato GIF
- Il modello utilizzato è `nightmareai/cogvideo`
