"""
Gera 3 videos HUMOR + upload YouTube + TikTok.
FASE 1: asyncio - gera + upload YouTube APENAS (upload_tiktok=False)
FASE 2: subprocess por video - upload TikTok (process isolation)
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

TOPICS = [
    "psychology of procrastination why your brain always says ill do it tomorrow and enjoys it",
    "the science of why you cringe so hard at your own voice on recordings",
    "why your brain thinks of the perfect comeback 3 hours after the argument ends",
]

TAGS_BY_TOPIC = [
    ["procrastination", "dark psychology", "relatable", "brain facts", "funny psychology",
     "psychology", "mindset", "fyp", "shorts"],
    ["cringe", "dark psychology", "relatable", "funny psychology", "brain",
     "psychology facts", "fyp", "shorts"],
    ["overthinking", "dark psychology", "relatable", "funny", "brain",
     "psychology", "mindset", "fyp", "shorts"],
]

async def generate_all():
    results = []
    for i, topic in enumerate(TOPICS):
        print(f"\n[GEN {i+1}/3] {topic[:65]}...")
        try:
            r = await run_pipeline(
                mode="shorts",
                manual_topic=topic,
                upload=True,
                upload_tiktok=False,   # TikTok feito depois via subprocess
                niche="dark psychology"
            )
            results.append((r, TAGS_BY_TOPIC[i]))
            print(f"  -> {r.get('title','?')} | {r.get('video','?')}")
        except Exception as e:
            print(f"  [X] Failed: {e}")
            import traceback; traceback.print_exc()
            results.append(({}, TAGS_BY_TOPIC[i]))
    return results

print("\n" + "="*57)
print("FASE 1: Gerando 3 videos humor + upload YouTube")
print("="*57)
results = asyncio.run(generate_all())

# ── FASE 2: TikTok via subprocess isolado ────────────────────────────────────
print("\n" + "="*57)
print("FASE 2: TikTok upload (subprocess isolado por video)")
print("="*57)

script = Path(__file__).parent / "_tt_one.py"
ok_tt = 0
total_tt = 0

for r, tags in results:
    mp4 = Path(r.get("video", ""))
    if not mp4.exists():
        print(f"\n[SKIP] Video nao encontrado: {mp4}")
        continue

    total_tt += 1
    title = r.get("title", "Dark Psychology Humor Facts")
    print(f"\n[TikTok] {title}")

    proc = subprocess.run(
        [sys.executable, str(script), str(mp4), title, json.dumps(tags)],
        cwd=Path(__file__).parent,
    )
    if proc.returncode == 0:
        ok_tt += 1
        print(f"  -> TikTok OK")
    else:
        print(f"  -> TikTok FAILED")

print(f"\n{'='*57}")
print(f"[DONE] TikTok: {ok_tt}/{total_tt} | YouTube: veja logs acima")
print("="*57)
