#!/usr/bin/env python3
"""Scans images/ and writes photos.json and photos.js. Every sub-folder becomes a gallery section.
Usage:  python3 build_gallery.py
Optional: pip install pillow  -> also makes small thumbnails (faster gallery)."""
import json, re
from pathlib import Path

ROOT = Path(__file__).parent
IMAGES, THUMBS = ROOT / "images", ROOT / "thumbs"
EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None

def natural(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", str(p))]

photos = []
for f in sorted((p for p in IMAGES.rglob("*") if p.suffix.lower() in EXT), key=natural):
    parts = f.relative_to(IMAGES).parts
    item = {"folder": parts[0] if len(parts) > 1 else "", "src": f.relative_to(ROOT).as_posix()}
    if Image and f.suffix.lower() != ".gif":
        t = THUMBS / f.relative_to(IMAGES).with_suffix(".jpg")
        if not t.exists() or t.stat().st_mtime < f.stat().st_mtime:
            t.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(f) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((700, 700))
                im.save(t, "JPEG", quality=82)
        item["thumb"] = t.relative_to(ROOT).as_posix()
    photos.append(item)

(ROOT / "photos.json").write_text(json.dumps({"photos": photos}, indent=1, ensure_ascii=False), encoding="utf-8")
# photos.js lets the site work when opened straight from disk (file://), where fetch() is blocked
(ROOT / "photos.js").write_text("window.GALLERY_PHOTOS = " + json.dumps(photos, indent=1, ensure_ascii=False) + ";\n", encoding="utf-8")
print(f"{len(photos)} photos in {len({p['folder'] for p in photos if p['folder']})} folders -> photos.json + photos.js")
