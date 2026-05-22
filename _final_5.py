"""
Gera sleep + money videos e faz TikTok upload de todos os 5 temas distintos.
IMPORTANTE: gera TUDO primeiro (async), depois faz uploads (sync puro).
"""
import sys, asyncio
if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr,'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from modules.ffmpeg_helper import ensure_ffmpeg
ensure_ffmpeg()

# ── FASE 1: Gerar sleep + money (sem upload) ──────────────────────────────────
from main import run_pipeline

async def generate_two():
    results = []
    for topic in [
        "terrifying things that happen to your brain and body while you sleep tonight",
        "dark psychology of money why poor people stay poor and rich get richer",
    ]:
        print(f"\n[GEN] {topic[:60]}...")
        try:
            r = await run_pipeline(mode="shorts", manual_topic=topic,
                                   upload=False, niche="dark psychology")
            results.append(r)
            print(f"  -> {r.get('title','?')} | {r.get('video','?')}")
        except Exception as e:
            print(f"  [X] Failed: {e}")
            import traceback; traceback.print_exc()
    return results

print("\n" + "="*55)
print("FASE 1: Gerando 2 videos (sleep + money)")
print("="*55)
new_results = asyncio.run(generate_two())

# ── FASE 2: Upload TikTok de todos os 5 (sync puro, FORA de asyncio) ─────────
from modules.tiktok_uploader import TikTokUploader
from config import Config

cfg = Config()
tt = TikTokUploader(cfg)

# 3 prontos + 2 recém-gerados
UPLOADS = [
    {
        "mp4": Path("output/20260522_164602_shorts.mp4"),
        "title": "You're Hooked On Your Phone",
        "tags": ["phone addiction","dark psychology","dopamine","social media","psychology","mindset","fyp","shorts"],
    },
    {
        "mp4": Path("output/20260522_164419_shorts.mp4"),
        "title": "They're Pretending to Like You",
        "tags": ["dark psychology","toxic people","narcissist","psychology","fake friends","mindset","fyp","shorts"],
    },
    {
        "mp4": Path("output/20260522_164345_shorts.mp4"),
        "title": "What's Really Controlling Your Mind",
        "tags": ["dark psychology","mind control","manipulation","brain","psychology facts","mindset","fyp","shorts"],
    },
]

# Adiciona os 2 recém-gerados
for r in new_results:
    mp4 = Path(r.get("video",""))
    if mp4.exists():
        UPLOADS.append({
            "mp4": mp4,
            "title": r.get("title", "Dark Psychology Facts"),
            "tags": ["dark psychology","psychology","mindset","brain","fyp","shorts"],
        })

print("\n" + "="*55)
print(f"FASE 2: TikTok upload de {len(UPLOADS)} videos")
print("="*55)

for i, v in enumerate(UPLOADS):
    if not v["mp4"].exists():
        print(f"\n[{i+1}/{len(UPLOADS)}] SKIP (not found): {v['mp4'].name}")
        continue
    print(f"\n[{i+1}/{len(UPLOADS)}] {v['title']}")
    result = tt.upload(
        video_path=v["mp4"],
        title=v["title"],
        description=v["title"],
        tags=v["tags"],
        mode="shorts"
    )
    print(f"  -> {result}")

print("\n" + "="*55)
print("[DONE] Todos os uploads TikTok concluidos!")
print("="*55)
