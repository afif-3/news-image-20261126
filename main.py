#!/usr/bin/env python3
"""THE WORLD TODAY - a newspaper front-page poster for 26 November 2026.

Single self-contained program, Python standard library only.
Implements its own rasterizer, its own stroke (vector) font and its
own PNG encoder (zlib + struct). No network, no clock, no randomness:
the output bytes are identical on every run.
"""

import os
import struct
import sys
import zlib
from binascii import crc32
from math import sqrt

# ---------------------------------------------------------------- canvas ---
SS = 2                      # supersample factor (rendered 2x, downscaled)
W = 1680                    # final poster width
H = 2200                    # final poster height
SW = W * SS                 # supersampled width
SH = H * SS                 # supersampled height

PAPER = (244, 236, 217)     # cream paper  #f4ecd9
INK = (26, 23, 16)          # ink          #1a1710
RED = (179, 35, 27)         # red accent   #b3231b
GOLD = (217, 164, 65)       # gold         #d9a441
DARK = (23, 20, 29)         # dark panel   #17141d
FAINT = (120, 110, 88)      # muted ink for hairlines / footer
CREAM_DIM = (214, 205, 182)  # dim cream for dark-panel body text

BUF = bytearray(bytes(PAPER) * (SW * SH))


# ------------------------------------------------------------- rasterizer ---
def _fill_ss(x0, y0, x1, y1, color):
    """Fill an axis-aligned rectangle given in supersampled pixels."""
    if x0 < 0:
        x0 = 0
    if y0 < 0:
        y0 = 0
    if x1 > SW:
        x1 = SW
    if y1 > SH:
        y1 = SH
    if x1 <= x0 or y1 <= y0:
        return
    pat = bytes(color) * (x1 - x0)
    n = len(pat)
    row = y0
    base = (row * SW + x0) * 3
    step = SW * 3
    while row < y1:
        BUF[base:base + n] = pat
        base += step
        row += 1


def fill_rect(x, y, w, h, color):
    _fill_ss(int(x * SS), int(y * SS), int((x + w) * SS), int((y + h) * SS),
             color)


def outline_rect(x, y, w, h, color, t=3):
    fill_rect(x, y, w, t, color)
    fill_rect(x, y + h - t, w, t, color)
    fill_rect(x, y, t, h, color)
    fill_rect(x + w - t, y, t, h, color)


def hline(x, y, w, color, t=3):
    fill_rect(x, y, w, t, color)


def vline(x, y, h, color, t=3):
    fill_rect(x, y, t, h, color)


def _stamp(sx, sy, t, color):
    """Stamp a filled square of side t (supersampled px) centred at sx, sy."""
    half = t // 2
    _fill_ss(sx - half, sy - half, sx - half + t, sy - half + t, color)


