"""Upload TikTok - cada video em subprocess isolado (sem asyncio residual)."""
import sys, subprocess, json
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path

VIDEOS = [
    {
        "mp4": "output/20260522_164419_shorts.mp4",
        "title": "They're Pretending to Like You",
        "tags": ["dark psychology","toxic people","narcissist","fake friends","psychology","mindset","fyp","shorts"],
    },
    {
        "mp4": "output/20260522_164345_shorts.mp4",
        "title": "What's Really Controlling Your Mind",
        "tags": ["dark psychology","mind control","brain","psychology facts","manipulation","mindset","fyp","shorts"],
    },
    {
        "mp4": "output/20260522_165145_shorts.mp4",
        "title": "Your Brain Is Wired To Remember Your Worst Fears",
        "tags": ["dark psychology","sleep","brain","nightmares","fear","psychology","fyp","shorts"],
    },
    {
        "mp4": "output/20260522_165248_shorts.mp4",
        "title": "Manipulation By The Rich",
        "tags": ["dark psychology","money","wealth","poor","rich","psychology","fyp","shorts"],
    },
]

total = len(VIDEOS)
ok = 0
script = Path(__file__).parent / "_tt_one.py"

for i, v in enumerate(VIDEOS):
    mp4 = Path(v["mp4"])
    if not mp4.exists():
        print(f"[{i+1}/{total}] SKIP: {mp4.name}")
        continue

    print(f"\n[{i+1}/{total}] {v['title']}")
    r = subprocess.run(
        [sys.executable, str(script), str(mp4), v["title"], json.dumps(v["tags"])],
        cwd=Path(__file__).parent,
    )
    if r.returncode == 0:
        ok += 1
        print(f"  -> OK")
    else:
        print(f"  -> FAILED")

print(f"\n[DONE] {ok}/{total} uploaded to TikTok")
