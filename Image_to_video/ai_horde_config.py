# Configurazione AI Horde
# Questo file contiene le impostazioni per l'uso di AI Horde

# API Key (già configurata)
API_KEY = "xbCXATE-9l8CPYqfojI9iQ"

# URL Base API
BASE_URL = "https://stablehorde.net/api/v2"

# Impostazioni di default per la generazione
DEFAULT_SETTINGS = {
    "width": 512,
    "height": 512,
    "steps": 30,
    "cfg_scale": 7.5,
    "sampler_name": "k_euler_a"
}

# Modelli consigliati per diversi stili
RECOMMENDED_MODELS = {
    "fotorealistico": ["Realistic Vision v5.0", "Real-ESRGAN", "Deliberate v3"],
    "artistico": ["Deliberate v3", "Anything v3", "Waifu Diffusion"],
    "veloce": ["stable_diffusion", "SD 1.5"],
    "alta_qualita": ["SDXL 1.0", "SDXL Turbo"],
    "anime": ["Anything v3", "Waifu Diffusion", "NovelAI"],
    "fantasy": ["Dreamlike Photoreal", "Fantasy.ai", "Deliberate v3"]
}

# Prompt templates utili
PROMPT_TEMPLATES = {
    "fotorealistico": "{subject}, photorealistic, high quality, detailed, 8k resolution",
    "artistico": "{subject}, digital art, beautiful composition, trending on artstation",
    "cinematico": "{subject}, cinematic lighting, dramatic, film still, movie scene",
    "fantasy": "{subject}, fantasy art, magical, ethereal, mystical atmosphere",
    "cyberpunk": "{subject}, cyberpunk style, neon lights, futuristic, sci-fi",
    "vintage": "{subject}, vintage style, retro, film photography, nostalgic"
}

# Parametri ottimizzati per diversi tipi di immagine
OPTIMIZED_PARAMS = {
    "ritratto": {"width": 512, "height": 768, "steps": 35, "cfg_scale": 8.0},
    "paesaggio": {"width": 768, "height": 512, "steps": 30, "cfg_scale": 7.5},
    "quadrato": {"width": 512, "height": 512, "steps": 30, "cfg_scale": 7.5},
    "wallpaper": {"width": 1024, "height": 576, "steps": 40, "cfg_scale": 7.0},
    "mobile": {"width": 512, "height": 1024, "steps": 30, "cfg_scale": 7.5}
}

# Post-processing raccomandati
POST_PROCESSING_OPTIONS = [
    "RealESRGAN_x4plus",     # Upscaling generale
    "RealESRGAN_x4plus_anime", # Upscaling per anime
    "GFPGAN",                # Face restoration
    "CodeFormers"            # Alternative face restoration
]

# Negative prompts comuni per migliorare la qualità
NEGATIVE_PROMPTS = {
    "generale": "blurry, low quality, distorted, deformed, bad anatomy, worst quality, low res",
    "ritratto": "blurry, low quality, bad anatomy, deformed face, extra limbs, worst quality",
    "artistico": "amateur, low quality, worst quality, normal quality, jpeg artifacts, signature, watermark"
}

# Costi stimati in kudos (approssimativi)
KUDOS_COSTS = {
    "512x512_20steps": 3.0,
    "512x512_30steps": 4.5,
    "768x512_30steps": 6.8,
    "1024x1024_30steps": 18.0
}

# Suggerimenti per ottenere risultati migliori
TIPS = [
    "Usa descrizioni specifiche e dettagliate nei prompt",
    "Includi style keywords: 'photorealistic', 'digital art', 'cinematic'",
    "Specifica la qualità: 'high quality', '8k', 'detailed'",
    "Per ritratti usa: 'beautiful face', 'detailed eyes', 'sharp focus'",
    "Per paesaggi: 'landscape photography', 'golden hour', 'dramatic lighting'",
    "Evita prompt troppo lunghi (max 200 caratteri)",
    "Usa negative prompts per escludere elementi indesiderati",
    "Steps tra 20-40 sono sufficienti (più steps = più kudos)",
    "CFG Scale 7-8 funziona bene per la maggior parte dei casi"
]