def draw_line(x0, y0, x1, y1, thick, color):
    """Thick polyline segment; coordinates in final poster pixels."""
    ax, ay = x0 * SS, y0 * SS
    bx, by = x1 * SS, y1 * SS
    t = max(1, int(round(thick * SS)))
    dist = max(abs(bx - ax), abs(by - ay))
    step = max(1, t // 2)
    n = int(dist // step) + 1
    if n > 4000:
        n = 4000
    i = 0
    while i <= n:
        f = (i / n) if n else 0.0
        _stamp(int(ax + (bx - ax) * f), int(ay + (by - ay) * f), t, color)
        i += 1


def fill_circle(cx, cy, r, color):
    cr = int(r * SS)
    ccx, ccy = int(cx * SS), int(cy * SS)
    dy = -cr
    while dy <= cr:
        dx = int(sqrt(max(0, cr * cr - dy * dy)))
        _fill_ss(ccx - dx, ccy + dy, ccx + dx + 1, ccy + dy + 1, color)
        dy += 1


# -------------------------------------------------------------- stroke font ---
# Glyphs live on a grid 4 units wide, 6 units tall (x: 0..4, y: 0..6,
# y grows downward). Each glyph is a tuple of strokes; a stroke is a tuple
# of points. A one-point stroke stamps a dot.
GLYPHS = {
    "A": (((0, 6), (2, 0), (4, 6)), ((0.8, 4), (3.2, 4))),
    "B": (((0, 0), (0, 6)), ((0, 0), (2.8, 0), (4, 1.2), (2.8, 3), (0, 3)),
          ((0, 3), (2.8, 3), (4, 4.4), (2.8, 6), (0, 6))),
    "C": (((4, 1.2), (2.4, 0), (0.8, 0.6), (0, 2), (0, 4), (0.8, 5.4),
           (2.4, 6), (4, 4.8)),),
    "D": (((0, 0), (0, 6)), ((0, 0), (2.6, 0), (4, 1.8), (4, 4.2),
           (2.6, 6), (0, 6))),
    "E": (((4, 0), (0, 0), (0, 6), (4, 6)), ((0, 3), (3, 3))),
    "F": (((4, 0), (0, 0), (0, 6)), ((0, 3), (3, 3))),
    "G": (((4, 1.2), (2.4, 0), (0.8, 0.6), (0, 2), (0, 4), (0.8, 5.4),
           (2.4, 6), (4, 5), (4, 3.4), (2.2, 3.4)),),
    "H": (((0, 0), (0, 6)), ((4, 0), (4, 6)), ((0, 3), (4, 3))),
    "I": (((2, 0), (2, 6)), ((0.4, 0), (3.6, 0)), ((0.4, 6), (3.6, 6))),
    "J": (((4, 0), (4, 4.6), (3.2, 5.8), (1.2, 6), (0.2, 5)),),
    "K": (((0, 0), (0, 6)), ((4, 0), (0.4, 3.2)), ((1.6, 2.4), (4, 6))),
    "L": (((0, 0), (0, 6), (4, 6)),),
    "M": (((0, 6), (0, 0), (2, 3.2), (4, 0), (4, 6)),),
    "N": (((0, 6), (0, 0), (4, 6), (4, 0)),),
    "O": (((2, 0), (0.7, 0.7), (0, 2), (0, 4), (0.7, 5.3), (2, 6),
           (3.3, 5.3), (4, 4), (4, 2), (3.3, 0.7), (2, 0)),),
    "P": (((0, 6), (0, 0), (2.8, 0), (4, 1.2), (2.8, 3), (0, 3)),),
    "Q": (((2, 0), (0.7, 0.7), (0, 2), (0, 4), (0.7, 5.3), (2, 6),
           (3.3, 5.3), (4, 4), (4, 2), (3.3, 0.7), (2, 0)),
          ((2.6, 4.2), (4.2, 6.2))),
    "R": (((0, 6), (0, 0), (2.8, 0), (4, 1.2), (2.8, 3), (0, 3)),
          ((2.2, 3), (4, 6))),
    "S": (((4, 0.8), (2.6, 0), (0.8, 0.5), (0, 1.6), (0.8, 2.8), (3.2, 3.4),
           (4, 4.4), (3.4, 5.6), (1.6, 6), (0, 5.2)),),
    "T": (((0, 0), (4, 0)), ((2, 0), (2, 6))),
    "U": (((0, 0), (0, 4.4), (0.8, 5.6), (2, 6), (3.2, 5.6), (4, 4.4),
           (4, 0)),),
    "V": (((0, 0), (2, 6), (4, 0)),),
    "W": (((0, 0), (0.9, 6), (2, 2.4), (3.1, 6), (4, 0)),),
    "X": (((0, 0), (4, 6)), ((4, 0), (0, 6))),
    "Y": (((0, 0), (2, 3), (4, 0)), ((2, 3), (2, 6))),
    "Z": (((0, 0), (4, 0), (0, 6), (4, 6)),),
    "0": (((2, 0), (0.7, 0.7), (0, 2), (0, 4), (0.7, 5.3), (2, 6),
           (3.3, 5.3), (4, 4), (4, 2), (3.3, 0.7), (2, 0)),
          ((0.8, 5), (3.2, 1))),
    "1": (((1.2, 1.2), (2.4, 0), (2.4, 6)), ((0.6, 6), (3.6, 6))),
    "2": (((0.2, 1.4), (1, 0.3), (2.6, 0), (3.8, 1), (3.8, 2.2),
           (0.2, 6), (4, 6)),),
    "3": (((0.2, 0.6), (2.4, 0), (3.8, 1), (2.6, 3), (0.6, 3)),
          ((2.6, 3), (3.8, 4), (3.4, 5.6), (1.4, 6), (0.2, 5.4))),
    "4": (((3.2, 6), (3.2, 0), (0, 4.2), (4, 4.2)),),
    "5": (((3.8, 0), (0.4, 0), (0.2, 2.8), (2.4, 2.6), (3.8, 3.6),
           (3.6, 5.2), (2, 6), (0.2, 5.4)),),
    "6": (((3.6, 0.8), (2, 0), (0.6, 1.4), (0, 3), (0, 4.6), (1, 5.8),
           (2.6, 6), (4, 5), (3.8, 3.6), (2.4, 2.8), (0.2, 3.2)),),
    "7": (((0, 0), (4, 0), (1.8, 6)),),
    "8": (((2, 3), (0.8, 2.4), (0.2, 1.2), (1, 0.2), (3, 0.2), (3.8, 1.2),
           (3.2, 2.4), (2, 3), (0.6, 3.8), (0.2, 5), (1.2, 6), (2.8, 6),
           (3.8, 5), (3.4, 3.8), (2, 3)),),
    "9": (((0.4, 5.2), (2, 6), (3.4, 4.6), (4, 3), (4, 1.4), (3, 0.2),
           (1.4, 0), (0.2, 1), (0.4, 2.6), (1.8, 3.2), (3.8, 2.8)),),
    " ": (),
    ".": (((2, 5.6),),),
    ",": (((2, 5.2),), ((2.4, 5.4), (1.7, 6.3))),
    ":": (((2, 1.4),), ((2, 5.2),)),
    ";": (((2, 1.4),), ((2, 5.2),), ((2.4, 5.4), (1.7, 6.3))),
    "-": (((0.4, 3), (3.6, 3)),),
    "'": (((2.2, 0), (1.8, 1.5)),),
    "!": (((2, 0), (2, 4)), ((2, 5.6),)),
    "?": (((0.2, 1.2), (1, 0.2), (3, 0.2), (3.8, 1.2), (3.4, 2.4),
           (2, 3.4), (2, 4.4)), ((2, 5.6),)),
    "%": (((0, 6), (4, 0)), ((1, 0.4), (0.3, 1), (1, 1.7), (1.7, 1),
           (1, 0.4)), ((3, 4.3), (2.3, 4.9), (3, 5.6), (3.7, 4.9),
           (3, 4.3))),
    "$": (((4, 0.8), (2.6, 0), (0.8, 0.5), (0, 1.6), (0.8, 2.8), (3.2, 3.4),
           (4, 4.4), (3.4, 5.6), (1.6, 6), (0, 5.2)), ((2, -0.4), (2, 6.4))),
    "+": (((2, 1.2), (2, 4.8)), ((0.4, 3), (3.6, 3))),
    "/": (((0.8, 6), (3.2, 0)),),
    "(": (((3.2, 0), (1.4, 1.6), (1.4, 4.4), (3.2, 6)),),
    ")": (((0.8, 0), (2.6, 1.6), (2.6, 4.4), (0.8, 6)),),
    "&": (((4, 6), (1, 1.6), (0.6, 0.6), (1.8, 0), (2.8, 0.8), (2.4, 2),
           (0.4, 3.6), (0.2, 5), (1.2, 6), (2.8, 5.4), (4, 6)),
          ((2.8, 3.4), (4, 6))),
}


def text_width(text, size):
    unit = size / 6.0
    w = 0.0
    for ch in text:
        w += unit * 3.0 if ch == " " else unit * 5.0
    return w - unit  # no trailing gap after the last glyph


def draw_text(x, y, text, size, color, bold=False, align="l"):
    """Draw one line of text; (x, y) is the top-left of the line box."""
    text = text.upper()
    unit = size / 6.0
    thick = size * (0.17 if bold else 0.115)
    if thick < 1.6:
        thick = 1.6
    w = text_width(text, size)
    if align == "c":
        x = x - w / 2.0
    elif align == "r":
        x = x - w
    cx = float(x)
    for ch in text:
        if ch == " ":
            cx += unit * 3.0
            continue
        glyph = GLYPHS.get(ch)
        if glyph is None:
            glyph = GLYPHS["?"]
        for stroke in glyph:
            if len(stroke) == 1:
                px, py = stroke[0]
                _stamp(int((cx + px * unit) * SS), int((y + py * unit) * SS),
                       max(2, int(round(thick * 1.5 * SS))), color)
            else:
                for i in range(len(stroke) - 1):
                    x0, y0 = stroke[i]
                    x1, y1 = stroke[i + 1]
                    draw_line(cx + x0 * unit, y + y0 * unit,
                              cx + x1 * unit, y + y1 * unit, thick, color)
        cx += unit * 5.0
    return w


def wrap_text(text, size, max_w):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, text, size, color, max_w, line_h, bold=False,
                 align="l", max_lines=99):
    lines = wrap_text(text, size, max_w)[:max_lines]
    for line in lines:
        lx = x
        if align == "c":
            lx = x + max_w / 2.0
        draw_text(lx, y, line, size, color, bold=bold, align=align)
        y += line_h
    return y


def draw_kicker(x, y, text, size=25):
    draw_text(x, y, text, size, RED, bold=True)
    w = text_width(text, size)
    hline(x, y + size + 9, w, RED, t=3)
    return y + size + 20


# ------------------------------------------------------------------ layout ---
M = 64                      # page margin
CW = W - 2 * M              # column width (1552)


def render():
    # outer frame: heavy outer rule + hairline inner rule
    outline_rect(30, 30, W - 60, H - 60, INK, t=5)
    outline_rect(42, 42, W - 84, H - 84, INK, t=2)

    # ---- top line ------------------------------------------------------
    draw_text(M, 62, "THURSDAY, NOVEMBER 26, 2026", 21, INK, bold=True)
    draw_text(W - M, 62, "GLOBAL EDITION - 65 STORIES TRACKED - MOOD: UNEASY",
              21, INK, bold=True, align="r")
    hline(M, 100, CW, INK, t=4)
    hline(M, 108, CW, INK, t=1)

    # ---- masthead ------------------------------------------------------
    draw_text(W / 2, 122, "THE WORLD TODAY", 92, INK, bold=True, align="c")
    draw_text(W / 2, 228, "ONE PAGE. ONE DAY. THE WHOLE PLANET.", 27, RED,
              bold=True, align="c")
    hline(M, 272, CW, INK, t=1)
    hline(M, 278, CW, INK, t=4)

    # ---- lead story ----------------------------------------------------
    y = draw_kicker(M, 292, "TRADE - WASHINGTON", 26)
    draw_text(W / 2, y + 4, "AMERICA TAXES", 76, INK, bold=True, align="c")
    draw_text(W / 2, y + 100, "THE WORLD AGAIN", 76, RED, bold=True,
              align="c")
    y += 192
    y = draw_wrapped(M + 100, y, "The United States proposes new tariffs "
                     "on 14 trading partners - China, the EU, Japan and "
                     "India among them.", 30, INK, CW - 200, 40, align="c")
    y += 16
    hline(M + 500, y, CW - 1000, GOLD, t=5)
    y += 26

    # bullets (left) + stat panel (right)
    bullets = [
        "Rates up to 35% after an eight-month capacity probe",
        "China rejects the charges, stops short of retaliation",
        "Fourth Trump-Xi summit looms in Miami next month",
    ]
    by = y + 6
    for b in bullets:
        fill_rect(M + 2, by + 8, 12, 12, RED)
        by = draw_wrapped(M + 30, by, b, 25, INK, 940, 34)
        by += 12
    lead_bottom = by

    px, pw = 1104, 512
    ph = 232
    outline_rect(px, y, pw, ph, INK, t=3)
    fill_rect(px, y, pw, 10, RED)
    draw_text(px + 34, y + 26, "14", 105, RED, bold=True)
    draw_wrapped(px + 218, y + 34, "ECONOMIES IN THE FIRING LINE", 27, INK,
                 pw - 248, 36, bold=True)
    # small ascending bar chart along the panel's bottom edge
    base_y = y + ph - 22
    bx = px + 34
    heights = (18, 28, 38, 48, 58)
    for i, bh in enumerate(heights):
        fill_rect(bx + i * 56, base_y - bh, 40, bh, GOLD)
        outline_rect(bx + i * 56, base_y - bh, 40, bh, INK, t=2)
    hline(bx, base_y, 264, INK, t=3)
    draw_text(px + 326, base_y - 18, "TARIFF TARGETS", 15, FAINT, bold=True)
    y = max(lead_bottom, y + ph) + 26
    hline(M, y, CW, INK, t=3)
    y += 24

    # ---- stories 2-5: a 2 x 2 grid --------------------------------------
    stories = [
        ("CONFLICT - RIYADH", "Houthis strike Saudi ports and refinery",
         "Attacks claimed on Saudi ports and the giant Ras Tanura refinery "
         "as defences intercept missiles over Riyadh. Brent crude tops $94."),
        ("DISASTER - CAIRO", "Tanker fire kills 31 on Cairo ring road",
         "A fuel tanker overturned and burst into flames on the capital's "
         "busy ring road. At least 31 died and about 21 were injured."),
        ("EUROPE - BRUSSELS", "EU leaders clash over 45bn euro Ukraine loan",
         "Divisions over a loan for Kyiv and the bloc's next budget - as "
         "Ukraine reports damaging five jets at a Russian airbase."),
        ("SPACE - TIANGONG", "First Pakistani astronaut boards China's "
         "station",
         "Muhammad Zeeshan Ali arrives aboard Shenzhou-24, the first "
         "foreign national to join Tiangong - a milestone for Beijing's "
         "space diplomacy."),
    ]
    gap = 44
    col_w = (CW - gap) // 2
    mid_x = M + col_w + gap // 2
    row_h = 300
    grid_top = y
    for idx, (kick, head, body) in enumerate(stories):
        cx = M if idx % 2 == 0 else M + col_w + gap
        cy = grid_top if idx < 2 else grid_top + row_h
        sy = draw_kicker(cx, cy, kick, 23)
        sy = draw_wrapped(cx, sy + 2, head, 33, INK, col_w, 42, bold=True)
        sy += 4
        draw_wrapped(cx, sy, body, 23, INK, col_w, 32)
    vline(mid_x, grid_top + 4, row_h * 2 - 26, FAINT, t=2)
    hline(M, grid_top + row_h - 10, CW, FAINT, t=2)
    y = grid_top + row_h * 2 + 8
    hline(M, y, CW, INK, t=3)
    y += 24

    # ---- markets panel (dark) -------------------------------------------
    mp_h = 280
    fill_rect(M, y, CW, mp_h, DARK)
    fill_rect(M, y, CW, 8, GOLD)
    ix = M + 38
    iw = CW - 76
    draw_text(ix, y + 26, "MARKETS - NEW YORK", 24, GOLD, bold=True)
    draw_text(ix, y + 62, "AI SELL-OFF NEARS BEAR MARKET FOR NASDAQ", 37,
              PAPER, bold=True)
    draw_wrapped(ix, y + 112, "Nvidia falls 3.9% as AI jitters deepen, "
                 "even as the Dow tops 50,000.", 26, CREAM_DIM, 1000, 36)
    # descending red line chart, right side of the panel
    chx, chy, chw, chh = M + CW - 420, y + 106, 372, 96
    outline_rect(chx, chy, chw, chh, FAINT, t=2)
    pts = ((0, 10), (62, 24), (124, 18), (186, 42), (248, 54), (310, 50),
           (360, 78))
    for i in range(len(pts) - 1):
        draw_line(chx + 8 + pts[i][0], chy + 6 + pts[i][1],
                  chx + 8 + pts[i + 1][0], chy + 6 + pts[i + 1][1], 4, RED)
    for ptx, pty in pts:
        fill_circle(chx + 8 + ptx, chy + 6 + pty, 5, GOLD)
    # stats row
    stats = ("NVIDIA -3.9%", "NASDAQ NEAR -20%", "DOW 50,000+",
             "BRENT $94")
    sx = ix
    sy2 = y + mp_h - 58
    hline(ix, sy2 - 16, iw, FAINT, t=2)
    for i, s in enumerate(stats):
        col = RED if i < 2 else GOLD
        draw_text(sx, sy2, s, 28, col, bold=True)
        sx += text_width(s, 28) + 56
        if i < len(stats) - 1:
            vline(sx - 30, sy2 + 2, 26, FAINT, t=2)
    y += mp_h + 24

    # ---- red ticker band --------------------------------------------------
    tk_h = 188
    fill_rect(M, y, CW, tk_h, RED)
    fill_rect(M + 24, y + 20, 240, 44, DARK)
    draw_text(M + 42, y + 29, "ALSO TODAY", 26, PAPER, bold=True)
    ticker = ("KIM URGES WIDER NUCLEAR DEPLOYMENT /// SPAIN'S SNAP "
              "ELECTION IS SUNDAY /// 13 MINERS TRAPPED IN FLOODED "
              "INDONESIAN MINE /// US TELLS CITIZENS TO LEAVE IRAN /// "
              "LIVERPOOL BEAT BRUGGE 3-0 /// JUDGES SUGGEST DROPPING "
              "NETANYAHU CHARGE")
    draw_wrapped(M + 24, y + 80, ticker, 21, PAPER, CW - 48, 30, bold=True)
    y += tk_h + 20

    # ---- footer -----------------------------------------------------------
    hline(M, y, CW, INK, t=3)
    draw_wrapped(M + 130, y + 16, "Drawn entirely in code with the Python "
                 "standard library - Sources: Reuters, One Turn, Daily "
                 "Summary of World - 26.11.2026", 19, FAINT, CW - 260, 26,
                 align="c")
    print("[render] layout complete: masthead, lead, 4 stories, markets, "
          "ticker, footer")


# -------------------------------------------------------------- PNG output ---
def downscale():
    out = bytearray(W * H * 3)
    sw3 = SW * 3
    for yy in range(H):
        r0 = (2 * yy) * sw3
        r1 = r0 + sw3
        orow = yy * W * 3
        for xx in range(W):
            i0 = r0 + xx * 6
            i1 = r1 + xx * 6
            o = orow + xx * 3
            a = BUF[i0]
            b = BUF[i0 + 3]
            c = BUF[i1]
            d = BUF[i1 + 3]
            if a == b == c == d:
                out[o] = a
            else:
                out[o] = (a + b + c + d) >> 2
            a = BUF[i0 + 1]
            b = BUF[i0 + 4]
            c = BUF[i1 + 1]
            d = BUF[i1 + 4]
            if a == b == c == d:
                out[o + 1] = a
            else:
                out[o + 1] = (a + b + c + d) >> 2
            a = BUF[i0 + 2]
            b = BUF[i0 + 5]
            c = BUF[i1 + 2]
            d = BUF[i1 + 5]
            if a == b == c == d:
                out[o + 2] = a
            else:
                out[o + 2] = (a + b + c + d) >> 2
    return out


def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", crc32(tag + data) & 0xFFFFFFFF))


def encode_png(pixels):
    raw = bytearray()
    rowlen = W * 3
    for yy in range(H):
        raw.append(0)
        raw += pixels[yy * rowlen:(yy + 1) * rowlen]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + _chunk(b"IEND", b""))


def main():
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR", "")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    print("[render] THE WORLD TODAY - 26 November 2026 poster")
    print("[render] canvas %dx%d (supersample %dx), bot_dir=%s"
          % (W, H, SS, bot_dir or "-"))
    render()
    print("[render] raster done, downscaling")
    png = encode_png(downscale())
    if out_dir:
        target_dir = out_dir
    else:
        target_dir = os.path.join(".", "out")
    os.makedirs(target_dir, exist_ok=True)
    path = os.path.join(target_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)
    print("[render] wrote %s (%d bytes)" % (path, len(png)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
