#!/usr/bin/env python3
"""Render the profile README cards into cards/.

Pink on black in every GitHub theme, set in Geist, with halftone dots for data and 1-bit dithered art.
GitHub shows SVGs through <img>, so fonts and bitmaps are embedded as data URIs.
"""
import base64
import calendar
import datetime
import io
import json
import math
import os
from html import escape

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")
with open(os.path.join(ROOT, "data", "content.json")) as f:
    CONTENT = json.load(f)
with open(os.path.join(ROOT, "data", "profile.json")) as f:
    DATA = json.load(f)
DAYS = DATA["days"]
TOTAL = DATA["total"]

W, GAP, R, PAD = 880, 12, 12, 32
THEME = dict(surface="#000000", line="#3d1529", ink="#ff6eb4", soft="#f291c2", muted="#c9709b",
             faint="#2b1220", tint="#1c0912", accent="#ff4fa3", on_accent="#000000", dot="#b83d7c", hot="#ff4fa3",
             name=("#ffa3d0", "#ff2e93"))
FONT_FILES = {
    "s4": ("Geist", 400, "Geist-Regular.woff2"),
    "s5": ("Geist", 500, "Geist-Medium.woff2"),
    "s6": ("Geist", 600, "Geist-SemiBold.woff2"),
    "m4": ("Geist Mono", 400, "GeistMono-Regular.woff2"),
}
SANS = "Geist, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

_fonts = {}


def font(key):
    if key not in _fonts:
        loaded = TTFont(os.path.join(FONTS, FONT_FILES[key][2]))
        _fonts[key] = (loaded.getBestCmap(), loaded["hmtx"].metrics, loaded["head"].unitsPerEm,
                       loaded["OS/2"].sCapHeight)
    return _fonts[key]


def measure(s, key, size, ls=0.0):
    cmap, hmtx, upm, _ = font(key)
    return sum(hmtx[cmap[ord(c)]][0] if ord(c) in cmap else upm * 0.55 for c in s) * size / upm + ls * len(s)


def cap(key, size):
    _, _, upm, cap_height = font(key)
    return cap_height / upm * size


def wrap(s, key, size, width):
    lines, line = [], ""
    for word in s.split():
        trial = f"{line} {word}".strip()
        if line and measure(trial, key, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


def balanced(s, key, size, width):
    """Wrap to the fewest lines, then narrow the measure so the last line is not a lone word."""
    lines = wrap(s, key, size, width)
    while len(lines) > 1 and width > 40 and len(wrap(s, key, size, width - 4)) == len(lines):
        width -= 4
        lines = wrap(s, key, size, width)
    return lines


def text(x, y, s, key, size, fill, anchor="start", ls=None):
    family_name, weight, _ = FONT_FILES[key]
    family = MONO if "Mono" in family_name else SANS
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    l = f' letter-spacing="{ls}"' if ls is not None else ""
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-weight="{weight}" '
            f'font-size="{size}" fill="{fill}"{a}{l}>{escape(s)}</text>')


def label(x, y, s, t, anchor="start", fill=None):
    return text(x, y, s.upper(), "m4", 10.5, fill or t["muted"], anchor=anchor, ls=1.2)


