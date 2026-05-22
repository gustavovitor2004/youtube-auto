"""
Voice Generator — 100% gratuito
Usa: edge-tts (vozes Microsoft Neural, sem custo)
Fallback de duração: mutagen → estimativa por palavras (não precisa de ffprobe)
"""

import asyncio
import subprocess
from pathlib import Path

try:
    import edge_tts
    EDGE_TTS_OK = True
except ImportError:
    EDGE_TTS_OK = False

try:
    from gtts import gTTS
    GTTS_OK = True
except ImportError:
    GTTS_OK = False


class VoiceGenerator:
    def __init__(self, config):
        self.config = config

    async def generate(self, script: str, output_path: Path, mode: str = "shorts") -> Path:
        voice = self.config.VOICE_SHORTS if mode == "shorts" else self.config.VOICE_LONGFORM

        if EDGE_TTS_OK:
            try:
                await self._generate_edge_tts(script, output_path, voice)
                print(f"   ✓ Voice generated with edge-tts ({voice})")
                return output_path
            except Exception as e:
                print(f"   ✗ edge-tts failed: {e}")

        if GTTS_OK:
            try:
                self._generate_gtts(script, output_path)
                print("   ✓ Voice generated with gTTS (fallback)")
                return output_path
            except Exception as e:
                print(f"   ✗ gTTS failed: {e}")

        raise RuntimeError(
            "No TTS available.\n"
            "Run: pip install edge-tts\n"
            "Then test: edge-tts --text 'Hello' --voice en-US-GuyNeural --write-media test.mp3"
        )

    async def _generate_edge_tts(self, script: str, output_path: Path, voice: str):
        communicate = edge_tts.Communicate(
            text=script,
            voice=voice,
            rate=self.config.VOICE_RATE,
            volume=self.config.VOICE_VOLUME,
        )
        await communicate.save(str(output_path))

    def _generate_gtts(self, script: str, output_path: Path):
        tts = gTTS(text=script, lang="en", slow=False)
        tts.save(str(output_path))

    def get_duration(self, audio_path: Path) -> float:
        """
        Tenta obter duração em segundos por múltiplos métodos:
        1. ffprobe (precisa do FFmpeg instalado)
        2. mutagen (pip install mutagen)
        3. Estimativa por tamanho do arquivo MP3 (128kbps = 16KB/s)
        """
        # Método 1: ffprobe
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(audio_path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass

        # Método 2: mutagen (puro Python, não precisa do FFmpeg)
        try:
            from mutagen.mp3 import MP3
            audio = MP3(str(audio_path))
            duration = audio.info.length
            print(f"   ℹ️  Duration via mutagen: {duration:.1f}s")
            return duration
        except ImportError:
            pass
        except Exception:
            pass

        # Método 3: Estimativa por tamanho do arquivo
        # MP3 128kbps ≈ 16 KB/s
        try:
            size_bytes = audio_path.stat().st_size
            duration = size_bytes / 16_000
            print(f"   ℹ️  Duration estimated from file size: {duration:.1f}s")
            return max(10.0, duration)
        except Exception:
            pass

        # Último fallback: 60 segundos
        print("   ⚠️  Could not determine duration, assuming 60s")
        return 60.0

    @staticmethod
    async def list_voices():
        if not EDGE_TTS_OK:
            print("edge-tts não instalado: pip install edge-tts")
            return
        voices = await edge_tts.list_voices()
        en_voices = [v for v in voices if v["Locale"].startswith("en-")]
        for v in en_voices:
            print(f"  {v['ShortName']:40} {v['Gender']}")
