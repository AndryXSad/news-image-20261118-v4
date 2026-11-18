#!/usr/bin/env python3
"""The Daily Globe — Wednesday 18 November 2026 (v4).

A 1024x1024 newspaper front page for make.fun news-image-20261118:
33 stories from six continents, a real Natural Earth world map keyed
to the day's eight biggest stories, a hand-drawn scene of the Kerch
bridge attack, and three illustrated secondary stories.

v4 fixes the v3 rejection: the grader mounts the repo READ-ONLY at
/bot and runs `python3 -P -s /bot/main.py` with MAKEFUN_OUTPUT_DIR
pointing at an empty writable directory. v3 saved entry.png into the
repo directory first and crashed with PermissionError. v4 writes ONLY
to $MAKEFUN_OUTPUT_DIR when it is set, and only falls back to the
script's own directory for a plain local run.

Run:  python3 main.py
      MAKEFUN_OUTPUT_DIR=out python3 main.py

Python 3, Pillow only, no network, fully deterministic.
"""

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
EDGE = 30
SPAN = PAGE - 2 * EDGE

# ---------------------------------------------------------------- palette
NEWS = (247, 242, 231)      # warm newsprint
BLACK = (24, 21, 16)
BODY = (56, 52, 44)
GREY = (112, 106, 94)
SCARLET = (178, 30, 42)
NAVY = (30, 58, 96)
SEA = (214, 229, 236)
SHORE = (234, 221, 193)
SHORE_LN = (196, 178, 138)
GILT = (212, 156, 44)
TEAL = (15, 108, 102)
DARK = (16, 32, 58)
DARKER = (11, 22, 42)

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype"
SERIF_BOLD = FONT_DIR + "/liberation/LiberationSerif-Bold.ttf"
SERIF_PLAIN = FONT_DIR + "/liberation/LiberationSerif-Regular.ttf"
SERIF_ITALIC = FONT_DIR + "/liberation/LiberationSerif-Italic.ttf"
SANS_BOLD = FONT_DIR + "/dejavu/DejaVuSans-Bold.ttf"
SANS_PLAIN = FONT_DIR + "/dejavu/DejaVuSans.ttf"

_cache = {}


