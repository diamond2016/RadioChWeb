Background image

Start with a lightweight SVG background (scales nicely, no extra image files).

Use a low-contrast palette and a semi-opaque overlay so foreground text/cards remain readable.

Provide a Pillow script to produce bitmap WebP/JPG variants later from a source photo/artwork if you want photographic backgrounds.

I give you: an SVG you can drop into static/images, the index/base template CSS patch to use it with a soft overlay, and an optional generator script.

SVG background (light, vintage radio silhouettes, tileable)

Optional: generate photographic/background bitmaps from assets (Pillow)

If you collect multiple photos of vintage radios/antennas you can compose them with a tint/overlay and export WebP variants for performance. Save script as scripts/generate_backgrounds.py and run with a source image.

# ...existing code...
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path

OUT_DIR = Path("static/images")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SIZES = {
    "large": (1920, 1080),
    "medium": (1280, 720),
    "small": (800, 600),
}

def make_variant(src_path, size, out_path, tint=(240,245,250,160)):
    im = Image.open(src_path).convert("RGBA")
    im = im.resize(size, Image.LANCZOS)

    # desaturate slightly and reduce contrast for background subtlety
    enhancer = ImageEnhance.Color(im)
    im = enhancer.enhance(0.3)
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(0.95)

    # add soft gaussian blur
    im = im.filter(ImageFilter.GaussianBlur(radius=6))

    # color tint overlay
    overlay = Image.new("RGBA", im.size, tint)
    combined = Image.alpha_composite(im, overlay)

    combined.save(out_path, format="WEBP", quality=75, method=6)
    print("Saved", out_path)

def main(src):
    for name, dims in SIZES.items():
        out = OUT_DIR / f"bg-{name}.webp"
        make_variant(src, dims, out)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_backgrounds.py path/to/source.jpg")
        sys.exit(1)
    main(sys.argv[1])


    Accessibility / tuning tips

Adjust --bg-overlay alpha up (more opaque) if text contrast is too low; down if too flat.
Use .card background slightly opaque (0.9–0.98) and backdrop-filter blur to separate content from pattern.
Test readability with Lighthouse or axe; ensure contrast of primary text >= 4.5:1.
For performance, serve WebP for large devices and use media queries to swap to smaller images on mobile.