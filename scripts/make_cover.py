#!/usr/bin/env python3
"""Generate a post's cover image from the `hero:` block in its front matter.

Two styles (see README "Cover images"):

  card   Title card for technical posts: slate grid, series color bar,
         ghosted detail (like a rule number), chip, avatar.
  photo  A real photo in a comic frame: halftone dots, ink border,
         caption box. For talks, events and personal posts.

Front matter example:

  cover:
      image: "cover.png"
      alt: "..."
      relative: true
  hero:
      style: card              # or photo
      color: reg               # reg | ai | talk
      label: "Regulated Markets on AWS"
      title: "Designing Pre-Trade Risk Controls on AWS"   # optional, defaults to the post title
      ghost: "15c3-5"          # card only
      chip: "SEC Rule 15c3-5"  # card only
      photo: "photo.jpg"       # photo only, relative to the post folder

The image is written next to index.md as cover.png (card) or cover.jpg (photo).

Usage:
  python3 scripts/make_cover.py content/posts/2026/02/some-post/index.md [...]
  python3 scripts/make_cover.py --all      # every post with a hero: block
"""

import sys
from pathlib import Path

import yaml
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
AVATAR = ROOT / "static" / "images" / "avatar.png"

W, H = 1200, 630
SERIES = {"reg": "#14b8a6", "ai": "#f59e0b", "talk": "#a78bfa"}
SLATE = "#0f172a"
INK = "#0b1220"
PAPER = "#f8fafc"


