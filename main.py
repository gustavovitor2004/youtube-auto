"""
YouTube Automation System -- Main Orchestrator
100% gratuito | edge-tts + Whisper + FFmpeg + Pexels + Pillow
"""

import asyncio
import argparse
import shutil
import json
from pathlib import Path
from datetime import datetime

from config import Config
from modules import (
    TrendFinder, ScriptGenerator, VoiceGenerator,
    SubtitleGenerator, VideoCreator, ThumbnailCreator,
    YouTubeUploader, TikTokUploader, AnalyticsManager
)
from modules.ffmpeg_helper import ensure_ffmpeg


def banner():
    print("""
+------------------------------------------------------+
|       YouTube Automation System -- Free Stack        |
|   edge-tts | Whisper | FFmpeg | Pexels | Pillow      |
+------------------------------------------------------+
""")


async def run_pipeline(mode: str = "shorts",
                       manual_topic: str = None,
                       manual_script_path: str = None,
                       upload: bool = False,
                       niche: str = None) -> dict:
    banner()
    config = Config()
    if niche:
        config.CHANNEL_NICHE = niche

    # --- Verifica FFmpeg -------------------------------------------------------
    ffmpeg_ok = ensure_ffmpeg()
    if not ffmpeg_ok:
        print("\n[!] Continuing without FFmpeg -- video creation will be SKIPPED")
        print("   (Voice + Subtitles will still be generated for preview)\n")

    # --- Setup ----------------------------------------------------------------
    ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = Path(config.TEMP_DIR) / ts
    session_dir.mkdir(parents=True, exist_ok=True)
    Path(config.OUTPUT_DIR).mkdir(exist_ok=True)

    print(f"[VIDEO] Mode : {mode.upper()}")
    print(f"[*]    Niche: {config.CHANNEL_NICHE}")
    print(f"[*]    Session: {session_dir}\n")

    # --- STEP 1: Trend Research -----------------------------------------------
    print("=" * 55)
    print("STEP 1 > TREND RESEARCH")
    print("=" * 55)

    if manual_topic:
        topic = manual_topic
        print(f"   [OK] Manual topic: {topic}")
    else:
        finder = TrendFinder()
        topics = finder.get_trending_topics(config.CHANNEL_NICHE)
        topic = _pick_best_topic(topics, config.CHANNEL_NICHE)

    # --- STEP 2: Script Generation --------------------------------------------
    print("\n" + "=" * 55)
    print("STEP 2 > SCRIPT GENERATION")
    print("=" * 55)

    generator = ScriptGenerator(config)

    if manual_script_path and Path(manual_script_path).exists():
        script_text = Path(manual_script_path).read_text(encoding="utf-8")
        script_data = generator.generate_from_manual_script(topic, script_text, mode)
        print(f"   [OK] Manual script loaded ({len(script_text)} chars)")
    else:
        script_data = generator.generate(topic, mode)
        print(f"   [OK] Script: \"{script_data['title']}\"")
        print(f"   Words: {len(script_data['script'].split())}")

    # Salva script para revisao
    script_file = session_dir / "script.json"
    script_file.write_text(json.dumps(script_data, indent=2, ensure_ascii=False))

    # --- STEP 3: Voice Generation ---------------------------------------------
    print("\n" + "=" * 55)
    print("STEP 3 > VOICE GENERATION (edge-tts)")
    print("=" * 55)

    voice_path = session_dir / "voiceover.mp3"
    voice_gen  = VoiceGenerator(config)
    await voice_gen.generate(script_data["script"], voice_path, mode)
    duration = voice_gen.get_duration(voice_path)
    print(f"   [OK] Audio duration: {duration:.1f}s")

    # Se FFmpeg nao esta disponivel, para aqui
    if not ffmpeg_ok:
        _print_partial_result(voice_path, script_data, session_dir)
        return {"voice": str(voice_path), "title": script_data["title"], "topic": topic}

    # --- STEP 4: Subtitles ----------------------------------------------------
    print("\n" + "=" * 55)
    print("STEP 4 > SUBTITLE GENERATION (Whisper)")
    print("=" * 55)

    srt_path = session_dir / "subtitles.srt"
    sub_gen  = SubtitleGenerator(config)
    sub_gen.generate(voice_path, srt_path, mode)

    # --- STEP 5: Video Assembly -----------------------------------------------
    print("\n" + "=" * 55)
    print("STEP 5 > VIDEO CREATION (Pexels + FFmpeg)")
    print("=" * 55)

    video_path    = session_dir / "final_video.mp4"
    video_creator = VideoCreator(config)
    video_creator.create(
        audio_path=voice_path,
        srt_path=srt_path,
        topic=topic,
        mode=mode,
        output_path=video_path
    )

    # --- STEP 6: Thumbnail ----------------------------------------------------
    print("\n" + "=" * 55)
    print("STEP 6 > THUMBNAIL CREATION (Pillow)")
    print("=" * 55)

    thumb_path    = session_dir / "thumbnail.jpg"
    thumb_creator = ThumbnailCreator(config)
    thumb_creator.create(
        title=script_data["title"],
        topic=topic,
        output_path=thumb_path
    )

    # --- Copy to output/ ------------------------------------------------------
    final_video = Path(config.OUTPUT_DIR) / f"{ts}_{mode}.mp4"
    final_thumb = Path(config.OUTPUT_DIR) / f"{ts}_{mode}_thumb.jpg"
    shutil.copy(video_path, final_video)
    if thumb_path.exists():
        shutil.copy(thumb_path, final_thumb)

    print(f"\n{'='*55}")
    print("[OK] PIPELINE COMPLETE!")
    print(f"{'='*55}")
    print(f"[VIDEO]  Video     : {final_video}")
    print(f"[IMAGE]  Thumbnail : {final_thumb}")
    print(f"[TITLE]  Title     : {script_data['title']}")
    tags = script_data.get("tags", [])
    if tags:
        print(f"[TAGS]   Tags      : {', '.join(tags[:5])}...")

    # --- STEP 7: Upload (YouTube + TikTok) ------------------------------------
    if upload:
        title       = script_data["title"]
        description = script_data.get("description", "")
        tags        = script_data.get("tags", [])

        # YouTube
        print(f"\n{'='*55}")
        print("STEP 7a > UPLOADING TO YOUTUBE SHORTS")
        print(f"{'='*55}")
        yt = YouTubeUploader(config)
        yt_url = yt.upload(
            video_path=final_video,
            thumbnail_path=final_thumb,
            title=title,
            description=description,
            tags=tags,
            mode=mode
        )
        if yt_url and yt_url.startswith("http"):
            print(f"   YouTube: {yt_url}")

        # TikTok
        print(f"\n{'='*55}")
        print("STEP 7b > UPLOADING TO TIKTOK")
        print(f"{'='*55}")
        tt = TikTokUploader(config)
        tt.upload(
            video_path=final_video,
            title=title,
            description=description,
            tags=tags,
            mode=mode
        )
    else:
        print("\n[i] To upload: run with --upload flag")
        print("   Setup YouTube : python setup_youtube.py")
        print("   Setup TikTok  : python setup_tiktok.py")

    return {
        "video":     str(final_video),
        "thumbnail": str(final_thumb),
        "title":     script_data["title"],
        "topic":     topic,
        "script":    str(script_file),
    }


