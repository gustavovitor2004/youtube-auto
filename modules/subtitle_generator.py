"""
Subtitle Generator — 100% gratuito
Usa: faster-whisper (Whisper da OpenAI otimizado, roda localmente)
Modelo 'base' — rápido e preciso para inglês
"""

import datetime
from pathlib import Path

try:
    from faster_whisper import WhisperModel
    WHISPER_OK = True
except ImportError:
    WHISPER_OK = False


class SubtitleGenerator:
    def __init__(self, config):
        self.config = config
        self._model = None

    def generate(self, audio_path: Path, output_path: Path, mode: str = "shorts") -> Path:
        if not WHISPER_OK:
            print("   ⚠️  faster-whisper not installed — creating empty subtitles")
            print("   Install: pip install faster-whisper")
            output_path.write_text("")
            return output_path

        model = self._get_model()

        print("   Transcribing audio (this may take a minute)...")
        segments, info = model.transcribe(
            str(audio_path),
            language="en",
            word_timestamps=True,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 300}
        )
        segments = list(segments)  # Materializa o gerador

        # Shorts: 2-3 palavras por legenda (impacto visual)
        # Long-form: 6-8 palavras (mais confortável para leitura)
        words_per_sub = 3 if mode == "shorts" else 7

        srt = self._to_srt(segments, words_per_sub)
        output_path.write_text(srt, encoding="utf-8")

        count = srt.count("\n\n")
        print(f"   ✓ {count} subtitle segments generated")
        return output_path

    # ─── PRIVATE ──────────────────────────────────────────────────────────────

    def _get_model(self):
        """Carrega o modelo uma vez (lazy loading)."""
        if self._model is None:
            print("   Loading Whisper model (base, CPU)...")
            # 'base' = boa qualidade, rápido, ~145MB download na primeira vez
            # Para mais qualidade: 'small' ou 'medium' (mais lento)
            self._model = WhisperModel("base", device="cpu", compute_type="int8")
            print("   ✓ Whisper model loaded")
        return self._model

    def _to_srt(self, segments, words_per_sub: int) -> str:
        lines = []
        idx = 1
        buffer = []
        SENTENCE_END = {'.', '!', '?'}

        for segment in segments:
            if hasattr(segment, "words") and segment.words:
                for word in segment.words:
                    buffer.append(word)
                    word_text = word.word.strip()
                    # Quebra no fim de frase (mínimo 2 palavras) OU no limite
                    is_sentence_end = bool(word_text) and word_text[-1] in SENTENCE_END
                    if len(buffer) >= words_per_sub or (is_sentence_end and len(buffer) >= 2):
                        lines.extend(self._make_entry(idx, buffer))
                        idx += 1
                        buffer = []
            else:
                lines.append(str(idx))
                lines.append(f"{self._fmt(segment.start)} --> {self._fmt(segment.end)}")
                lines.append(segment.text.strip().upper())
                lines.append("")
                idx += 1

        if buffer:
            lines.extend(self._make_entry(idx, buffer))

        return "\n".join(lines)

    def _make_entry(self, idx: int, words: list) -> list:
        start = words[0].start
        end   = words[-1].end
        text  = " ".join(w.word.strip() for w in words).upper()
        return [str(idx), f"{self._fmt(start)} --> {self._fmt(end)}", text, ""]

    @staticmethod
    def _fmt(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
