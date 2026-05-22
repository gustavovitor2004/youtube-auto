"""
Thumbnail Creator — 100% gratuito
Usa: Pillow (Python Imaging Library)
Cria thumbnails profissionais com texto, gradiente e elementos visuais
"""

import random
from pathlib import Path
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False


# Paletas de cores por estilo
PALETTES = {
    "dark_red":    {"bg": (8, 8, 20),   "accent": (200, 20, 20),   "text": (255, 255, 255), "highlight": (255, 50, 50)},
    "dark_blue":   {"bg": (5, 10, 30),  "accent": (30, 80, 200),   "text": (255, 255, 255), "highlight": (80, 160, 255)},
    "dark_purple": {"bg": (15, 5, 30),  "accent": (120, 20, 180),  "text": (255, 255, 255), "highlight": (200, 100, 255)},
    "dark_gold":   {"bg": (10, 8, 5),   "accent": (180, 130, 10),  "text": (255, 255, 255), "highlight": (255, 200, 50)},
}

POWER_WORDS = [
    "DARK SECRET", "HIDDEN TRUTH", "NEVER TOLD", "SHOCKING",
    "EXPOSED", "THEY HIDE THIS", "WARNING", "DISTURBING",
]

# Caminhos comuns de fontes por OS
FONT_PATHS = [
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    # macOS
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    # Windows
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/Arial.ttf",
    "C:/Windows/Fonts/impact.ttf",
]


