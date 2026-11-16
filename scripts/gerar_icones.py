"""Gera ícones PWA do UniApp (desenho simples, sem marca de instituição)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "static" / "icons"

NAVY = (18, 32, 143, 255)
NAVY_DARK = (10, 20, 102, 255)
YELLOW = (255, 212, 0, 255)
WHITE = (255, 255, 255, 255)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        path = Path(name)
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def desenhar(size: int, *, maskable: bool = False) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Área segura do maskable (~80% central)
    pad = int(size * 0.1) if maskable else int(size * 0.06)
    box = [pad, pad, size - pad, size - pad]
    radius = int(size * 0.18)
    draw.rounded_rectangle(box, radius=radius, fill=NAVY)
    # Círculo decorativo
    c = int(size * 0.22)
    draw.ellipse([size - pad - c, pad, size - pad, pad + c], fill=(255, 255, 255, 28))
    font = _font(int(size * 0.42))
    text = "U"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) / 2 - bbox[0]
    y = (size - th) / 2 - bbox[1] - size * 0.02
    draw.text((x, y), text, font=font, fill=YELLOW)
    # Barra amarela discreta
    bar_h = max(2, size // 40)
    draw.rectangle(
        [pad + size * 0.18, size - pad - bar_h * 3, size - pad - size * 0.18, size - pad - bar_h * 2],
        fill=YELLOW,
    )
    if not maskable:
        # Sombra interna sutil na borda
        draw.rounded_rectangle(box, radius=radius, outline=NAVY_DARK, width=max(1, size // 64))
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    specs = [
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, False),
        ("maskable-512.png", 512, True),
        ("apple-touch-icon.png", 180, False),
    ]
    for name, size, maskable in specs:
        path = OUT / name
        desenhar(size, maskable=maskable).save(path, format="PNG")
        print("gerado", path)


if __name__ == "__main__":
    main()