def font(name, size, variation=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if variation:
        f.set_variation_by_name(variation)
    return f


def sans(size):
    return font("InstrumentSans-wdth-wght.ttf", size, "Bold")


def mono(size, weight="Bold"):
    return font("JetBrainsMono-wght.ttf", size, weight)


def comic(size):
    return font("Bangers-Regular.ttf", size)


def wrap(draw, text, fnt, max_width, spacing=0):
    """Greedy word wrap using real glyph widths."""
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=fnt) + spacing * len(candidate) <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def spaced(draw, xy, text, fnt, fill, tracking):
    """Draw text with letter-spacing (tracking in px)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def spaced_width(draw, text, fnt, tracking):
    return sum(draw.textlength(ch, font=fnt) + tracking for ch in text) - tracking


def balanced(draw, text, fnt, max_width, spacing=0):
    """Wrap into the fewest lines, then narrow the measure as far as possible
    without adding a line, so lines come out even (no one-word last line)."""
    lines = wrap(draw, text, fnt, max_width, spacing)
    lo, hi = max_width // 3, max_width
    while lo < hi:
        mid = (lo + hi) // 2
        if len(wrap(draw, text, fnt, mid, spacing)) == len(lines):
            hi = mid
        else:
            lo = mid + 1
    return wrap(draw, text, fnt, hi, spacing)


def fit_title(draw, text, make_font, sizes, max_width, max_lines, spacing=0):
    for size in sizes:
        fnt = make_font(size)
        lines = balanced(draw, text, fnt, max_width, spacing)
        if len(lines) <= max_lines:
            return fnt, lines, size
    return fnt, lines, size


def circle_avatar(size):
    avatar = Image.open(AVATAR).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    bg = Image.new("RGBA", (size, size), "white")
    bg.paste(avatar, (0, 0), avatar)
    bg.putalpha(mask)
    return bg


def card(hero, title):
    color = SERIES[hero.get("color", "reg")]
    img = Image.new("RGBA", (W, H), SLATE)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(grid)
    for x in range(0, W, 48):
        g.line([(x, 0), (x, H)], fill=(148, 163, 184, 18))
    for y in range(0, H, 48):
        g.line([(0, y), (W, y)], fill=(148, 163, 184, 18))
    img = Image.alpha_composite(img, grid)

    # Ghosted detail, outline only, bleeding off the right edge
    ghost = hero.get("ghost")
    if ghost:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(layer)
        gf = mono(170)
        gw = gd.textlength(ghost, font=gf)
        gd.text((W - gw + 14, H - 84 - 170), ghost, font=gf, fill=(0, 0, 0, 0),
                stroke_width=2, stroke_fill=(148, 163, 184, 60))
        img = Image.alpha_composite(img, layer)

    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 16, H), fill=color)

    left, right = 78, W - 60
    spaced(d, (left, 54), hero.get("label", "").upper(), mono(16), color, 2)

    fnt, lines, size = fit_title(d, title, sans, (64, 58, 52, 46), 900, 3)
    line_h = int(size * 1.1)
    block_h = line_h * len(lines)
    top = 92 + (H - 92 - 110 - block_h) // 2
    for i, line in enumerate(lines):
        d.text((left, top + i * line_h), line, font=fnt, fill="#e2e8f0")

    # Footer: chip on the left, avatar + site on the right
    foot_y = H - 70
    chip = hero.get("chip")
    if chip:
        cf = mono(17, "Medium")
        cw = d.textlength(chip, font=cf)
        d.rounded_rectangle((left, foot_y - 8, left + cw + 26, foot_y + 28), radius=6,
                            outline=(148, 163, 184, 110), width=2)
        d.text((left + 13, foot_y - 1), chip, font=cf, fill="#cbd5e1")
    sf = mono(17, "Medium")
    site = "lukelittle.com"
    sw = d.textlength(site, font=sf)
    d.text((right - sw, foot_y - 1), site, font=sf, fill="#94a3b8")
    av = circle_avatar(40)
    img.paste(av, (int(right - sw - 52), foot_y - 10), av)
    return img.convert("RGB")


def photo(hero, title, folder):
    color = SERIES[hero.get("color", "talk")]
    pad, border = 20, 7
    img = Image.new("RGB", (W, H), PAPER)

    # Photo cropped to fill the frame, with a halftone dot overlay
    fw, fh = W - 2 * pad, H - 2 * pad
    src = ImageOps.exif_transpose(Image.open(folder / hero["photo"])).convert("RGB")
    framed = ImageOps.fit(src, (fw, fh), Image.LANCZOS, centering=hero.get("focus", (0.5, 0.4)))
    dots = Image.new("RGB", (fw, fh), "white")
    dd = ImageDraw.Draw(dots)
    step, r = 10, 2.1
    for y in range(0, fh, step):
        for x in range(0, fw, step):
            dd.ellipse((x - r, y - r, x + r, y + r), fill=(206, 210, 217))
    framed = ImageChops.multiply(framed, dots)
    img.paste(framed, (pad, pad))
    d = ImageDraw.Draw(img)
    d.rectangle((pad, pad, W - pad - 1, H - pad - 1), outline=INK, width=border)

    # Caption box, bottom-left, with a hard offset shadow in the series color
    box_left, box_w = 48, 700
    badge_font = mono(15)
    badge = hero.get("label", "").upper()
    tf, lines, size = fit_title(d, title.upper(), comic, (58, 52, 46, 40), box_w - 52, 2, spacing=1.5)
    line_h = int(size * 1.02)
    badge_h = 32
    box_h = 26 + badge_h + 14 + line_h * len(lines) + 22
    box_top = H - 48 - box_h
    shadow = 12
    d.rectangle((box_left + shadow, box_top + shadow, box_left + box_w + shadow, box_top + box_h + shadow), fill=color)
    d.rectangle((box_left, box_top, box_left + box_w, box_top + box_h), fill="white", outline=INK, width=border)

    bx, by = box_left + 26, box_top + 24
    bw = spaced_width(d, badge, badge_font, 1.8) + 22
    d.rectangle((bx, by, bx + bw, by + badge_h), fill=color, outline=INK, width=3)
    spaced(d, (bx + 11, by + 6), badge, badge_font, INK, 1.8)

    ty = by + badge_h + 14
    for i, line in enumerate(lines):
        spaced(d, (bx, ty + i * line_h), line, tf, INK, 1.5)
    return img


def front_matter(path):
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    return yaml.safe_load(text.split("---", 2)[1]) or {}


def build(path):
    path = Path(path).resolve()
    meta = front_matter(path)
    hero = meta.get("hero")
    if not hero:
        return None
    title = hero.get("title") or meta["title"]
    folder = path.parent
    if hero.get("style") == "photo":
        out = folder / "cover.jpg"
        photo(hero, title, folder).save(out, quality=86, optimize=True)
    else:
        out = folder / "cover.png"
        card(hero, title).save(out, optimize=True)
    return out


def main(args):
    if args == ["--all"]:
        args = [str(p) for p in (ROOT / "content" / "posts").rglob("index.md")]
    if not args:
        print(__doc__)
        return 1
    for arg in args:
        out = build(arg)
        if out:
            print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