class ThumbnailCreator:
    def __init__(self, config):
        self.config = config
        self.pexels_key = config.PEXELS_API_KEY
        self.session = requests.Session() if REQUESTS_OK else None
        if self.session and self.pexels_key:
            self.session.headers["Authorization"] = self.pexels_key

    # ─── PUBLIC ───────────────────────────────────────────────────────────────

    def create(self, title: str, topic: str, output_path: Path) -> Path:
        if not PIL_OK:
            print("   ⚠️  Pillow not installed: pip install Pillow")
            output_path.write_bytes(b"")
            return output_path

        W, H = 1280, 720
        palette = random.choice(list(PALETTES.values()))

        # 1) Base image (Pexels ou gradiente gerado)
        img = self._get_base(topic, W, H, palette)

        # 2) Overlay gradiente escuro
        img = self._add_overlay(img, W, H, palette)

        # 3) Texto principal
        img = self._add_title(img, title, W, H, palette)

        # 4) Badge de poder ("DARK SECRET" etc.)
        img = self._add_badge(img, palette)

        # 5) Barra lateral de acento
        img = self._add_side_bar(img, H, palette)

        img.save(str(output_path), "JPEG", quality=95, optimize=True)
        print(f"   ✓ Thumbnail created: {output_path.name}")
        return output_path

    # ─── BASE IMAGE ───────────────────────────────────────────────────────────

    def _get_base(self, topic: str, W: int, H: int, palette: dict) -> "Image":
        # Tenta buscar do Pexels
        if self.pexels_key and self.session:
            try:
                img = self._pexels_image(topic, W, H)
                if img:
                    return img
            except Exception:
                pass

        # Fallback: gradiente programático
        return self._gradient_base(W, H, palette)

    def _pexels_image(self, topic: str, W: int, H: int):
        words = topic.split()[:3]
        query = " ".join(words) + " dark dramatic"
        r = self.session.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            timeout=10
        )
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if not photos:
            return None

        photo = random.choice(photos[:3])
        img_url = photo["src"]["large2x"]
        img_r = self.session.get(img_url, timeout=15)
        img_r.raise_for_status()

        img = Image.open(BytesIO(img_r.content)).convert("RGB")
        img = img.resize((W, H), Image.LANCZOS)
        # Escurece para o texto ficar legível
        return ImageEnhance.Brightness(img).enhance(0.35)

    def _gradient_base(self, W: int, H: int, palette: dict) -> "Image":
        img = Image.new("RGB", (W, H), palette["bg"])
        draw = ImageDraw.Draw(img)
        bg = palette["bg"]
        acc = palette["accent"]

        # Gradiente radial simulado (cantos escuros, centro levemente mais claro)
        for y in range(H):
            for step in range(0, W, 4):
                cx = abs(step - W // 2) / (W // 2)
                cy = abs(y - H // 2) / (H // 2)
                dist = min((cx * cx + cy * cy) ** 0.5, 1.0)
                r = int(bg[0] + (acc[0] - bg[0]) * (1 - dist) * 0.2)
                g = int(bg[1] + (acc[1] - bg[1]) * (1 - dist) * 0.2)
                b = int(bg[2] + (acc[2] - bg[2]) * (1 - dist) * 0.2)
                draw.line([(step, y), (min(step + 4, W), y)], fill=(r, g, b))

        return img.filter(ImageFilter.GaussianBlur(radius=2))

    # ─── OVERLAYS ─────────────────────────────────────────────────────────────

    def _add_overlay(self, img: "Image", W: int, H: int, palette: dict) -> "Image":
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        bg = palette["bg"]

        # Gradiente de baixo para cima (escurece a parte de baixo para o texto)
        for y in range(H):
            alpha = int(220 * (y / H) ** 1.5)
            draw.line([(0, y), (W, y)], fill=(*bg, alpha))

        base = img.convert("RGBA")
        return Image.alpha_composite(base, overlay).convert("RGB")

    def _add_title(self, img: "Image", title: str, W: int, H: int, palette: dict) -> "Image":
        draw = ImageDraw.Draw(img)

        # Quebra o título em linhas
        title_upper = title.upper()
        lines = self._wrap_text(draw, title_upper, W - 80, 70)
        font_size = 70 if len(lines) <= 2 else 58
        font   = self._font(font_size)
        font_s = self._font(font_size - 10)

        line_h = font_size + 12
        total_h = len(lines) * line_h
        start_y = H - total_h - 55

        for i, line in enumerate(lines):
            y = start_y + i * line_h
            f = font if i == 0 else font_s
            bbox = draw.textbbox((0, 0), line, font=f)
            x = (W - (bbox[2] - bbox[0])) // 2

            # Sombra
            for dx, dy in [(-3, 3), (3, 3), (-3, -3), (3, -3), (0, 4)]:
                draw.text((x + dx, y + dy), line, font=f, fill=(0, 0, 0))

            # Texto: primeira linha em destaque, resto branco
            color = palette["highlight"] if i == 0 else palette["text"]
            draw.text((x, y), line, font=f, fill=color)

        return img

    def _add_badge(self, img: "Image", palette: dict) -> "Image":
        draw = ImageDraw.Draw(img)
        word = random.choice(POWER_WORDS)
        font = self._font(26)
        bbox = draw.textbbox((0, 0), word, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        pad_x, pad_y = 16, 8
        bx1, by1 = 30, 30
        bx2, by2 = bx1 + tw + pad_x * 2, by1 + th + pad_y * 2

        draw.rectangle([bx1, by1, bx2, by2], fill=palette["accent"])
        draw.text((bx1 + pad_x, by1 + pad_y), word, font=font, fill=(255, 255, 255))
        return img

    def _add_side_bar(self, img: "Image", H: int, palette: dict) -> "Image":
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (7, H)], fill=palette["accent"])
        return img

    # ─── HELPERS ──────────────────────────────────────────────────────────────

    def _wrap_text(self, draw: "ImageDraw", text: str, max_w: int, size: int) -> list[str]:
        font = self._font(size)
        words = text.split()
        lines, current = [], []

        for word in words:
            test = " ".join(current + [word])
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_w:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))

        return lines[:3]  # Máx 3 linhas

    def _font(self, size: int) -> "ImageFont":
        for path in FONT_PATHS:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()
