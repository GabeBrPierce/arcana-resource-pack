"""
Builds the server resource pack (resource-pack/build/ArcanaPack.zip).

Fonts: the ritual planet symbols are redrawn as 5-pixel-wide bitmaps, so (with Minecraft's 1px
letter gap) each is exactly as wide as a digit and the Grimoire's circle diagrams line up.
Font definitions merge across packs, so this only adds these eight characters to the default font.

Run: python resource-pack/build_pack.py   (prints the zip's SHA-1 for server.properties)
"""
import hashlib
import json
import os
import shutil
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build")
PACK_FORMAT_MIN = 88   # 26.2
PACK_FORMAT_MAX = 99   # leave room for 26.3+ clients joining through ViaVersion

# 5 columns wide, rows top to bottom; '#' = ink. Row 6 sits on the baseline, row 7 is a descender.
GLYPHS = {
    "☉": [".....",
          ".###.",
          "#...#",
          "#.#.#",
          "#...#",
          ".###.",
          ".....",
          "....."],
    "☽": ["###..",
          "...#.",
          "....#",
          "....#",
          "....#",
          "...#.",
          "###..",
          "....."],
    "☿": ["#...#",
          ".###.",
          "#...#",
          "#...#",
          ".###.",
          "..#..",
          ".###.",
          "..#.."],
    "♀": [".###.",
          "#...#",
          "#...#",
          "#...#",
          ".###.",
          "..#..",
          ".###.",
          "..#.."],
    "♂": ["..###",
          "...##",
          "..#.#",
          ".##..",
          "#..#.",
          "#..#.",
          ".##..",
          "....."],
    "♃": [".#...",
          "#.#..",
          "..#..",
          ".#...",
          "#####",
          "...#.",
          "...#.",
          "....."],
    "♄": [".#...",
          "###..",
          ".#...",
          ".###.",
          ".#..#",
          "....#",
          "...#.",
          "....."],
    "✶": [".....",
          "..#..",
          "#.#.#",
          ".###.",
          "#.#.#",
          "..#..",
          ".....",
          "....."],
}


def build():
    root = os.path.join(OUT, "pack")
    if os.path.isdir(root):
        shutil.rmtree(root)
    tex = os.path.join(root, "assets", "arcana", "textures", "font")
    font = os.path.join(root, "assets", "minecraft", "font")
    os.makedirs(tex)
    os.makedirs(font)

    chars = "".join(GLYPHS)
    img = Image.new("RGBA", (8 * len(chars), 8), (0, 0, 0, 0))
    for i, ch in enumerate(chars):
        rows = GLYPHS[ch]
        assert len(rows) == 8 and all(len(r) == 5 for r in rows), ch
        assert any(r[4] == "#" for r in rows), f"{ch} must touch column 5 to be 6px wide"
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c == "#":
                    img.putpixel((i * 8 + x, y), (255, 255, 255, 255))
    img.save(os.path.join(tex, "planets.png"))

    with open(os.path.join(font, "default.json"), "w", encoding="utf-8") as f:
        json.dump({"providers": [{"type": "bitmap", "file": "arcana:font/planets.png",
                                  "ascent": 7, "height": 8, "chars": [chars]}]}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(root, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump({"pack": {"description": "Arcana: ritual symbols and more",
                            "min_format": PACK_FORMAT_MIN, "max_format": PACK_FORMAT_MAX}}, f, indent=2)

    # Preview at 8x scale for checking the glyphs by eye.
    img.resize((img.width * 8, img.height * 8), Image.NEAREST).save(os.path.join(OUT, "preview.png"))

    zpath = os.path.join(OUT, "ArcanaPack.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(root):
            for name in files:
                full = os.path.join(dirpath, name)
                z.write(full, os.path.relpath(full, root).replace(os.sep, "/"))
    sha1 = hashlib.sha1(open(zpath, "rb").read()).hexdigest()
    print(zpath)
    print("sha1", sha1)
    return zpath, sha1


if __name__ == "__main__":
    build()
