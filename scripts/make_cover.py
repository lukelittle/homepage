#!/usr/bin/env python3
"""Generate a post's cover image from the `hero:` block in its front matter.

One template, two variants, in the site's own fonts (IBM Plex Sans titles,
Fira Code labels):

  card   Slate background with a faint grid and a ghosted detail (like a
         rule number). For technical posts.
  photo  The same card with a photo filling the right side, faded into the
         slate behind the title. For talks, events and personal posts.

Front matter example:

  cover:
      image: "cover.png"       # cover.jpg for photo style
      alt: "..."
      relative: true
  hero:
      style: card              # or photo
      color: reg               # reg | ai | cloud | talk
      label: "Regulated Markets on AWS"
      title: "Designing Pre-Trade Risk Controls on AWS"   # optional, defaults to the post title
      ghost: "15c3-5"          # card only; dropped if too long to fit
      chip: "SEC Rule 15c3-5"  # optional
      photo: "photo.jpg"       # photo only, relative to the post folder
      focus: [0.3, 0.4]        # photo only, optional: which part of the photo
                               # to keep when cropping (x, y from 0 to 1)

The image is written next to index.md as cover.png (card) or cover.jpg (photo).

Usage:
  python3 scripts/make_cover.py content/posts/2026/02/some-post/index.md [...]
  python3 scripts/make_cover.py --all      # every post with a hero: block
"""

import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
AVATAR = ROOT / "static" / "images" / "avatar.png"

W, H = 1200, 630   # design size (the 1200x630 social-preview shape)
SCALE = 2           # render at 2x so covers stay crisp on high-density screens
# reg: Regulated Markets · ai: applied AI · cloud: AWS and infrastructure
# talk: people (talks, podcasts, career, students)
SERIES = {"reg": "#14b8a6", "ai": "#f59e0b", "cloud": "#38bdf8", "talk": "#a78bfa"}
SLATE = "#0f172a"
SLATE_RGB = (15, 23, 42)


def font(name, size, variation=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if variation:
        f.set_variation_by_name(variation)
    return f


def plex(size, weight="Bold"):
    """IBM Plex Sans: the site's heading face, used for cover titles."""
    return font("IBMPlexSans-wdth-wght.ttf", size, weight)


def fira(size, weight="SemiBold"):
    return font("FiraCode-wght.ttf", size, weight)


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


def fit_title(draw, text, make_font, sizes, max_width, max_lines, spacing=0, two_line_sizes=None):
    """Prefer two lines, but only at the larger sizes (two_line_sizes); a long
    title gets three lines at full size rather than two tiny ones."""
    passes = [(two_line_sizes or sizes, 2), (sizes, max_lines)]
    for size_list, limit in passes:
        for size in size_list:
            fnt = make_font(size)
            lines = balanced(draw, text, fnt, max_width, spacing)
            if len(lines) <= limit:
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


def render(hero, title, photo_path=None):
    """Draw a cover at SCALE x the 1200x630 design size."""
    k = SCALE
    w, h = W * k, H * k
    color = SERIES[hero.get("color", "reg")]
    img = Image.new("RGBA", (w, h), SLATE)
    text_w = 820 * k

    if photo_path:
        # Photo fills the right ~64%, fading into the slate behind the title
        pw = int(w * 0.64)
        src = ImageOps.exif_transpose(Image.open(photo_path)).convert("RGBA")
        focus = tuple(hero.get("focus", (0.5, 0.4)))
        img.paste(ImageOps.fit(src, (pw, h), Image.LANCZOS, centering=focus), (w - pw, 0))
        fade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fade)
        # Fade from solid slate at the photo's left edge to a light tint by
        # ~56% across, so most of the photo stays visible
        x0, x1 = w - pw, int(w * 0.56)
        for x in range(w):
            if x < x0:
                a = 255
            elif x > x1:
                a = 55
            else:
                a = int(255 - 200 * ((x - x0) / (x1 - x0)) ** 0.7)
            fd.line([(x, 0), (x, h)], fill=SLATE_RGB + (a,))
        img = Image.alpha_composite(img, fade)
        text_w = 600 * k
    else:
        grid = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        g = ImageDraw.Draw(grid)
        for x in range(0, w, 48 * k):
            g.line([(x, 0), (x, h)], fill=(148, 163, 184, 16), width=k)
        for y in range(0, h, 48 * k):
            g.line([(0, y), (w, y)], fill=(148, 163, 184, 16), width=k)
        img = Image.alpha_composite(img, grid)

        # Ghosted detail, outline only; shrinks to fit or is left out
        ghost = hero.get("ghost")
        if ghost:
            layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            size, max_w = 190 * k, 470 * k
            while size > 90 * k and ld.textlength(ghost, font=fira(size, "Medium")) > max_w:
                size -= 4 * k
            gf = fira(size, "Medium")
            if ld.textlength(ghost, font=gf) <= max_w:
                gw = ld.textlength(ghost, font=gf)
                bottom = ld.textbbox((0, 0), ghost, font=gf)[3]
                ld.text((w - 64 * k - gw, h - 118 * k - bottom), ghost, font=gf, fill=(0, 0, 0, 0),
                        stroke_width=2 * k, stroke_fill=(148, 163, 184, 52))
                img = Image.alpha_composite(img, layer)

    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 14 * k, h), fill=color)

    left = 72 * k
    spaced(d, (left, 58 * k), hero.get("label", "").upper(), fira(19 * k), color, 2.5 * k)

    sizes = tuple(v * k for v in (70, 64, 58, 54, 50))
    fnt, lines, size = fit_title(d, title, plex, sizes, text_w, 3,
                                 two_line_sizes=tuple(v * k for v in (70, 64, 58)))
    line_h = int(size * 1.1)
    top = 100 * k + (h - 220 * k - line_h * len(lines)) // 2
    if photo_path:
        # Soft shadow so the title stays readable where it overlaps the photo
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        for i, line in enumerate(lines):
            sd.text((left, top + i * line_h), line, font=fnt, fill=SLATE_RGB + (230,))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10 * k))
        img = Image.alpha_composite(img, shadow)
        d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        d.text((left, top + i * line_h), line, font=fnt, fill=(241, 245, 249))

    # Footer: chip on the left, avatar + site on the right
    foot_y = h - 76 * k
    chip = hero.get("chip")
    if chip:
        cf = fira(20 * k, "Medium")
        cw = d.textlength(chip, font=cf)
        d.rounded_rectangle((left, foot_y - 10 * k, left + cw + 28 * k, foot_y + 32 * k), radius=7 * k,
                            fill=SLATE_RGB + (200,), outline=(148, 163, 184, 130), width=2 * k)
        d.text((left + 14 * k, foot_y - 1 * k), chip, font=cf, fill=(226, 232, 240))
    sf = fira(20 * k, "Medium")
    site = "lukelittle.com"
    sw = d.textlength(site, font=sf)
    right = w - 64 * k
    if photo_path:  # keep the site mark readable over the photo
        d.rounded_rectangle((right - sw - 70 * k, foot_y - 14 * k, right + 16 * k, foot_y + 36 * k),
                            radius=25 * k, fill=SLATE_RGB + (190,))
    d.text((right - sw, foot_y - 1 * k), site, font=sf, fill=(203, 213, 225))
    av = circle_avatar(46 * k)
    img.paste(av, (int(right - sw - 58 * k), foot_y - 12 * k), av)
    return img.convert("RGB")


def card(hero, title):
    return render(hero, title)


def photo(hero, title, folder):
    return render(hero, title, folder / hero["photo"])


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
        photo(hero, title, folder).save(out, quality=82, optimize=True, progressive=True)
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
