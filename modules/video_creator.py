"""
Video Creator — 100% gratuito
Usa: Pexels API (grátis), FFmpeg (grátis/open-source)
"""

import subprocess
import requests
import random
import shutil
import os
from pathlib import Path


VISUAL_MAP = {
    "psychology":   ["human brain concept", "psychology thinking", "mind concept"],
    "manipulation": ["chess strategy dark", "shadow control", "puppet strings"],
    "narcissist":   ["mirror reflection dark", "person alone", "isolation"],
    "mind":         ["brain neurons", "thinking abstract", "mind concept dark"],
    "dark":         ["dark atmosphere", "mystery shadow", "night city abstract"],
    "control":      ["control mechanism", "power authority", "chess master"],
    "brain":        ["brain scan", "neural network", "human brain"],
    "social":       ["crowd people", "social interaction", "human behavior"],
    "anxiety":      ["stress person", "anxiety dark", "overwhelmed"],
    "memory":       ["memory concept", "past present", "nostalgia abstract"],
    "fear":         ["fear dark", "horror atmosphere", "scared"],
    "addiction":    ["addiction concept", "compulsion behavior", "loop"],
    "money":        ["finance dark", "money power", "wealth concept"],
    "crime":        ["crime scene dark", "investigation", "detective night"],
    "history":      ["ancient history", "historical concept", "time past"],
    "adhd":         ["focus distraction", "brain activity", "concentration"],
    "trauma":       ["dark emotional", "pain concept", "healing"],
}

DEFAULT_SEARCHES = ["dark abstract background", "moody atmosphere", "cinematic dark"]

# Visuals "no sense" — não têm nada a ver com o conteúdo mas são visualmente viciantes
NONSENSE_SEARCHES = [
    "cute puppy playing grass",
    "baby laughing happy",
    "colorful confetti celebration",
    "pizza cheese melting pull",
    "cat surprised jumping",
    "dolphin jumping ocean",
    "rainbow bright colorful field",
    "cooking burger sizzling grill",
    "sunflower field yellow bright",
    "children playground laughing",
    "colorful paint splashing slow",
    "sports celebration goal win",
    "ice cream colorful summer",
    "dog shaking water funny",
    "butterfly flower close colorful",
]


