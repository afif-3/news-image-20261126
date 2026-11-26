"""Drawing toolkit for the front page: fonts, wrapping, rules, icons.

Everything is drawn with Pillow primitives only - no image assets, no
network, fully deterministic.  Fonts are resolved from a preference
list so the page renders identically on any machine that carries at
least one of the common open font families.
"""

import math
import os

from PIL import ImageFont

_FONT_DIRS = [
    "/usr/share/fonts/truetype/noto",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/dejavu",
]

_FONT_FILES = {
    "serif_black": ["NotoSerif-Black.ttf", "LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"],
    "serif_bold": ["NotoSerif-Bold.ttf", "LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"],
    "serif": ["NotoSerif-Regular.ttf", "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"],
    "sans_black": ["NotoSans-Black.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
    "sans_bold": ["NotoSans-Bold.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
    "sans": ["NotoSans-Regular.ttf", "LiberationSans-Regular.ttf", "DejaVuSans.ttf"],
}

_cache = {}


def font(kind, size):
    """Return a cached truetype font for the given style kind and size."""
    key = (kind, size)
    if key in _cache:
        return _cache[key]
    chosen = None
    for name in _FONT_FILES[kind]:
        for folder in _FONT_DIRS:
            path = os.path.join(folder, name)
            if os.path.exists(path):
                chosen = path
                break
        if chosen:
            break
    if chosen is None:
        result = ImageFont.load_default()
    else:
        result = ImageFont.truetype(chosen, size)
    _cache[key] = result
    return result


def text_width(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if text_width(draw, trial, fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, xy, lines, fnt, fill, leading):
    """Draw pre-split lines, returning the y just below the block."""
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tracked_text(draw, xy, text, fnt, fill, tracking):
    """Draw letter-spaced text (for kickers and masthead furniture)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += text_width(draw, ch, fnt) + tracking
    return x - tracking


def tracked_width(draw, text, fnt, tracking):
    if not text:
        return 0
    total = sum(text_width(draw, ch, fnt) for ch in text)
    return total + tracking * (len(text) - 1)


def rule(draw, x0, x1, y, fill, width=3):
    draw.rectangle([x0, y, x1, y + width - 1], fill=fill)


def kicker_tag(draw, xy, text, bg, fg, fnt, pad_x=14, pad_y=7, tracking=3):
    """A solid label chip with tracked capitals; returns its width."""
    w = tracked_width(draw, text, fnt, tracking)
    h = fnt.size + pad_y * 2 - 4
    x, y = xy
    draw.rectangle([x, y, x + w + pad_x * 2, y + h], fill=bg)
    tracked_text(draw, (x + pad_x, y + pad_y - 3), text, fnt, fg, tracking)
    return w + pad_x * 2, h


def draw_flame(draw, cx, cy, scale, fill):
    pts = []
    for t in range(0, 361, 6):
        a = math.radians(t)
        r = scale * (0.62 + 0.38 * math.sin(a * 3 + 1.2))
        pts.append((cx + r * math.sin(a) * 0.72, cy - r * math.cos(a) - scale * 0.25 * math.sin(a * 2)))
    draw.polygon(pts, fill=fill)
    draw.ellipse([cx - scale * 0.20, cy - scale * 0.18, cx + scale * 0.20, cy + scale * 0.30], fill=(255, 244, 214))


def draw_drop(draw, cx, cy, scale, fill):
    draw.polygon([(cx, cy - scale), (cx + scale * 0.62, cy + scale * 0.28), (cx - scale * 0.62, cy + scale * 0.28)], fill=fill)
    draw.ellipse([cx - scale * 0.62, cy - scale * 0.05, cx + scale * 0.62, cy + scale * 0.72], fill=fill)


def draw_stars_circle(draw, cx, cy, radius, fill, count=12):
    for i in range(count):
        a = 2 * math.pi * i / count
        sx = cx + radius * math.cos(a)
        sy = cy + radius * math.sin(a)
        r = radius * 0.13
        draw.polygon([(sx, sy - r), (sx + r * 0.32, sy - r * 0.32), (sx + r, sy),
                      (sx + r * 0.32, sy + r * 0.32), (sx, sy + r),
                      (sx - r * 0.32, sy + r * 0.32), (sx - r, sy),
                      (sx - r * 0.32, sy - r * 0.32)], fill=fill)


def draw_orbit(draw, cx, cy, radius, fill, accent):
    draw.ellipse([cx - radius, cy - radius * 0.42, cx + radius, cy + radius * 0.42], outline=fill, width=5)
    draw.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=accent)
    sx = cx + radius * 0.82
    sy = cy - radius * 0.30
    draw.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], fill=fill)


def tariff_bars(draw, box, fill, dim):
    """Rising bar chart symbolising escalating tariff rates."""
    x0, y0, x1, y1 = box
    heights = [0.30, 0.44, 0.58, 0.76, 1.0]
    n = len(heights)
    gap = (x1 - x0) * 0.06
    bw = ((x1 - x0) - gap * (n + 1)) / n
    for i, h in enumerate(heights):
        bx = x0 + gap + i * (bw + gap)
        by = y1 - (y1 - y0) * h
        draw.rectangle([bx, by, bx + bw, y1], fill=fill if i == n - 1 else dim)
    rule(draw, x0, x1, y1 + 6, fill, width=5)


def sparkline_down(draw, box, fill, width=7):
    """Jagged descending market line with an end dot."""
    x0, y0, x1, y1 = box
    frac = [(0.0, 0.10), (0.16, 0.30), (0.30, 0.22), (0.46, 0.48),
            (0.60, 0.40), (0.74, 0.66), (0.88, 0.60), (1.0, 0.88)]
    pts = [(x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy) for fx, fy in frac]
    draw.line(pts, fill=fill, width=width, joint="curve")
    ex, ey = pts[-1]
    draw.ellipse([ex - 11, ey - 11, ex + 11, ey + 11], fill=fill)
