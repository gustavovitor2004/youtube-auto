import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ─── FREE API Keys ─────────────────────────────────────────────────────────
    # Pexels: grátis em pexels.com/api (200 req/hora)
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

    # YouTube: grátis no Google Cloud Console
    YOUTUBE_CLIENT_SECRETS = "client_secrets.json"

    # ─── LLM Local (Ollama - 100% gratuito) ───────────────────────────────────
    # Instale: https://ollama.com → depois: ollama pull llama3.2
    OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_BASE_URL = "http://localhost:11434"

    # ─── Canal ────────────────────────────────────────────────────────────────
    CHANNEL_NAME      = "MindVault"
    CHANNEL_NICHE     = "dark psychology"
    CHANNEL_LANGUAGE  = "en"

    # YouTube: youtube.com/channel/UC--ZWl2W0kVGKUVb4czV6Rg
    YOUTUBE_CHANNEL_ID = "UC--ZWl2W0kVGKUVb4czV6Rg"

    # TikTok: tiktok.com/@mind.vauit
    TIKTOK_HANDLE      = "@mind.vauit"

    # ─── Voz (edge-tts - gratuito, vozes Microsoft) ───────────────────────────
    # Rode `edge-tts --list-voices` para ver todas as opções
    VOICE_SHORTS   = "en-US-GuyNeural"    # Voz masculina energética
    VOICE_LONGFORM = "en-US-AriaNeural"   # Voz feminina profissional
    VOICE_RATE     = "+15%"               # Velocidade (+/- %)
    VOICE_VOLUME   = "+0%"

    # ─── Vídeo ────────────────────────────────────────────────────────────────
    SHORTS_W, SHORTS_H   = 1080, 1920
    LONGFORM_W, LONGFORM_H = 1920, 1080
    FPS = 30

    # ─── Velocidade ───────────────────────────────────────────────────────────
    VIDEO_SPEED = 1.25  # 1.0 = normal | 1.25 = snappy | 1.5 = brain-rot | 2.0 = máximo

    # ─── Legendas ─────────────────────────────────────────────────────────────
    SUBTITLE_SIZE_SHORTS   = 16
    SUBTITLE_SIZE_LONGFORM = 48

    # ─── Diretórios ───────────────────────────────────────────────────────────
    OUTPUT_DIR = "output"
    TEMP_DIR   = "temp"
    MUSIC_DIR  = "music"   # Coloque arquivos .mp3 royalty-free aqui

    # ─── Upload ───────────────────────────────────────────────────────────────
    UPLOAD_CATEGORY = "22"        # People & Blogs
    UPLOAD_PRIVACY  = "public"    # "public" → vai ao ar imediatamente