class VideoCreator:
    def __init__(self, config):
        self.config = config
        self.pexels_key = config.PEXELS_API_KEY
        self.session = requests.Session()
        if self.pexels_key:
            self.session.headers["Authorization"] = self.pexels_key

    def create(self, audio_path: Path, srt_path: Path, topic: str,
               mode: str, output_path: Path) -> Path:
        w, h = (self.config.SHORTS_W, self.config.SHORTS_H) if mode == "shorts" \
               else (self.config.LONGFORM_W, self.config.LONGFORM_H)
        orientation = "portrait" if mode == "shorts" else "landscape"

        duration = self._get_duration(audio_path)
        print(f"   Audio duration: {duration:.1f}s | Resolution: {w}x{h}")

        clips_dir = output_path.parent / "clips"
        clips_dir.mkdir(exist_ok=True)
        clips = self._fetch_footage(topic, duration, orientation, clips_dir)

        if not clips:
            print("   ⚠️  No Pexels footage — creating animated background")
            clips = [self._make_animated_bg(duration, w, h, output_path.parent)]

        raw_video = output_path.parent / "bg_video.mp4"
        self._build_background(clips, raw_video, duration, w, h)
        self._compose(raw_video, audio_path, srt_path, output_path, w, h, mode)

        return output_path

    # ─── FOOTAGE ──────────────────────────────────────────────────────────────

    def _fetch_footage(self, topic, duration, orientation, clips_dir):
        if not self.pexels_key:
            print("   ℹ️  No PEXELS_API_KEY — add it to .env for better visuals")
            return []

        search_terms = self._topic_to_searches(topic)
        clips = []
        needed = int(duration / 4) + 3

        for term in search_terms:
            if len(clips) >= needed:
                break
            try:
                results = self._search_pexels_video(term, orientation, per_page=4)
                for video in results:
                    if len(clips) >= needed:
                        break
                    dest = clips_dir / f"clip_{len(clips):03d}.mp4"
                    url  = self._best_video_url(video)
                    if url and self._download(url, dest):
                        clips.append(dest)
            except Exception as e:
                print(f"   Pexels '{term}': {e}")

        print(f"   ✓ Downloaded {len(clips)} footage clips")
        return clips

    def _search_pexels_video(self, query, orientation, per_page):
        r = self.session.get(
            "https://api.pexels.com/videos/search",
            params={"query": query, "per_page": per_page,
                    "orientation": orientation, "size": "medium"},
            timeout=15
        )
        r.raise_for_status()
        return r.json().get("videos", [])

    def _best_video_url(self, video):
        files = video.get("video_files", [])
        for quality in ["hd", "sd"]:
            for f in files:
                if f.get("quality") == quality:
                    return f["link"]
        return files[0]["link"] if files else ""

    def _download(self, url, dest):
        try:
            r = self.session.get(url, stream=True, timeout=30)
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return dest.stat().st_size > 10_000
        except Exception:
            return False

    def _topic_to_searches(self, topic):
        relevant = []
        topic_lower = topic.lower()
        for keyword, terms in VISUAL_MAP.items():
            if keyword in topic_lower:
                relevant.extend(terms)
        if not relevant:
            relevant = DEFAULT_SEARCHES.copy()

        # 50% conteúdo relevante + 50% "no sense" para prender a atenção
        nonsense = random.sample(NONSENSE_SEARCHES, min(4, len(NONSENSE_SEARCHES)))
        random.shuffle(relevant)
        # Intercala: 1 relevante, 1 no-sense, 1 relevante, 1 no-sense...
        mixed = []
        for i in range(max(len(relevant), len(nonsense))):
            if i < len(relevant):
                mixed.append(relevant[i])
            if i < len(nonsense):
                mixed.append(nonsense[i])
        return mixed

    # ─── ANIMATED BACKGROUND FALLBACK ─────────────────────────────────────────

    def _make_animated_bg(self, duration, w, h, out_dir):
        bg = out_dir / "animated_bg.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x0a0a1a:s={w}x{h}:r=30",
            "-t", str(duration + 2),
            "-vf", "noise=alls=15:allf=t+u",
            "-c:v", "libx264", "-preset", "ultrafast",
            str(bg)
        ]
        subprocess.run(cmd, capture_output=True)
        return bg

    # ─── FFMPEG PIPELINE ──────────────────────────────────────────────────────

    def _build_background(self, clips, out, duration, w, h):
        scaled = []
        temp = out.parent / "scaled"
        temp.mkdir(exist_ok=True)

        for i, clip in enumerate(clips):
            sp = temp / f"s{i:03d}.mp4"
            vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                  f"crop={w}:{h},setsar=1,fps={self.config.FPS}")
            r = subprocess.run(
                ["ffmpeg", "-y", "-i", str(clip),
                 "-vf", vf, "-t", "6",
                 "-c:v", "libx264", "-preset", "ultrafast", "-an", str(sp)],
                capture_output=True
            )
            if r.returncode == 0 and sp.exists() and sp.stat().st_size > 1000:
                scaled.append(sp)

        if not scaled:
            scaled = [self._make_animated_bg(duration, w, h, out.parent)]

        list_file = out.parent / "concat.txt"
        clips_needed = int(duration / 5) + 4
        with open(list_file, "w") as f:
            for i in range(clips_needed):
                c = scaled[i % len(scaled)]
                f.write(f"file '{c.absolute()}'\n")

        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-t", str(duration + 1),
            "-c:v", "libx264", "-preset", "ultrafast",
            str(out)
        ], capture_output=True)

    @staticmethod
    def _speed_srt(srt_path: Path, speed: float) -> Path:
        """Ajusta timestamps do SRT para a nova velocidade."""
        import re

        def scale_time(m):
            total_ms = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 +
                        int(m.group(3))) * 1000 + int(m.group(4))
            t = int(total_ms / speed)
            h, rem = divmod(t, 3_600_000)
            mn, rem = divmod(rem, 60_000)
            s, ms = divmod(rem, 1_000)
            return f"{h:02d}:{mn:02d}:{s:02d},{ms:03d}"

        content = srt_path.read_text(encoding="utf-8", errors="replace")
        adjusted = re.sub(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", scale_time, content)
        out = srt_path.parent / "temp_subtitles_sped.srt"
        out.write_text(adjusted, encoding="utf-8")
        return out

    def _compose(self, bg, audio, srt, out, w, h, mode):
        font_size = self.config.SUBTITLE_SIZE_SHORTS if mode == "shorts" \
                    else self.config.SUBTITLE_SIZE_LONGFORM
        margin_v = 20 if mode == "shorts" else 15
        speed = getattr(self.config, "VIDEO_SPEED", 1.0)

        # ── FIX CRÍTICO: copia SRT para caminho simples sem dois pontos ────────
        simple_srt = Path("temp_subtitles.srt")
        try:
            if speed != 1.0:
                sped = self._speed_srt(srt, speed)
                shutil.copy(str(sped), str(simple_srt))
                try: sped.unlink()
                except: pass
            else:
                shutil.copy(str(srt), str(simple_srt))
            srt_ffmpeg = simple_srt.name
        except Exception:
            srt_ffmpeg = None

        music_files = []
        music_dir = Path(self.config.MUSIC_DIR)
        music_dir.mkdir(exist_ok=True)
        music_files = list(music_dir.glob("*.mp3")) + list(music_dir.glob("*.wav"))

        if not music_files:
            ambient = music_dir / "dark_ambient_loop.wav"
            print("   Generating dark ambient background music...")
            if self._generate_ambient_music(ambient):
                music_files = [ambient]
                print("   ✓ Dark ambient loop generated")

        # Tenta COM legendas primeiro
        if srt_ffmpeg and simple_srt.exists():
            success = self._run_compose(bg, audio, out, music_files, srt_ffmpeg, font_size, margin_v)
            if success:
                try:
                    simple_srt.unlink()
                except Exception:
                    pass
                return

        # Fallback: sem legendas
        print("   ⚠️  Subtitle burn failed — video without subtitles")
        self._run_compose_no_subs(bg, audio, out, music_files)
        try:
            simple_srt.unlink()
        except Exception:
            pass

    def _run_compose(self, bg, audio, out, music_files, srt_path_str, font_size, margin_v):
        """Tenta renderizar com legendas. Retorna True se sucesso."""
        speed = getattr(self.config, "VIDEO_SPEED", 1.0)
        v_speed = f"setpts=PTS/{speed}," if speed != 1.0 else ""
        a_speed = f",atempo={speed}"      if speed != 1.0 else ""

        sub_filter = (
            f"subtitles='{srt_path_str}':force_style='"
            f"FontName=Arial,FontSize={font_size},Bold=1,"
            f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
            f"Outline=2,Shadow=1,Alignment=2,MarginV={margin_v}'"
        )

        if music_files:
            music = random.choice(music_files)
            cmd = [
                "ffmpeg", "-y",
                "-i", str(bg), "-i", str(audio),
                "-stream_loop", "-1", "-i", str(music),
                "-filter_complex",
                (f"[1:a]volume=1.0{a_speed}[voice];"
                 f"[2:a]volume=0.30[bgm];"
                 f"[voice][bgm]amix=inputs=2:duration=first[audio_mix];"
                 f"[0:v]{v_speed}{sub_filter}[v]"),
                "-map", "[v]", "-map", "[audio_mix]",
                "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", str(out)
            ]
        else:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(bg), "-i", str(audio),
                "-filter_complex",
                (f"[1:a]volume=1.0{a_speed}[voice];"
                 f"[0:v]{v_speed}{sub_filter}[v]"),
                "-map", "[v]", "-map", "[voice]",
                "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", str(out)
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ Video composed with subtitles")
            return True

        # Debug: mostra o erro real do FFmpeg
        err = result.stderr[-300:] if result.stderr else "unknown"
        print(f"   ✗ FFmpeg subtitle error: ...{err}")
        return False

    def _run_compose_no_subs(self, bg, audio, out, music_files):
        """Renderiza sem legendas como fallback final."""
        if music_files:
            music = random.choice(music_files)
            cmd = [
                "ffmpeg", "-y",
                "-i", str(bg), "-i", str(audio),
                "-stream_loop", "-1", "-i", str(music),
                "-filter_complex",
                ("[1:a]volume=1.0[voice];"
                 "[2:a]volume=0.30[bgm];"
                 "[voice][bgm]amix=inputs=2:duration=first[audio_mix]"),
                "-map", "0:v", "-map", "[audio_mix]",
                "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac", "-shortest", str(out)
            ]
        else:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(bg), "-i", str(audio),
                "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac", "-shortest", str(out)
            ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ Video composed (no subtitles)")
        else:
            print(f"   ❌ Fatal FFmpeg error: {result.stderr[-200:]}")

    @staticmethod
    def _generate_ambient_music(output_path: Path) -> bool:
        """Gera um loop dark ambient usando numpy. Sem APIs, sem dependências externas."""
        try:
            import numpy as np
            import wave as wave_module

            sr, duration = 44100, 30
            t = np.linspace(0, duration, duration * sr, dtype=np.float64)

            lfo_slow = np.sin(2 * np.pi * 0.10 * t)
            lfo_mid  = np.sin(2 * np.pi * 0.25 * t)
            vibrato  = 1 + 0.004 * lfo_slow

            # Bass layer
            audio  = 0.25 * np.sin(2 * np.pi * 55  * vibrato * t)
            audio += 0.12 * np.sin(2 * np.pi * 110 * t)

            # Mid-range pad (audível em caixas de laptop: 300-700Hz)
            audio += 0.18 * np.sin(2 * np.pi * 330 * t) * (0.5 + 0.5 * lfo_slow)
            audio += 0.14 * np.sin(2 * np.pi * 440 * t) * (0.4 + 0.6 * lfo_mid)
            audio += 0.10 * np.sin(2 * np.pi * 550 * t) * (0.3 + 0.7 * np.sin(2 * np.pi * 0.07 * t))
            audio += 0.07 * np.sin(2 * np.pi * 660 * t) * (0.2 + 0.8 * np.sin(2 * np.pi * 0.04 * t))

            # Textura suave
            noise = np.convolve(np.random.normal(0, 0.008, len(t)), np.ones(120) / 120, mode="same")
            audio += noise

            # Breathing AM
            audio *= 0.78 + 0.22 * np.sin(2 * np.pi * 0.05 * t)

            fade = min(2 * sr, len(audio) // 4)
            audio[:fade]  *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)

            audio = audio / max(np.max(np.abs(audio)), 1e-9) * 0.65

            pcm = (audio * 32767).astype(np.int16)
            stereo = np.column_stack([pcm, pcm])

            with wave_module.open(str(output_path), "w") as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(stereo.tobytes())
            return True
        except Exception as e:
            print(f"   ⚠️  Music generation failed: {e}")
            return False

    @staticmethod
    def _get_duration(path):
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True
        )
        try:
            return float(r.stdout.strip())
        except ValueError:
            return 60.0
