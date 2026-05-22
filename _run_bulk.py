"""Script para rodar 5 videos com temas distintos — TikTok apenas hoje."""
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import asyncio
from modules.ffmpeg_helper import ensure_ffmpeg
ensure_ffmpeg()

from main import run_bulk

# 5 temas completamente diferentes:
# 1. Brain facts (curiosidade/perturbador)
# 2. Phone/scroll addiction (viral/relevante)
# 3. Sleep dark truth (curioso/diferente)
# 4. Money psychology (impacto/pratico)
# 5. Love dark side (emocional/relacionamento)
TOPICS = [
    "disturbing facts about your brain that will change how you see reality forever",
    "why you literally cannot stop scrolling your phone dark psychology of apps",
    "terrifying things that happen to your brain and body while you sleep tonight",
    "dark psychology of money why poor people stay poor and rich get richer",
    "why you keep falling in love with the wrong people dark psychology explained",
]

asyncio.run(run_bulk(
    count=5,
    mode="shorts",
    niche="dark psychology",
    upload=True,
    topics=TOPICS
))