def font(path, size):
    """Load (and cache) a truetype font."""
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def fit(draw, text, fnt, width):
    """Greedy word wrap returning lines that fit `width`."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def block(draw, x, y, text, fnt, width, fill=BLACK, gap=3, limit=None):
    """Draw a wrapped paragraph; return y just below its last line."""
    lines = fit(draw, text, fnt, width)
    if limit is not None:
        lines = lines[:limit]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


def rule(draw, y, weight=1, color=BLACK):
    draw.line([(EDGE, y), (PAGE - EDGE, y)], fill=color, width=weight)


def double_rule(draw, y):
    rule(draw, y, 2)
    rule(draw, y + 4, 1)
    return y + 8


def dot(draw, cx, cy, r, fill):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

# ---------------------------------------------------------------- the day's stories (18 November 2026)
LEAD = {
    "kick": "UKRAINE WAR  —  1",
    "head": "Ukraine destroys a span of Putin's Crimea bridge",
    "deck": ("Kyiv calls the overnight attack 'unprecedented'; Moscow "
             "answers by pounding bridges in the capital."),
    "byline": "From our correspondents in Kyiv and Moscow",
}

SECONDARIES = [
    {
        "kick": "MANILA  —  3",
        "head": "Trump lands in Manila for Quad talks ahead of China visit",
        "stand": "Quad leaders open the Manila summit before APEC.",
        "art": "quad",
    },
    {
        "kick": "SHENZHEN  —  4",
        "head": "APEC opens in Shenzhen; first Trump–Xi–Putin summit tomorrow",
        "stand": "Three leaders meet on APEC's sidelines.",
        "art": "apec",
    },
    {
        "kick": "WALL STREET",
        "head": "Nvidia revenue doubles to $115.8bn; board won't bring back Huang",
        "stand": "Trump backs calls to bring Huang back.",
        "art": "nvda",
    },
]

# (map number or None, section, headline) — 18 more stories
GRID = [
    (2, "EUROPE", "Russia hits Kyiv bridges in reply; UN counts 372 dead in October"),
    (5, "MIDDLE EAST", "Iran drones hit a US radar site in Bahrain; Kuwait reports attacks"),
    (6, "ASIA", "US presses UN aviation body over Taiwan curbs; China hits back"),
    (7, "ASIA", "North Korea fires a ballistic missile into the Sea of Japan"),
    (8, "ASIA", "Modi presses Indo-Pacific vision at East Asia Summit; e-visas open"),
    (None, "ASIA", "Cyclone Akvan bears down on Andhra Pradesh; landfall due 20 Nov"),
    (None, "SPORT", "Dhoni bids farewell to the IPL"),
    (None, "MARKETS", "Dow plunges 1,000 points as Wall Street reels"),
    (None, "BUSINESS", "Anthropic prices its long-awaited IPO"),
    (None, "EUROPE", "Britain sanctions eight firms over illegal West Bank settlements"),
    (None, "EUROPE", "UK pledges £240m for Ukraine's air defences"),
    (None, "EUROPE", "Estonia to shut its border with Russia from December"),
    (None, "EUROPE", "Hundreds of thousands march in Prague for media freedom"),
    (None, "AFRICA", "Rival DR Congo peace efforts fail as eastern violence flares"),
    (None, "MIDDLE EAST", "Gaza ceasefire 'faces imminent collapse', Board of Peace warns"),
    (None, "MIDDLE EAST", "Israel's parliament elects Matan Kahana as speaker"),
    (None, "AMERICAS", "Pakistani man jailed 27½ years in the US over a plot to kill Trump"),
    (None, "ASIA", "Xi meets Carney as Canada and China extend trade deals"),
]

TICKER = [
    "Latvia approves new Kulbergs cabinet",
    "Germany warns of hybrid, cyber threats",
    "Strikes halt Spain; walkouts hit France",
    "Ecuador fishermen sue Trump over drone strike",
    "EU agrees €45bn loan for Ukraine",
    "Cape Town baboon move sparks protests",
    "Deutsche Bank ignored client warnings",
    "Trump gets until 22 Jan in $10bn BBC suit",
    "NZ takes blame for Penrhyn port blowout",
    "One Nation vows 90% refugee-intake cut",
    "Voyager 1 reaches one light-day from Earth",
]

# (number, longitude, latitude, badge offset x, badge offset y)
PINS = [
    (1, 35.4, 45.3, 22, 16),     # Crimea bridge
    (2, 30.5, 50.45, -30, -22),  # Kyiv
    (3, 121.0, 14.6, 12, 24),    # Manila
    (4, 114.1, 22.5, -26, -8),   # Shenzhen
    (5, 50.6, 26.2, 0, 22),      # Bahrain
    (6, 121.6, 25.0, 24, -16),   # Taipei
    (7, 125.75, 39.0, 14, -24),  # Pyongyang
    (8, 77.2, 28.6, -8, -24),    # New Delhi
]

PIN_KEY = ("1 Crimea bridge  ·  2 Kyiv  ·  3 Manila  ·  4 Shenzhen  ·  "
           "5 Bahrain  ·  6 Taipei  ·  7 Pyongyang  ·  8 New Delhi")

# ---------------------------------------------------------------- masthead
def masthead(draw):
    draw.text((PAGE // 2, 14), "THE DAILY GLOBE", font=font(SERIF_BOLD, 58),
              fill=BLACK, anchor="ma")
    draw.line([(EDGE, 88), (PAGE - EDGE, 88)], fill=SCARLET, width=2)
    y = 96
    draw.text((EDGE, y), "WEDNESDAY 18 NOVEMBER 2026",
              font=font(SANS_BOLD, 15), fill=SCARLET)
    draw.text((PAGE // 2, y), "33 STORIES  ·  6 CONTINENTS  ·  ONE DAY",
              font=font(SANS_PLAIN, 12), fill=BODY, anchor="ma")
    draw.text((PAGE - EDGE, y), "WORLD EDITION", font=font(SANS_BOLD, 15),
              fill=BLACK, anchor="ra")
    return double_rule(draw, 118)


# ---------------------------------------------------------------- world map
def world_map(img, top, height):
    """Real Natural Earth land on an equirectangular grid, clipped to frame."""
    draw = ImageDraw.Draw(img)
    x0, x1 = EDGE, PAGE - EDGE
    bottom = top + height
    mw, mh = x1 - x0, height
    lat_hi, lat_lo = 82.0, -58.0

    layer = Image.new("RGB", (mw, mh), SEA)
    ld = ImageDraw.Draw(layer)

    def project(lon, lat):
        px = (lon + 180.0) / 360.0 * mw
        py = (lat_hi - lat) / (lat_hi - lat_lo) * mh
        return px, py

    # graticule
    for lon in range(-150, 181, 30):
        gx, _ = project(lon, 0)
        ld.line([(gx, 0), (gx, mh)], fill=(196, 211, 219), width=1)
    for lat in range(-30, 91, 30):
        _, gy = project(0, lat)
        ld.line([(0, gy), (mw, gy)], fill=(196, 211, 219), width=1)

    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "data", "land.json")) as fh:
        geo = json.load(fh)

    def draw_ring(ring, fill, outline):
        pts = []
        prev_lon = None
        for lon, lat in ring:
            if prev_lon is not None and abs(lon - prev_lon) > 180:
                if len(pts) >= 3:
                    ld.polygon(pts, fill=fill, outline=outline)
                pts = []
            pts.append(project(lon, lat))
            prev_lon = lon
        if len(pts) >= 3:
            ld.polygon(pts, fill=fill, outline=outline)

    for ring in geo["land"]:
        draw_ring(ring, SHORE, SHORE_LN)
    for ring in geo["holes"]:  # lakes and inland seas stay ocean-coloured
        draw_ring(ring, SEA, SHORE_LN)

    # continent names
    lab = font(SANS_BOLD, 10)
    for name, lon, lat in [("NORTH AMERICA", -100, 56),
                           ("SOUTH AMERICA", -60, -14),
                           ("EUROPE", 4, 52), ("AFRICA", 18, 6),
                           ("ASIA", 92, 56), ("AUSTRALIA", 134, -25)]:
        px, py = project(lon, lat)
        ld.text((px, py), name, font=lab, fill=(118, 106, 82), anchor="ma")
    # ocean names, slanted feel via italic serif
    ocn = font(SERIF_ITALIC, 12)
    for name, lon, lat in [("PACIFIC", -150, 2), ("PACIFIC", 158, -38),
                           ("ATLANTIC", -32, 22), ("INDIAN", 82, -32)]:
        px, py = project(lon, lat)
        ld.text((px, py), name, font=ocn, fill=(94, 118, 138), anchor="ma")

    # numbered story pins with leader lines fanning the badge away
    num_font = font(SANS_BOLD, 11)
    for num, lon, lat, dx, dy in PINS:
        px, py = project(lon, lat)
        bx, by = px + dx, py + dy
        dot(ld, px, py, 3, SCARLET)
        if dx or dy:
            ld.line([(px, py), (bx, by)], fill=SCARLET, width=1)
        ld.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=SCARLET,
                   outline=(255, 255, 255), width=2)
        ld.text((bx, by - 1), str(num), font=num_font,
                fill=(255, 255, 255), anchor="mm")

    img.paste(layer, (x0, top))
    draw.rectangle([x0, top, x1, bottom], outline=BLACK, width=2)
    draw.text((EDGE, bottom + 7),
              "THE WORLD AT A GLANCE — the numbered places are the day's biggest stories.",
              font=font(SANS_PLAIN, 11), fill=GREY)
    draw.text((EDGE, bottom + 24), PIN_KEY,
              font=font(SANS_BOLD, 10), fill=BODY)
    return bottom + 42

# ---------------------------------------------------------------- Kerch bridge scene
def kerch_scene(draw, x0, y0, w, h):
    """Night over the strait: a suspension bridge with its middle span gone."""
    x1, y1 = x0 + w, y0 + h
    # sky: deep blue bands, darkest at the top
    sky = [(30, 54, 92), (24, 46, 80), (19, 38, 68), (15, 31, 56)]
    band_h = (h - 50) // len(sky)
    for i, colour in enumerate(sky):
        draw.rectangle([x0, y0 + i * band_h, x1, y0 + (i + 1) * band_h],
                       fill=colour)
    # stars: deterministic scatter, kept out of the caption strip
    for i in range(30):
        fx = (math.sin(i * 12.9898) * 43758.5453) % 1.0
        fy = (math.sin(i * 78.233) * 12543.1234) % 1.0
        sx = x0 + 10 + int(fx * (w - 20))
        sy = y0 + 30 + int(fy * 30)
        r = 2 if i % 4 == 0 else 1
        dot(draw, sx, sy, r, (222, 230, 242))
    # crescent moon, upper right
    draw.ellipse([x1 - 54, y0 + 10, x1 - 22, y0 + 42], fill=(236, 230, 198))
    draw.ellipse([x1 - 46, y0 + 8, x1 - 20, y0 + 36], fill=(24, 46, 80))
    draw.ellipse([x1 - 50, y0 + 14, x1 - 26, y0 + 38], fill=(246, 242, 216))

    sea_y = y0 + h - 50
    draw.rectangle([x0, sea_y, x1, y1], fill=DARKER)
    # moonlight ripples on the water
    for i in range(10):
        fx = (math.sin(i * 39.346) * 24634.6345) % 1.0
        wx = x0 + 12 + int(fx * (w - 70))
        wy = sea_y + 7 + i * 4
        draw.line([(wx, wy), (wx + 24, wy)], fill=(72, 102, 142), width=1)

    mid = x0 + w // 2
    deck_y = sea_y - 12

    def cable(p0, p1, sag):
        pts = []
        for t in range(21):
            tt = t / 20.0
            bx = p0[0] + (p1[0] - p0[0]) * tt
            by = p0[1] + (p1[1] - p0[1]) * tt + sag * 4 * tt * (1 - tt)
            pts.append((bx, by))
        draw.line(pts, fill=(192, 198, 206), width=2)

    # towers with cross-bracing
    for tx in (x0 + 56, x1 - 64):
        draw.rectangle([tx, y0 + 46, tx + 8, deck_y], fill=(162, 170, 180))
        draw.rectangle([tx - 3, y0 + 42, tx + 11, y0 + 48], fill=(162, 170, 180))
        draw.line([(tx, y0 + 60), (tx + 8, y0 + 84)], fill=(140, 148, 158), width=1)
        draw.line([(tx + 8, y0 + 60), (tx, y0 + 84)], fill=(140, 148, 158), width=1)
    cable((x0 + 6, y0 + 48), (x0 + 60, y0 + 44), 22)
    cable((x0 + 60, y0 + 44), (x1 - 60, y0 + 44), 26)
    cable((x1 - 60, y0 + 44), (x1 - 6, y0 + 48), 22)
    # hangers dropping from the main cable to the deck
    for hx in range(x0 + 30, x1 - 24, 26):
        if abs(hx - mid) < 34:
            continue
        t = (hx - (x0 + 60)) / float((x1 - 60) - (x0 + 60))
        cy = (y0 + 44) + 26 * 4 * t * (1 - t)
        draw.line([(hx, cy), (hx, deck_y)], fill=(170, 176, 184), width=1)

    # deck left and right of the blown gap, ends torn jagged
    gap = 52
    draw.rectangle([x0 + 6, deck_y, mid - gap // 2, deck_y + 7],
                   fill=(206, 211, 217))
    draw.rectangle([mid + gap // 2, deck_y, x1 - 6, deck_y + 7],
                   fill=(206, 211, 217))
    draw.polygon([(mid - gap // 2, deck_y),
                  (mid - gap // 2 + 9, deck_y + 7),
                  (mid - gap // 2 + 3, deck_y + 13),
                  (mid - gap // 2 - 5, deck_y + 9)], fill=(168, 174, 182))
    draw.polygon([(mid + gap // 2, deck_y),
                  (mid + gap // 2 - 9, deck_y + 7),
                  (mid + gap // 2 - 3, deck_y + 13),
                  (mid + gap // 2 + 5, deck_y + 9)], fill=(168, 174, 182))
    # a deck segment tipping nose-first into the gap
    draw.polygon([(mid - gap // 2 + 2, deck_y + 2), (mid + 12, deck_y + 5),
                  (mid - 8, deck_y + 36), (mid - gap // 2 - 2, deck_y + 30)],
                 fill=(180, 186, 194))
    draw.line([(mid - 8, deck_y + 36), (mid + 2, sea_y - 2)],
              fill=(180, 186, 194), width=3)

    # fireball in the gap: rays, glow rings, hot core
    cx, cy = mid, deck_y - 12
    for ang in range(0, 360, 18):
        ln = 32 if ang % 54 == 0 else 22
        ex = cx + math.cos(math.radians(ang)) * ln
        ey = cy + math.sin(math.radians(ang)) * ln
        draw.line([(cx, cy), (ex, ey)], fill=(255, 176, 32), width=4)
    dot(draw, cx, cy, 18, (255, 120, 20))
    dot(draw, cx, cy, 11, (255, 214, 90))
    dot(draw, cx, cy, 5, (255, 246, 202))
    # smoke column, drifting left as it rises
    for sx, sy, r, col in [(mid - 2, cy - 28, 13, (108, 110, 116)),
                           (mid - 10, cy - 46, 15, (126, 128, 134)),
                           (mid - 24, cy - 62, 13, (144, 146, 152)),
                           (mid - 38, cy - 66, 10, (158, 160, 166)),
                           (mid + 14, cy - 54, 9, (126, 128, 134))]:
        dot(draw, sx, sy, r, col)
    # blast light shimmering on the water under the gap
    for wy, wl in [(sea_y + 8, 46), (sea_y + 16, 32), (sea_y + 24, 20)]:
        draw.line([(cx - wl // 2, wy), (cx + wl // 2, wy)],
                  fill=(216, 132, 40), width=2)

    draw.text((x0 + 10, y0 + 8), "KERCH CROSSING", font=font(SANS_BOLD, 12),
              fill=(255, 255, 255))
    draw.text((x0 + 10, y1 - 22), "A span down — the bridge to Crimea",
              font=font(SANS_PLAIN, 11), fill=(216, 226, 240))
    draw.rectangle([x0, y0, x1, y1], outline=BLACK, width=2)


def lead_story(draw, y):
    top = y
    draw.text((EDGE, y), LEAD["kick"], font=font(SANS_BOLD, 13), fill=SCARLET)
    y += 22
    text_w = 592
    y = block(draw, EDGE, y, LEAD["head"], font(SERIF_BOLD, 31), text_w,
              gap=4, limit=2)
    y += 4
    y = block(draw, EDGE, y, LEAD["deck"], font(SERIF_PLAIN, 15), text_w,
              fill=BODY, gap=4, limit=2)
    y += 4
    draw.text((EDGE, y), LEAD["byline"], font=font(SERIF_ITALIC, 12), fill=GREY)
    kerch_scene(draw, 648, top, PAGE - EDGE - 648, 158)
    return max(y + 18, top + 158)

# ---------------------------------------------------------------- secondary illustrations
def flag_usa(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(178, 34, 52))
    for i in range(0, 7, 2):
        draw.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7],
                       fill=(240, 240, 240))
    draw.rectangle([x, y, x + int(w * 0.42), y + int(h * 0.55)],
                   fill=(28, 48, 96))
    for r in range(3):
        for c in range(4):
            dot(draw, x + 5 + c * 5, y + 5 + r * 5, 1, (255, 255, 255))


def flag_japan(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    dot(draw, x + w // 2, y + h // 2, 8, (188, 0, 45))


def flag_india(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h // 3], fill=(255, 153, 51))
    draw.rectangle([x, y + h // 3, x + w, y + 2 * h // 3],
                   fill=(255, 255, 255))
    draw.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(19, 136, 8))
    cx, cy = x + w // 2, y + h // 2
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=(0, 56, 120), width=1)
    for k in range(8):
        ang = math.radians(k * 45)
        draw.line([(cx, cy),
                   (cx + 6 * math.cos(ang), cy + 6 * math.sin(ang))],
                  fill=(0, 56, 120), width=1)


def flag_australia(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(0, 40, 104))
    # simplified Union Jack in the canton
    cw, ch = int(w * 0.5), int(h * 0.5)
    draw.rectangle([x, y, x + cw, y + ch], fill=(0, 40, 104))
    draw.line([(x, y), (x + cw, y + ch)], fill=(255, 255, 255), width=2)
    draw.line([(x + cw, y), (x, y + ch)], fill=(255, 255, 255), width=2)
    draw.line([(x, y + ch // 2), (x + cw, y + ch // 2)], fill=(255, 255, 255),
              width=3)
    draw.line([(x + cw // 2, y), (x + cw // 2, y + ch)], fill=(255, 255, 255),
              width=3)
    # Southern Cross stars
    for sx, sy in [(w - 14, 6), (w - 22, 14), (w - 10, 20), (w - 18, 26)]:
        dot(draw, x + sx, y + sy, 2, (255, 255, 255))
    dot(draw, x + w // 2, y + h - 10, 2, (255, 255, 255))


def panel_quad(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(238, 228, 200))
    flags = [(flag_usa, "USA"), (flag_japan, "JAPAN"),
             (flag_india, "INDIA"), (flag_australia, "AUSTRALIA")]
    fw, fh, gap = 62, 38, 12
    total = 4 * fw + 3 * gap
    sx = x0 + (w - total) // 2
    lab = font(SANS_BOLD, 8)
    for i, (fn, name) in enumerate(flags):
        fx = sx + i * (fw + gap)
        fn(draw, fx, y0 + 16, fw, fh)
        draw.rectangle([fx, y0 + 16, fx + fw, y0 + 16 + fh],
                       outline=BLACK, width=1)
        draw.text((fx + fw // 2, y0 + 58), name, font=lab, fill=BODY,
                  anchor="ma")


def panel_apec(draw, x0, y0, w, h):
    # dusk sky, then a lit Shenzhen skyline with one antenna tower
    sky = [(244, 198, 132), (228, 166, 124), (198, 132, 130), (152, 122, 142)]
    bh = h // len(sky)
    for i, colour in enumerate(sky):
        draw.rectangle([x0, y0 + i * bh, x0 + w, y0 + (i + 1) * bh], fill=colour)
    dot(draw, x0 + w - 48, y0 + 22, 14, (206, 64, 44))
    base = y0 + h
    towers = [(8, 34, 34), (48, 26, 48), (80, 30, 40), (116, 24, 56),
              (146, 34, 44), (186, 28, 38), (220, 30, 50), (256, 26, 30)]
    for bx, bw, bhgt in towers:
        draw.rectangle([x0 + bx, base - bhgt, x0 + bx + bw, base],
                       fill=(38, 52, 78))
        for wy in range(base - bhgt + 6, base - 4, 9):
            for wx in range(x0 + bx + 5, x0 + bx + bw - 4, 9):
                if (wx * 7 + wy * 13) % 5 < 2:
                    draw.rectangle([wx, wy, wx + 3, wy + 4],
                                   fill=(240, 200, 90))
    # antenna tower rising above the rest
    tx = x0 + 128
    draw.rectangle([tx, base - 66, tx + 6, base], fill=(38, 52, 78))
    draw.line([(tx + 3, base - 66), (tx + 3, base - 74)], fill=(38, 52, 78),
              width=2)
    dot(draw, tx + 3, base - 76, 2, (240, 80, 60))
    draw.text((x0 + 10, y0 + 6), "APEC", font=font(SANS_BOLD, 11),
              fill=(255, 255, 255))


def panel_nvda(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(13, 59, 34))
    for gy in range(1, 4):
        yy = y0 + gy * h // 4
        draw.line([(x0 + 8, yy), (x0 + w - 8, yy)], fill=(30, 90, 55), width=1)
    pts = [(x0 + 14, y0 + h - 14), (x0 + 54, y0 + h - 30),
           (x0 + 94, y0 + h - 24), (x0 + 134, y0 + h - 42),
           (x0 + 174, y0 + h - 36), (x0 + 214, y0 + h - 52),
           (x0 + 254, y0 + h - 48), (x0 + w - 12, y0 + h - 60)]
    draw.polygon(pts + [(x0 + w - 12, y0 + h - 4), (x0 + 14, y0 + h - 4)],
                 fill=(24, 96, 58))
    draw.line(pts, fill=(110, 220, 130), width=3, joint="curve")
    for px, py in pts[1:-1]:
        dot(draw, px, py, 3, (255, 255, 255))
    draw.text((x0 + 12, y0 + 8), "NVDA", font=font(SANS_BOLD, 13),
              fill=(255, 255, 255))
    draw.text((x0 + w - 12, y0 + h - 16), "+112% YoY",
              font=font(SANS_BOLD, 11), fill=(110, 220, 130), anchor="ra")
    draw.text((x0 + 12, y0 + h - 16), "$115.8bn revenue",
              font=font(SANS_PLAIN, 9), fill=(170, 210, 180))


PANELS = {"quad": panel_quad, "apec": panel_apec, "nvda": panel_nvda}


def secondaries(draw, y):
    col_w, gap = 306, 19
    bottom = y
    for i, sec in enumerate(SECONDARIES):
        x0 = EDGE + i * (col_w + gap)
        PANELS[sec["art"]](draw, x0, y, col_w, 72)
        draw.rectangle([x0, y, x0 + col_w, y + 72], outline=BLACK, width=1)
        ty = y + 80
        draw.text((x0, ty), sec["kick"], font=font(SANS_BOLD, 11),
                  fill=SCARLET)
        ty += 16
        ty = block(draw, x0, ty, sec["head"], font(SERIF_BOLD, 15), col_w,
                   gap=2, limit=3)
        ty += 2
        ty = block(draw, x0, ty, sec["stand"], font(SERIF_PLAIN, 11), col_w,
                   fill=GREY, gap=2, limit=1)
        bottom = max(bottom, ty)
    return bottom

# ---------------------------------------------------------------- story grid + ticker + footer
def story_grid(draw, y):
    draw.text((EDGE, y), "AROUND THE WORLD", font=font(SANS_BOLD, 13),
              fill=BLACK)
    draw.text((PAGE - EDGE, y), "18 MORE STORIES", font=font(SANS_PLAIN, 11),
              fill=GREY, anchor="ra")
    y += 20
    col_w, gap, row_h = 306, 19, 36
    kick_f = font(SANS_BOLD, 9)
    head_f = font(SERIF_PLAIN, 11)
    num_f = font(SANS_BOLD, 9)
    for row in range(6):
        for col in range(3):
            num, section, head = GRID[row * 3 + col]
            x0 = EDGE + col * (col_w + gap)
            yy = y + row * row_h
            if num is not None:
                draw.ellipse([x0, yy + 1, x0 + 15, yy + 16], fill=SCARLET)
                draw.text((x0 + 7.5, yy + 8), str(num), font=num_f,
                          fill=(255, 255, 255), anchor="mm")
            else:
                dot(draw, x0 + 7, yy + 9, 3, GREY)
            tx = x0 + 21
            draw.text((tx, yy), section, font=kick_f, fill=SCARLET)
            block(draw, tx, yy + 12, head, head_f, col_w - 21, gap=1, limit=2)
    return y + 6 * row_h


def news_ticker(draw, y):
    tick_f = font(SANS_PLAIN, 10)
    sep = "   •   "
    lines, current = [], ""
    for item in TICKER:
        trial = (current + sep + item) if current else item
        if draw.textlength(trial, font=tick_f) <= PAGE - 2 * EDGE - 20:
            current = trial
        else:
            lines.append(current)
            current = item
    if current:
        lines.append(current)
    strip_h = 6 + len(lines) * 14 + 6
    draw.rectangle([EDGE, y, PAGE - EDGE, y + strip_h], fill=(17, 17, 17))
    for li, line in enumerate(lines):
        draw.text((EDGE + 10, y + 3 + li * 14), line, font=tick_f,
                  fill=(240, 240, 240))
    return y + strip_h, len(lines)


# ---------------------------------------------------------------- compose + save
def compose():
    img = Image.new("RGB", (PAGE, PAGE), NEWS)
    draw = ImageDraw.Draw(img)
    y = masthead(draw)
    y = world_map(img, y + 8, 156)
    y = lead_story(draw, y + 6)
    y += 10
    rule(draw, y)
    y = secondaries(draw, y + 10)
    y += 8
    rule(draw, y)
    y = story_grid(draw, y + 8)
    y += 4
    y = double_rule(draw, y)
    end_y, tick_lines = news_ticker(draw, y + 6)
    draw.text((PAGE // 2, end_y + 4),
              "THE DAILY GLOBE — WORLD EDITION  ·  WEDNESDAY 18 NOVEMBER 2026  ·  PAGE 1",
              font=font(SANS_PLAIN, 9), fill=GREY, anchor="ma")
    print("ticker lines:", tick_lines, "content ends at y:", end_y)
    return img, end_y


def main():
    img, end_y = compose()
    if end_y > PAGE - 4:
        print(f"WARNING: content overflows by {end_y - (PAGE - 4)}px",
              file=sys.stderr)
    # THE FIX: when the grader sets MAKEFUN_OUTPUT_DIR, write ONLY there.
    # The repo directory is read-only in the grading sandbox, so saving
    # next to this file first would crash with PermissionError.
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        target = os.path.join(out_dir, "entry.png")
        img.save(target)
        print("saved", target, img.size)
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        target = os.path.join(here, "entry.png")
        img.save(target)
        print("saved", target, img.size)


if __name__ == "__main__":
    main()
