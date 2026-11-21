#!/usr/bin/env python3
"""LUMINARA — a travel poster for a place that does not exist.

Draws a 1024x1024 poster with PIL only, no network, fully deterministic
(fixed seed, no clock, no randomness outside the seeded generator).

The place: Luminara, a lagoon city where the water glows teal at dusk.
One landmark, the Lantern Spire, rises from the lagoon; stilt houses and
lantern strings frame it; a small boat crosses the glowing water.
Palette: deep indigo sky, violet dusk, rose horizon, teal lagoon,
warm amber lantern light. The name sits big at the top; the eye travels
name -> spire -> sun on the horizon -> glowing lagoon.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   -> writes out/entry.png
In the grader the output dir is /output (MAKEFUN_OUTPUT_DIR unset).
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1024
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

IVORY = (250, 244, 230)
INK_INDIGO = (24, 28, 58)
VIOLET = (74, 52, 110)
ROSE = (214, 120, 110)
AMBER = (255, 178, 77)
AMBER_DEEP = (255, 150, 48)
TEAL = (46, 196, 182)
TEAL_DARK = (18, 84, 96)
TEAL_DEEP = (10, 48, 66)

rng = random.Random(7)


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def vgrad(w, h, stops):
    """Vertical gradient through (position 0..1, rgb) stops."""
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[0, y] = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
                break
        else:
            px[0, y] = stops[-1][1]
    return img.resize((w, h))


def glow(img, cx, cy, r, color, blur, alpha=255):
    """Soft radial glow: blurred disc on an overlay, composited in."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def draw_text_spaced(d, cx, y, text, fnt, fill, tracking):
    """Draw text centred on cx, with extra tracking between letters."""
    widths = [d.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, wch in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += wch + tracking
    return total


def house(d, x, y_base, w, h, lit_windows):
    """A dark stilt house with amber windows; y_base is the waterline."""
    body_top = y_base - h
    # stilts
    for sx in (x + 6, x + w - 8):
        d.line([sx, y_base, sx, y_base + 26], fill=(16, 20, 44), width=3)
    # body + roof
    d.rectangle([x, body_top, x + w, y_base], fill=(20, 24, 52))
    d.polygon([(x - 5, body_top), (x + w / 2, body_top - 16),
               (x + w + 5, body_top)], fill=(14, 17, 40))
    # windows
    for wx, wy in lit_windows:
        d.rectangle([x + wx, body_top + wy, x + wx + 8, body_top + wy + 10],
                    fill=AMBER)


def main():
    img = Image.new("RGBA", (W, H))
    # --- sky: indigo -> violet -> rose down to the horizon (y=640) ---
    sky = vgrad(W, 660, [(0.0, (26, 30, 62)), (0.45, (58, 44, 96)),
                         (0.78, (110, 66, 112)), (1.0, (214, 120, 110))])
    img.paste(sky, (0, 0))
    d = ImageDraw.Draw(img)

    # --- stars, upper sky only ---
    for _ in range(130):
        x = rng.randint(20, W - 20)
        y = rng.randint(24, 380)
        r = rng.choice([1, 1, 1, 2])
        a = rng.randint(90, 210)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 235, a))

    # a few birds
    for bx, by, s in ((180, 210, 9), (215, 190, 7), (830, 250, 8)):
        d.arc([bx - s, by - s, bx, by + s], 200, 340, fill=(30, 32, 66), width=2)
        d.arc([bx, by - s, bx + s, by + s], 200, 340, fill=(30, 32, 66), width=2)

    # --- low sun, just above the horizon, behind the spire ---
    glow(img, 512, 598, 150, (255, 170, 90), 60, 170)
    glow(img, 512, 598, 90, (255, 200, 120), 30, 220)
    d = ImageDraw.Draw(img)
    d.ellipse([512 - 62, 598 - 62, 512 + 62, 598 + 62], fill=(255, 196, 110))

    # --- distant headlands framing the lagoon ---
    d.polygon([(0, 640), (0, 560), (70, 585), (150, 560), (230, 600),
               (300, 640)], fill=(34, 34, 72))
    d.polygon([(1024, 640), (1024, 570), (950, 590), (880, 565), (800, 605),
               (740, 640)], fill=(34, 34, 72))

    # --- lagoon: teal, darker toward the bottom ---
    lagoon = vgrad(W, H - 640, [(0.0, (30, 122, 128)), (0.5, (18, 84, 96)),
                                (1.0, (10, 48, 66))])
    img.paste(lagoon, (0, 640))
    d = ImageDraw.Draw(img)

    # sun reflection: shimmering amber dashes under the sun
    for _ in range(90):
        x = 512 + rng.randint(-70, 70)
        y = rng.randint(648, 990)
        w = rng.randint(14, 60) * (1 - (y - 648) / 700.0)
        a = rng.randint(40, 150)
        d.line([x - w / 2, y, x + w / 2, y], fill=(255, 180, 100, a), width=2)

    # teal shimmer strokes across the lagoon
    for _ in range(70):
        x = rng.randint(30, W - 30)
        y = rng.randint(660, 1000)
        w = rng.randint(20, 90)
        a = rng.randint(25, 70)
        d.line([x, y, x + w, y], fill=(90, 220, 205, a), width=2)

    # --- Lantern Spire: the one landmark, centre ---
    # glow behind the beacon
    glow(img, 512, 268, 70, (255, 180, 90), 34, 200)
    d = ImageDraw.Draw(img)
    # tower body: tapered, dark indigo silhouette
    d.polygon([(512 - 30, 640), (512 - 17, 300), (512 + 17, 300),
               (512 + 30, 640)], fill=(22, 24, 54))
    # glowing rings
    for ry, rw in ((380, 24), (470, 27), (560, 30)):
        d.rectangle([512 - rw, ry - 4, 512 + rw, ry + 4], fill=AMBER)
    # windows: two columns of small amber lights
    for wy in range(320, 620, 34):
        for wx in (-9, 3):
            d.rectangle([512 + wx, wy, 512 + wx + 6, wy + 9], fill=AMBER)
    # beacon orb on top
    d.ellipse([512 - 16, 252, 512 + 16, 284], fill=AMBER_DEEP)
    d.ellipse([512 - 10, 258, 512 + 10, 278], fill=(255, 220, 140))

    # --- stilt-house clusters at the waterline, left and right ---
    house(d, 70, 648, 74, 52, [(10, 14), (34, 14), (52, 30)])
    house(d, 160, 650, 58, 40, [(10, 12), (32, 12)])
    house(d, 232, 646, 66, 46, [(12, 12), (36, 26)])
    house(d, 726, 646, 66, 46, [(12, 12), (36, 26)])
    house(d, 806, 650, 58, 40, [(10, 12), (32, 12)])
    house(d, 880, 648, 74, 52, [(10, 14), (34, 14), (52, 30)])

    # --- lantern strings from the spire to the houses ---
    def lantern_string(x0, y0, x1, y1, n):
        pts = []
        for i in range(0, n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t + 46 * 4 * t * (1 - t)  # sag
            pts.append((x, y))
        d.line(pts, fill=(24, 26, 52), width=2)  # the wire
        for (x, y) in pts[1:-1]:
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=AMBER)
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 225, 150))

    lantern_string(495, 330, 150, 620, 9)
    lantern_string(529, 330, 874, 620, 9)
    lantern_string(488, 470, 260, 640, 7)
    lantern_string(536, 470, 764, 640, 7)

    # --- small boat with a lantern, lower lagoon ---
    bx, by = 380, 880
    d.polygon([(bx - 52, by), (bx + 52, by), (bx + 34, by + 16),
               (bx - 34, by + 16)], fill=(14, 17, 40))
    d.line([bx + 8, by - 34, bx + 8, by], fill=(14, 17, 40), width=3)
    d.ellipse([bx - 2, by - 44, bx + 18, by - 24], fill=AMBER)
    d.ellipse([bx + 3, by - 39, bx + 13, by - 29], fill=(255, 225, 150))
    # boat reflection
    for i in range(5):
        yy = by + 24 + i * 9
        w = 44 - i * 7
        d.line([bx - w, yy, bx + w, yy], fill=(255, 180, 100, 90 - i * 14),
               width=2)

    # --- the name: big, ivory, letterspaced, top centre ---
    title_font = font(SERIF_B, 118)
    # soft shadow for legibility against the sky
    d2 = ImageDraw.Draw(img)
    draw_text_spaced(d2, 514, 78, "LUMINARA", title_font, (16, 18, 44), 26)
    draw_text_spaced(d, 512, 74, "LUMINARA", title_font, IVORY, 26)
    # thin rules flanking a small diamond under the name
    d.line([212, 216, 452, 216], fill=IVORY, width=2)
    d.line([572, 216, 812, 216], fill=IVORY, width=2)
    d.polygon([(512, 206), (522, 216), (512, 226), (502, 216)], fill=AMBER)

    # --- thin ivory frame ---
    d.rectangle([22, 22, W - 23, H - 23], outline=IVORY, width=3)

    img = img.convert("RGB")
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