def _pick_best_topic(topics: list[str], niche: str) -> str:
    """
    Evita topicos muito genericos.
    Prefere topicos com mais de 4 palavras e que parecam um titulo real.
    """
    scored = []
    for t in topics:
        words = t.split()
        score = 0
        score += min(len(words), 8)
        score -= 3 if t.lower().startswith("the ") and len(words) < 4 else 0
        score += 2 if any(w in t.lower() for w in ["secret","dark","hidden","truth","signs","why","how"]) else 0
        scored.append((score, t))

    scored.sort(reverse=True)
    best = scored[0][1]
    print(f"   -> Selected topic: \"{best}\"")
    return best


def _print_partial_result(voice_path: Path, script_data: dict, session_dir: Path):
    """Mostra resultado parcial quando FFmpeg nao esta disponivel."""
    print(f"\n{'='*55}")
    print("[!] PARTIAL RESULT (FFmpeg missing -- install to generate video)")
    print(f"{'='*55}")
    print(f"[AUDIO]  Audio  : {voice_path}")
    print(f"[TITLE]  Title  : {script_data['title']}")
    print(f"[SCRIPT] Script : {session_dir / 'script.json'}")
    print(f"\n{'='*55}")
    print("NEXT STEPS:")
    print("1. Install FFmpeg (see instructions above)")
    print("2. Run: python main.py")
    print(f"{'='*55}")


async def run_bulk(count: int, mode: str, niche: str,
                   upload: bool = False, topics: list = None):
    print(f"\n[BULK] {count} videos | {mode} | {niche} | upload={upload}")
    results = []
    for i in range(count):
        print(f"\n{'#'*55}")
        print(f"  VIDEO {i+1}/{count}")
        print(f"{'#'*55}")
        topic = topics[i] if topics and i < len(topics) else None
        try:
            r = await run_pipeline(mode=mode, niche=niche,
                                   manual_topic=topic, upload=upload)
            results.append(r)
        except Exception as e:
            print(f"   [X] Video {i+1} failed: {e}")
            import traceback; traceback.print_exc()
    print(f"\n{'='*55}")
    print(f"[OK] Bulk complete: {len(results)}/{count} succeeded")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Automation System -- Free Stack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python main.py                              # 1 Short, auto topic
  python main.py --mode longform             # 1 long-form video
  python main.py --topic "narcissist signs"  # Custom topic
  python main.py --script my_script.txt      # Use your own script
  python main.py --upload                    # Auto-upload to YouTube+TikTok
  python main.py --bulk 5                    # Generate 5 videos
  python main.py --analytics                 # Show channel analytics
  python main.py --niche "true crime"        # Change niche
"""
    )
    parser.add_argument("--mode",      choices=["shorts", "longform"], default="shorts")
    parser.add_argument("--topic",     type=str,  help="Manual topic")
    parser.add_argument("--script",    type=str,  help="Path to manual script .txt")
    parser.add_argument("--upload",    action="store_true")
    parser.add_argument("--bulk",      type=int, default=0)
    parser.add_argument("--niche",     type=str)
    parser.add_argument("--analytics", action="store_true")

    args = parser.parse_args()

    if args.analytics:
        cfg = Config()
        am  = AnalyticsManager(cfg)
        am.analyze_recent(days=14)
        return

    if args.bulk > 0:
        asyncio.run(run_bulk(args.bulk, args.mode,
                             args.niche or "dark psychology",
                             upload=args.upload))
    else:
        asyncio.run(run_pipeline(
            mode=args.mode,
            manual_topic=args.topic,
            manual_script_path=args.script,
            upload=args.upload,
            niche=args.niche
        ))


if __name__ == "__main__":
    main()
