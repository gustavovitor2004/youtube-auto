"""
Continua _humor_3.py onde parou:
  - Gera + YouTube: apenas video 3 (perfect comeback)
  - TikTok: todos os 3 videos via subprocess isolado
Videos 1 e 2 ja foram gerados e enviados ao YouTube na tentativa anterior.
"""
import sys, asyncio, subprocess, json
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from modules.ffmpeg_helper import ensure_ffmpeg
ensure_ffmpeg()

from main import run_pipeline

# Videos 1 e 2 ja prontos no disco
READY = [
    {
        "mp4": Path("output/20260523_184842_shorts.mp4"),
        "title": "I'll Do It Tomorrow Syndrome Is Real",
        "tags": ["procrastination", "dark psychology", "relatable", "brain facts",
                 "funny psychology", "psychology", "mindset", "fyp", "shorts"],
    },
    {
        "mp4": Path("output/20260523_185208_shorts.mp4"),
        "title": "Audio Feedback: The Dark Side Of Self-Portrait Recording",
        "tags": ["cringe", "dark psychology", "relatable", "funny psychology",
                 "brain", "psychology facts", "fyp", "shorts"],
    },
]

# Gerar apenas o 3o video
TOPIC_3 = "why your brain thinks of the perfect comeback 3 hours after the argument ends"
TAGS_3  = ["overthinking", "dark psychology", "relatable", "funny", "brain",
            "psychology", "mindset", "fyp", "shorts"]

print("\n" + "="*57)
print("FASE 1: Gerando video 3 + upload YouTube")
print("="*57)

async def gen_third():
    print(f"\n[GEN 3/3] {TOPIC_3[:65]}...")
    try:
        r = await run_pipeline(
            mode="shorts",
            manual_topic=TOPIC_3,
            upload=True,
            upload_tiktok=False,
            niche="dark psychology"
        )
        print(f"  -> {r.get('title','?')} | {r.get('video','?')}")
        return r
    except Exception as e:
        print(f"  [X] Failed: {e}")
        import traceback; traceback.print_exc()
        return {}

result_3 = asyncio.run(gen_third())

# Monta lista completa para TikTok
tiktok_queue = list(READY)
mp4_3 = Path(result_3.get("video", ""))
if mp4_3.exists():
    tiktok_queue.append({
        "mp4": mp4_3,
        "title": result_3.get("title", "Perfect Comeback Psychology"),
        "tags": TAGS_3,
    })
else:
    print(f"\n[!] Video 3 nao encontrado em: {mp4_3}")

# ── FASE 2: TikTok via subprocess isolado ────────────────────────────────────
print("\n" + "="*57)
print(f"FASE 2: TikTok upload ({len(tiktok_queue)} videos)")
print("="*57)

script = Path(__file__).parent / "_tt_one.py"
ok_tt = 0

for i, v in enumerate(tiktok_queue):
    if not v["mp4"].exists():
        print(f"\n[{i+1}/{len(tiktok_queue)}] SKIP: {v['mp4'].name}")
        continue

    print(f"\n[{i+1}/{len(tiktok_queue)}] {v['title']}")
    proc = subprocess.run(
        [sys.executable, str(script), str(v["mp4"]), v["title"], json.dumps(v["tags"])],
        cwd=Path(__file__).parent,
    )
    if proc.returncode == 0:
        ok_tt += 1
        print(f"  -> TikTok OK")
    else:
        print(f"  -> TikTok FAILED")

print(f"\n{'='*57}")
print(f"[DONE] TikTok: {ok_tt}/{len(tiktok_queue)} | YouTube video 3: veja acima")
print("="*57)
