"""Gera logo/foto de perfil do canal MindVault"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

SIZE = 800
OUT  = "output/MindVault_profile.png"
os.makedirs("output", exist_ok=True)

img  = Image.new("RGB", (SIZE, SIZE), "#000000")
draw = ImageDraw.Draw(img)

# ── Fundo gradiente roxo-escuro radial ────────────────────────────────────
for i in range(SIZE // 2, 0, -1):
    t   = i / (SIZE // 2)
    r   = int(8  + (30  - 8)  * (1 - t))
    g   = int(4  + (8   - 4)  * (1 - t))
    b   = int(20 + (60  - 20) * (1 - t))
    draw.ellipse([SIZE//2 - i, SIZE//2 - i, SIZE//2 + i, SIZE//2 + i],
                 fill=(r, g, b))

# ── Circulo externo (borda) ────────────────────────────────────────────────
m = 40
draw.ellipse([m, m, SIZE-m, SIZE-m], outline=(120, 60, 200), width=4)
draw.ellipse([m+6, m+6, SIZE-m-6, SIZE-m-6], outline=(80, 30, 140), width=1)

# ── Cérebro estilizado (duas metades simétricas) ───────────────────────────
cx, cy = SIZE // 2, SIZE // 2 - 30
brain_color  = (180, 100, 255)
brain_color2 = (120, 50, 200)

def brain_half(draw, cx, cy, flip=1):
    pts = []
    for angle in range(0, 181, 5):
        rad = math.radians(angle)
        rx  = 95 + 18 * math.sin(2 * rad)
        ry  = 110 + 12 * math.cos(3 * rad)
        x   = cx + flip * rx * math.cos(rad)
        y   = cy - ry * math.sin(rad)
        pts.append((x, y))
    # Linha de base
    pts.append((cx, cy))
    if len(pts) >= 3:
        draw.polygon(pts, fill=brain_color2, outline=brain_color)

brain_half(draw, cx, cy, flip=1)
brain_half(draw, cx, cy, flip=-1)

# Fissura central
draw.line([(cx, cy - 110), (cx, cy)], fill=(10, 5, 25), width=3)

# Sulcos do cérebro
for flip in [1, -1]:
    for i, (ox, oy, r) in enumerate([
        (35, -60, 22), (55, -30, 18), (30, -5, 20), (60, -80, 16)
    ]):
        ax = cx + flip * ox
        ay = cy + oy
        x0, y0 = min(ax - r, ax + r), ay - r // 2
        x1, y1 = max(ax - r, ax + r), ay + r // 2
        if x1 > x0 and y1 > y0:
            draw.arc([x0, y0, x1, y1], 0, 180, fill=(10, 5, 25), width=2)

# ── Olho no centro (símbolo) ───────────────────────────────────────────────
ey = cy + 10
draw.ellipse([cx-22, ey-10, cx+22, ey+10], fill=(10, 5, 25), outline=brain_color, width=2)
draw.ellipse([cx-8,  ey-8,  cx+8,  ey+8],  fill=(160, 80, 255))
draw.ellipse([cx-3,  ey-3,  cx+3,  ey+3],  fill=(10, 5, 25))

# ── Texto "MindVault" ─────────────────────────────────────────────────────
# Tenta fonte bold, cai para default se nao disponivel
font_size_title = 72
font_size_sub   = 28
try:
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial Bold.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
    ]
    font_title = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_title = ImageFont.truetype(fp, font_size_title)
            font_sub   = ImageFont.truetype(fp, font_size_sub)
            break
    if not font_title:
        font_title = ImageFont.load_default()
        font_sub   = font_title
except Exception:
    font_title = ImageFont.load_default()
    font_sub   = font_title

ty = cy + 130

# Sombra do texto
draw.text((cx+3, ty+3), "MindVault", font=font_title,
          fill=(60, 0, 100), anchor="mm")
# Texto principal
draw.text((cx, ty), "MindVault", font=font_title,
          fill=(220, 180, 255), anchor="mm")

# Subtítulo
draw.text((cx, ty + 52), "DARK PSYCHOLOGY", font=font_sub,
          fill=(120, 60, 180), anchor="mm")

# ── Brilho sutil no topo ───────────────────────────────────────────────────
glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
gd   = ImageDraw.Draw(glow)
gd.ellipse([SIZE//2-120, 30, SIZE//2+120, 200],
           fill=(140, 60, 255, 18))
img = img.convert("RGBA")
img = Image.alpha_composite(img, glow).convert("RGB")

img.save(OUT)
print(f"Logo salvo em: {OUT}")
img.show()