def font_face(keys):
    out = []
    for key in sorted(set(keys)):
        family, weight, filename = FONT_FILES[key]
        with open(os.path.join(FONTS, filename), "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        out.append(f"@font-face{{font-family:'{family}';font-weight:{weight};"
                   f"src:url(data:font/woff2;base64,{encoded}) format('woff2')}}")
    return "".join(out)


def svg(w, h, body, fonts, aria, defs="", view_x=0):
    style = font_face(fonts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" '
            f'viewBox="{view_x:.3f} 0 {w:.3f} {h}" '
            f'role="img" aria-label="{escape(aria)}"><title>{escape(aria)}</title>'
            f"<defs>{defs}</defs><style>{style}</style>{body}</svg>")


def card(x, w, h, t):
    return (f'<rect x="{x + .5:.3f}" y=".5" width="{w - 1:.3f}" height="{h - 1}" rx="{R}" '
            f'fill="{t["surface"]}" stroke="{t["line"]}"/>')


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)


def dots(points, stroke):
    """Draw (x, y, r) dots compactly, as zero-length round-capped strokes grouped by radius."""
    by_radius = {}
    for x, y, r in points:
        by_radius.setdefault(round(r * 4) / 4, []).append(f"M{x:.1f} {y:.1f}h.01")
    return "".join(f'<path d="{"".join(p)}" stroke="{stroke}" stroke-width="{2 * r:.2f}" '
                   f'stroke-linecap="round" fill="none"/>' for r, p in by_radius.items() if r > 0)


# ------------------------------------------------------------------ cards
# The hero is cut into side-by-side images because a link cannot live inside an SVG shown through <img>.
# Each slice draws the same card through its own viewBox, so the seams do not show.
HERO_LEFT = 572
BUTTONS = (("portfolio", "Portfolio", 572, 92.4, 579.2), ("linkedin", "LinkedIn", 664.4, 92.4, 671.6),
           ("email", "Email", 756.8, 123.2, 764))


def name_points(lines, x, y_top, target_width, pitch=3.5, scale=3):
    with open(os.path.join(FONTS, FONT_FILES["s6"][2]), "rb") as f:
        loaded = TTFont(io.BytesIO(f.read()))
    loaded.flavor = None
    raw = io.BytesIO()
    loaded.save(raw)
    size = 40
    while max(measure(line, "s6", size + 1) for line in lines) < target_width:
        size += 1
    raw.seek(0)
    pil_font = ImageFont.truetype(raw, size * scale)
    baselines = [size * (0.84 + 0.96 * i) for i in range(len(lines))]
    height = baselines[-1] + size * 0.3
    mask = Image.new("L", (int((target_width + 12) * scale), int(height * scale)), 0)
    draw = ImageDraw.Draw(mask)
    for line, baseline in zip(lines, baselines):
        draw.text((0, baseline * scale), line, font=pil_font, fill=255, anchor="ls")
    pixels = np.asarray(mask, dtype=float) / 255
    points = []
    for row in range(int(pixels.shape[0] / scale / pitch)):
        for col in range(int(pixels.shape[1] / scale / pitch)):
            x0, y0 = int(col * pitch * scale), int(row * pitch * scale)
            coverage = pixels[y0:y0 + int(pitch * scale), x0:x0 + int(pitch * scale)].mean()
            if coverage > 0.12:
                points.append((x + col * pitch + pitch / 2, y_top + row * pitch + pitch / 2,
                               pitch * 0.58 * math.sqrt(coverage)))
    return points, height


def button_icon(key, cx, cy):
    color = THEME["on_accent"]
    line = f'stroke="{color}" stroke-width="1.7" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if key == "portfolio":
        return (f'<circle cx="{cx}" cy="{cy}" r="11" {line}/><ellipse cx="{cx}" cy="{cy}" rx="4.6" ry="11" {line}/>'
                f'<path d="M{cx - 11} {cy}h22" {line}/>')
    if key == "linkedin":
        return (f'<rect x="{cx - 11.5}" y="{cy - 11.5}" width="23" height="23" rx="4" fill="{color}"/>'
                + text(cx, cy + 6.2, "in", "s6", 16, THEME["accent"], anchor="middle", ls=-0.4))
    return (f'<rect x="{cx - 12.5}" y="{cy - 9}" width="25" height="18" rx="2.5" {line}/>'
            f'<path d="M{cx - 12} {cy - 7.5}L{cx} {cy + 1.5}L{cx + 12} {cy - 7.5}" {line}/>')


def hero(t):
    y_label = PAD + cap("m4", 10.5)
    y_name = y_label + 16
    points, name_h = name_points(CONTENT["name"], PAD, y_name, 440)
    tagline = wrap(CONTENT["tagline"], "s4", 16, HERO_LEFT - PAD - 20)
    y_tag = y_name + name_h + 20
    y_foot = y_tag + (len(tagline) - 1) * 22 + 34
    h = int(round(y_foot + PAD))
    # drawn into every slice, so text may cross a seam
    shared = (card(0, W, h, t) + label(W - PAD, y_label, CONTENT["place"], t, anchor="end")
              + label(W - PAD, y_foot, CONTENT["now"], t, anchor="end"))

    defs = (f'<linearGradient id="nm" gradientUnits="userSpaceOnUse" x1="{PAD}" x2="{PAD + 440}" y1="0" y2="0">'
            f'<stop offset="0" stop-color="{t["name"][0]}"/><stop offset="1" stop-color="{t["name"][1]}"/>'
            '</linearGradient>')
    left = [shared, label(PAD, y_label, CONTENT["study"], t), dots(points, "url(#nm)")]
    left += [text(PAD, y_tag + i * 22, line, "s4", 16, t["ink"], ls=-0.1) for i, line in enumerate(tagline)]
    left.append(label(PAD, y_foot, CONTENT["focus"], t, fill=t["accent"]))
    aria = f'{" ".join(CONTENT["name"])}. {CONTENT["tagline"]} {CONTENT["focus"]}.'
    write("hero.svg", svg(HERO_LEFT, h + GAP, "".join(left), ["s4", "m4"], aria, defs))

    width, height = 84, 96
    top = round((h - height) / 2)
    for key, title, slice_x, slice_w, x in BUTTONS:
        cx = x + width / 2
        body = (shared + f'<rect x="{x}" y="{top}" width="{width}" height="{height}" rx="10" fill="{t["accent"]}"/>'
                + button_icon(key, round(cx, 2), top + 37)
                + text(cx, top + 75, title, "s5", 12.5, t["on_accent"], anchor="middle"))
        write(f"hero-{key}.svg", svg(slice_w, h + GAP, body, ["s5", "s6", "m4"], title, view_x=slice_x))


def grid():
    first = datetime.date.fromisoformat(DAYS[0]["date"])
    offset = (first.weekday() + 1) % 7
    return [((i + offset) // 7, (i + offset) % 7, d) for i, d in enumerate(DAYS)]


def levels():
    nonzero = sorted(d["count"] for d in DAYS if d["count"])
    q = [nonzero[int(len(nonzero) * f)] for f in (0.25, 0.5, 0.75)] if nonzero else [1, 2, 3]
    return lambda c: 0 if c == 0 else 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4


def heatmap(t):
    cells = grid()
    columns = cells[-1][0] + 1
    pitch = (W - 2 * PAD) / columns
    y_title = PAD + cap("s5", 19)
    top = y_title + 22
    y_months = top + 7 * pitch + 26
    h = int(round(y_months + PAD))
    body = [card(0, W, h, t), text(PAD, y_title, "Contributions", "s5", 19, t["ink"], ls=-0.3),
            label(W - PAD, y_title, "the last 12 months", t, anchor="end")]
    level = levels()
    radii = [1.0, 2.0, 3.0, 4.0, 5.0]
    k = pitch / 15.4
    empty, normal, hot, today = [], [], [], []
    for col, row, day in cells:
        L = level(day["count"])
        point = (PAD + col * pitch + pitch / 2, top + row * pitch + pitch / 2, radii[L] * k)
        if day["date"] == DAYS[-1]["date"]:
            today.append((point[0], point[1], max(radii[L], 2.5) * k))
        else:
            (empty if L == 0 else hot if L == 4 else normal).append(point)
    body += [dots(empty, t["faint"]), dots(normal, t["dot"]), dots(hot, t["hot"]), dots(today, t["accent"])]
    seen = set()
    for col, _, day in cells:
        date = datetime.date.fromisoformat(day["date"])
        if date.day == 1 and date.month not in seen and col < columns - 2:
            seen.add(date.month)
            body.append(label(PAD + col * pitch + pitch / 2, y_months, calendar.month_abbr[date.month], t,
                              anchor="middle"))
    aria = f"Contribution graph: {TOTAL} contributions in the last year"
    write(f"heatmap.svg", svg(W, h + GAP, "".join(body), ["s5", "m4"], aria))


def stats(t):
    y_num = PAD + cap("s6", 34)
    y_label = y_num + 24
    h = int(round(y_label + PAD))
    best = max(DAYS, key=lambda d: d["count"])
    best_date = datetime.date.fromisoformat(best["date"])
    items = [(f"{TOTAL:,}", "contributions"), (str(DATA["merged_prs"]), "pull requests merged"),
             (str(best["count"]), f"busiest day · {calendar.month_abbr[best_date.month]} {best_date.day}")]
    column = (W - 2 * PAD) / 3
    body = [card(0, W, h, t)]
    for i, (big, caption) in enumerate(items):
        x = PAD + i * column
        if i:
            body.append(f'<line x1="{x - 20:.2f}" x2="{x - 20:.2f}" y1="{PAD}" y2="{h - PAD}" stroke="{t["line"]}"/>')
        body.append(text(x, y_num, big, "s6", 34, t["ink"], ls=-1))
        body.append(label(x, y_label, caption, t))
    aria = f"{TOTAL} contributions in the last 12 months, {DATA['merged_prs']} pull requests merged, busiest day {best['count']}"
    write("stats.svg", svg(W, h + GAP, "".join(body), ["s6", "m4"], aria))


def tile_field(i, u, v):
    if i == 0:   # a rising wave
        return max(0.0, 1 - abs(v - (0.75 - 0.5 * u - 0.12 * math.sin(u * 9))) * 3.2)
    if i == 1:   # one ring per hackathon
        return max(max(0.0, 1 - abs(math.hypot((u - c) * 3.3, v - 0.5) - 0.3) * 8) for c in (0.14, 0.38, 0.62, 0.86))
    return max(0.0, 1 - math.hypot((u - 0.5) * 1.5, v - 1.05) * 1.25)  # a peak


def tiles(t):
    cw = (W - 2 * GAP) / 3
    ip = 22
    art_h = 100
    y_label = art_h + ip + cap("m4", 10.5)
    y_value = y_label + 36
    y_text = y_value + 25
    count = max(len(wrap(x["text"], "s4", 12.5, cw - 2 * ip)) for x in CONTENT["tiles"])
    h = int(round(y_text + (count - 1) * 17 + ip + 2))
    for i, tile in enumerate(CONTENT["tiles"]):
        x = [0, GAP / 3, 2 * GAP / 3][i]
        pitch = 6.2
        points = []
        for row in range(int((art_h - 16) / pitch)):
            for col in range(int((cw - 24) / pitch)):
                u, v = col * pitch / (cw - 24), row * pitch / (art_h - 16)
                value = tile_field(i, u, v)
                if value > 0.05:
                    points.append((x + 12 + col * pitch + pitch / 2, 8 + row * pitch + pitch / 2,
                                   pitch * 0.46 * math.sqrt(value)))
        body = [card(x, cw, h, t), dots(points, t["accent"]),
                f'<line x1="{x + 1}" x2="{x + cw - 1}" y1="{art_h + .5}" y2="{art_h + .5}" stroke="{t["line"]}"/>',
                label(x + ip, y_label, tile["label"], t),
                text(x + cw - ip, y_label + 1, "↗", "m4", 12, t["muted"], anchor="end") if tile.get("linked", True) else "",
                text(x + ip - 1, y_value, tile["value"], "s6", 26, t["ink"], ls=-0.7)]
        for j, line in enumerate(wrap(tile["text"], "s4", 12.5, cw - 2 * ip)):
            body.append(text(x + ip, y_text + j * 17, line, "s4", 12.5, t["soft"]))
        aria = f'{tile["label"]}: {tile["value"]}. {tile["text"]}'
        write(f"tile-{i}.svg", svg(W / 3, h + GAP, "".join(body), ["s4", "s6", "m4"], aria))


def section_title(t, name, title, note):
    h = 52
    body = (card(0, W, h, t) + text(PAD, 32, title, "s5", 19, t["ink"], ls=-0.3)
            + label(W - PAD, 31, note, t, anchor="end"))
    write(f"title-{name}.svg", svg(W, h + GAP, body, ["s5", "m4"], title))


# ------------------------------------------------------------------ dithered project art
def art_ruby(w, h):
    image = Image.new("L", (w, h), 18)
    draw = ImageDraw.Draw(image)
    cx, top, mid, bottom, half = w / 2, h * .12, h * .38, h * .92, h * .78
    girdle = [cx - half, cx - half * .5, cx, cx + half * .5, cx + half]
    crown = [cx - half * .55, cx, cx + half * .55]
    shades = [150, 215, 120, 235]
    for i in range(4):
        draw.polygon([(girdle[i], mid), (girdle[i + 1], mid), (cx, bottom)], fill=shades[i])
    draw.polygon([(girdle[0], mid), (crown[0], top), (girdle[1], mid)], fill=235)
    draw.polygon([(crown[0], top), (crown[1], top), (girdle[1], mid)], fill=120)
    draw.polygon([(crown[1], top), (girdle[1], mid), (girdle[2], mid)], fill=205)
    draw.polygon([(crown[1], top), (girdle[2], mid), (girdle[3], mid)], fill=95)
    draw.polygon([(crown[1], top), (crown[2], top), (girdle[3], mid)], fill=175)
    draw.polygon([(crown[2], top), (girdle[3], mid), (girdle[4], mid)], fill=125)
    return np.asarray(image, dtype=float) / 255


def art_scanner(w, h):
    y, x = np.mgrid[0:h, 0:w]
    field = np.zeros((h, w))
    for cx, weight in ((w * .39, .62), (w * .61, .62)):
        d = np.hypot(x - cx, y - h / 2) / (h * .46)
        field += weight * np.clip(1 - d, 0, 1) ** .55 * (.72 + .28 * np.sin(d * 24))
    return np.clip(field, 0, 1)


def art_design(w, h):
    y, x = np.mgrid[0:h, 0:w]
    cell = 14
    u, v = (x % cell) / cell - .5, (y % cell) / cell - .5
    a, b = x // cell, y // cell
    size = .16 + .3 * (np.sin(a * .55 + b * .9) * .5 + .5)
    kind = (a + 2 * b) % 3
    circle = np.hypot(u, v) < size
    square = np.maximum(abs(u), abs(v)) < size * .86
    ring = abs(np.hypot(u, v) - size) < .09
    shape = np.where(kind == 0, circle, np.where(kind == 1, square, ring))
    return shape * (.45 + .55 * x / w) + .04


def art_wattsentry(w, h):
    y, x = np.mgrid[0:h, 0:w]
    u = x / w
    curve = h * (.56 - .3 * np.sin(u * math.pi * 3 - .7) * np.exp(-((u - .55) ** 2) * 2.6))
    band = h * (.05 + .17 * u)
    inside = np.clip(1 - abs(y - curve) / band, 0, 1) * .62
    line = np.clip(1 - abs(y - curve) / 1.6, 0, 1)
    below = np.clip((y - curve) / h, 0, 1) * .34
    return np.clip(inside + line + below, 0, 1)


def art_audiobolt(w, h):
    rng = np.random.default_rng(7)
    y, x = np.mgrid[0:h, 0:w]
    field = rng.random((h, w)) * .13
    for t0, f0, amp in ((.2, .34, .13), (.48, .52, .18), (.76, .7, .12)):
        for harmonic in (0, 1, 2):
            base = f0 + harmonic * .11
            curve = h * (base + amp * np.arctan((x / w - t0) * 15) / (math.pi / 2))
            field += (.95 - harmonic * .25) * np.exp(-((y - curve) / 1.5) ** 2)
    return np.clip(field, 0, 1)


def art_server(w, h):
    rng = np.random.default_rng(5)
    image = Image.new("L", (w, h), 10)
    draw = ImageDraw.Draw(image)
    cx, cy = w / 2, h / 2
    for _ in range(46):
        angle = rng.uniform(0, math.tau)
        ex, ey = cx + math.cos(angle) * w * .62, cy + math.sin(angle) * h * .95
        draw.line([(cx, cy), (ex, ey)], fill=int(rng.uniform(70, 175)), width=1)
    for radius, shade in ((h * .42, 120), (h * .3, 175)):
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=shade, width=2)
    draw.ellipse([cx - h * .14, cy - h * .14, cx + h * .14, cy + h * .14], fill=255)
    return np.asarray(image, dtype=float) / 255


def art_ctf(w, h):
    rng = np.random.default_rng(13)
    y, x = np.mgrid[0:h, 0:w]
    cells = rng.random((h // 4 + 1, w // 4 + 1))[y // 4, x // 4]
    field = (cells > .84) * .24
    pole = (abs(x - w * .36) < 2) & (y > h * .1) & (y < h * .92)
    wave = h * (.16 + .035 * np.sin((x - w * .36) / w * 16))
    flag = (x > w * .36) & (x < w * .66) & (y > wave) & (y < wave + h * .4)
    field = np.where(flag, .55 + .45 * (cells > .35), field)
    return np.clip(np.where(pole, 1.0, field), 0, 1)


def art_zattify(w, h):
    rng = np.random.default_rng(11)
    image = Image.new("L", (w, h), 12)
    draw = ImageDraw.Draw(image)
    hubs = [(w * .28, h * .5), (w * .55, h * .36), (w * .77, h * .62)]
    draw.line(hubs, fill=190, width=2)
    for hx, hy in hubs:
        for _ in range(9):
            angle, length = rng.uniform(0, math.tau), rng.uniform(h * .22, h * .46)
            nx, ny = hx + math.cos(angle) * length * 1.4, hy + math.sin(angle) * length
            draw.line([(hx, hy), (nx, ny)], fill=105, width=1)
            draw.ellipse([nx - 2.5, ny - 2.5, nx + 2.5, ny + 2.5], fill=235)
    glow = image.filter(ImageFilter.GaussianBlur(4))
    field = np.maximum(np.asarray(image, dtype=float), np.asarray(glow, dtype=float) * 1.5) / 255
    canvas = Image.fromarray(np.uint8(np.clip(field, 0, 1) * 255))
    draw = ImageDraw.Draw(canvas)
    for hx, hy in hubs:
        draw.ellipse([hx - 7, hy - 7, hx + 7, hy + 7], fill=255)
    return np.asarray(canvas, dtype=float) / 255


ART = {"ruby": art_ruby, "scanner": art_scanner, "wattsentry": art_wattsentry, "audiobolt": art_audiobolt,
       "server": art_server, "design": art_design, "zattify": art_zattify, "ctf": art_ctf}
_bits = {}


def atkinson(field):
    a = np.array(field, dtype=float)
    h, w = a.shape
    bits = np.zeros((h, w), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            old = a[y, x]
            bits[y, x] = 1 if old >= .5 else 0
            error = (old - bits[y, x]) / 8
            for dx, dy in ((1, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2)):
                if 0 <= x + dx < w and y + dy < h:
                    a[y + dy, x + dx] += error
    return bits


def png_uri(bits, color):
    rgb = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    image = Image.fromarray(bits, mode="P")
    image.putpalette([0, 0, 0] + rgb)
    out = io.BytesIO()
    image.save(out, "PNG", optimize=True, transparency=0)
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode()


def projects(t):
    cw = (W - GAP) / 2
    h, art_h, px = 296, 140, 2
    for i, project in enumerate(CONTENT["projects"]):
        x = 0 if i % 2 == 0 else GAP / 2
        key = project["id"]
        columns, rows = int((cw - 2) // px), art_h // px
        if key not in _bits:
            _bits[key] = atkinson(ART[key](columns, rows))
        r = R - 1
        clip = (f'<clipPath id="c{i}"><path d="M{x + 1:.2f},{art_h} V{r + 1} a{r},{r} 0 0 1 {r},-{r} '
                f'H{x + cw - 1 - r:.2f} a{r},{r} 0 0 1 {r},{r} V{art_h} Z"/></clipPath>')
        y0 = art_h + 36
        body = [card(x, cw, h, t),
                f'<g clip-path="url(#c{i})"><image style="image-rendering:pixelated" '
                f'x="{x + 1:.2f}" y="1" width="{columns * px}" height="{rows * px}" '
                f'href="{png_uri(_bits[key], t["accent"])}"/></g>',
                f'<line x1="{x + 1}" x2="{x + cw - 1}" y1="{art_h + .5}" y2="{art_h + .5}" stroke="{t["line"]}"/>',
                text(x + 22, y0, project["name"], "s6", 18, t["ink"], ls=-0.3),
                text(x + cw - 22, y0 - 1, project["lang"].upper(), "m4", 10.5, t["muted"], anchor="end", ls=1.0)]
        for j, line in enumerate(wrap(project["pitch"], "s4", 13, cw - 44)[:3]):
            body.append(text(x + 22, y0 + 26 + j * 19, line, "s4", 13, t["soft"]))
        body.append(label(x + 22, h - 22, project["tag"], t, fill=t["accent"]))
        aria = f'{project["name"]}: {project["pitch"]}'
        write(f"project-{key}.svg", svg(W / 2, h + GAP, "".join(body), ["s4", "s6", "m4"], aria, clip))


def see_more(t):
    h, title, size = 56, "See more", 16
    arrow = 10
    x = (W - measure(title, "s5", size) - 8 - arrow) / 2
    ax, cy = x + measure(title, "s5", size) + 8, h / 2
    stroke = f'stroke="{t["on_accent"]}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    body = (f'<rect width="{W}" height="{h}" rx="{R}" fill="{t["accent"]}"/>'
            + text(x, cy + cap("s5", size) / 2, title, "s5", size, t["on_accent"], ls=-0.1)
            + f'<path d="M{ax:.2f} {cy + 5}L{ax + arrow:.2f} {cy - 5}M{ax + 2:.2f} {cy - 5}H{ax + arrow:.2f}V{cy + 3}" {stroke}/>')
    write("see-more.svg", svg(W, h + GAP, body, ["s5"], "See more: all repositories"))


def stack(t):
    y_title = PAD + cap("s5", 19)
    size, chip_h, gap, row_gap = 12, 26, 7, 8
    left = PAD + 112
    y = y_title + 26
    body = [text(PAD, y_title, "Stack", "s5", 19, t["ink"], ls=-0.3)]
    for group, items in CONTENT["stack"]:
        body.append(label(PAD, y + 17, group, t))
        cx = left
        for item in items:
            width = measure(item, "m4", size) + 20
            if cx + width > W - PAD:
                cx, y = left, y + chip_h + row_gap
            body.append(f'<rect x="{cx + .5:.2f}" y="{y + .5:.2f}" width="{width - 1:.2f}" height="{chip_h - 1}" '
                        f'rx="{chip_h / 2 - .5}" fill="none" stroke="{t["line"]}"/>')
            body.append(text(cx + width / 2, y + 17.5, item, "m4", size, t["ink"], anchor="middle"))
            cx += width + gap
        y += chip_h + 14
    h = int(round(y - 14 + PAD))
    aria = "Stack: " + "; ".join(f'{group}: {", ".join(items)}' for group, items in CONTENT["stack"])
    write(f"stack.svg", svg(W, h + GAP, card(0, W, h, t) + "".join(body), ["s5", "m4"], aria))


def orgs(t):
    h, size, width = 84, 40, W / 3
    top = (h - size) / 2
    shared = card(0, W, h, t)
    for i, org in enumerate(CONTENT["orgs"]):
        slice_x = i * width
        x = slice_x + 24
        with open(os.path.join(ROOT, "assets", "orgs", f'{org["id"]}.png'), "rb") as f:
            logo = base64.b64encode(f.read()).decode()
        clip = f'<clipPath id="o{i}"><rect x="{x:.2f}" y="{top}" width="{size}" height="{size}" rx="9"/></clipPath>'
        body = [shared,
                f'<image clip-path="url(#o{i})" x="{x:.2f}" y="{top}" width="{size}" height="{size}" '
                f'href="data:image/png;base64,{logo}"/>',
                f'<rect x="{x + .5:.2f}" y="{top + .5}" width="{size - 1}" height="{size - 1}" rx="8.5" '
                f'fill="none" stroke="{t["line"]}"/>',
                text(x + size + 12, top + 17, org["name"], "s5", 15, t["ink"], ls=-0.1),
                text(x + size + 12, top + 35, org["role"], "s4", 12.5, t["soft"]),
                text(slice_x + width - 18, top + 11, "↗", "m4", 12, t["muted"], anchor="end")]
        if i:
            body.append(f'<line x1="{slice_x + .5:.2f}" x2="{slice_x + .5:.2f}" y1="20" y2="{h - 20}" '
                        f'stroke="{t["line"]}"/>')
        aria = f'{org["name"]}: {org["role"]}'
        write(f'org-{org["id"]}.svg', svg(width, h + GAP, "".join(body), ["s4", "s5", "m4"], aria, clip, view_x=slice_x))


def log(t):
    rows = CONTENT["log"]
    y_title = PAD + cap("s5", 19)
    rail, tile_h, row_h, section_gap = 104, 64, 72, 34
    spine = PAD + rail + 18
    left = spine + 22
    column_gap = 8
    cw = (W - PAD - left - column_gap) / 2
    years = {}
    for row in rows:
        years.setdefault(row[0], []).append(row)

    body = [text(PAD, y_title, "Log", "s5", 19, t["ink"], ls=-0.3),
            label(W - PAD, y_title, "projects and hackathons, newest first", t, anchor="end")]
    defs = (f'<linearGradient id="yr" gradientUnits="userSpaceOnUse" x1="{PAD}" x2="{PAD + rail}" y1="0" y2="0">'
            f'<stop offset="0" stop-color="{t["name"][0]}"/><stop offset="1" stop-color="{t["name"][1]}"/>'
            '</linearGradient>')
    y = y_title + 26
    for index, (year, items) in enumerate(years.items()):
        section_h = math.ceil(len(items) / 2) * row_h - (row_h - tile_h)
        if index:
            body.append(f'<line x1="{PAD}" x2="{W - PAD}" y1="{y - section_gap / 2:.1f}" '
                        f'y2="{y - section_gap / 2:.1f}" stroke="{t["line"]}"/>')
        points, year_h = name_points([year], PAD, y, rail, pitch=2.4)
        body.append(dots(points, "url(#yr)"))
        count = f'{len(items)} {"entry" if len(items) == 1 else "entries"}'
        body.append(label(PAD, y + year_h + 8, count, t))
        steps = max(int(section_h / 6), 1)
        body.append(dots([(spine, y + i * 6 + 3, .5 + 1.5 * (1 - i / steps)) for i in range(steps)], t["dot"]))

        for j, (_, name, desc, hack) in enumerate(items):
            x = left + (j % 2) * (cw + column_gap)
            top = y + (j // 2) * row_h
            fill, stroke = (t["tint"], t["dot"]) if hack else ("none", t["line"])
            body.append(f'<rect x="{x + .5:.2f}" y="{top + .5:.2f}" width="{cw - 1:.2f}" height="{tile_h - 1}" '
                        f'rx="8" fill="{fill}" stroke="{stroke}"/>')
            body.append(text(x + 13, top + 22, name, "s5", 14, t["ink"], ls=-0.1))
            what, _, where = desc.partition(" · ")
            lines = [(what, t["soft"] if hack else t["muted"]), (where, t["accent"])] if where else [
                (line, t["soft"] if hack else t["muted"]) for line in balanced(desc, "s4", 12, cw - 26)]
            for k, (line, color) in enumerate(lines[:2]):
                body.append(text(x + 13, top + 39 + k * 15, line, "s4", 12, color))
            if hack:
                pill = measure("HACKATHON", "m4", 9, 0.8) + 12
                pill_x = x + cw - 9 - pill
                body.append(f'<rect x="{pill_x:.2f}" y="{top + 9}" width="{pill:.2f}" height="16" rx="8" '
                            f'fill="{t["accent"]}"/>')
                body.append(text(pill_x + pill / 2, top + 20.2, "HACKATHON", "m4", 9, t["on_accent"],
                                 anchor="middle", ls=0.8))
        y += section_h + section_gap
    h = int(round(y - section_gap + PAD))
    aria = "Log: " + "; ".join(f"{y} {n}: {d}" for y, n, d, _ in rows)
    write(f"log.svg", svg(W, h + GAP, card(0, W, h, t) + "".join(body), ["s4", "s5", "m4"], aria, defs))


def main():
    t = THEME
    hero(t)
    heatmap(t)
    stats(t)
    tiles(t)
    section_title(t, "work", "Selected work", f'{len(CONTENT["projects"])} projects')
    projects(t)
    see_more(t)
    stack(t)
    orgs(t)
    log(t)
    print(f"rendered {len(os.listdir(OUT))} cards")


if __name__ == "__main__":
    main()
