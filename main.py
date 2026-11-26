"""Render the 26 November 2026 world-news front page as one image.

Run with python3 main.py - writes out/entry.png next to this file.
Pure Pillow, deterministic, no network, no external assets.
"""

import os

from PIL import Image, ImageDraw

import content
import render as R

W, H = 1600, 2000
MARGIN = 72
CW = W - MARGIN * 2

PAPER = (247, 242, 230)
PANEL = (238, 230, 213)
INK = (24, 21, 18)
MUTED = (108, 99, 86)
RED = (178, 26, 30)
RED_DARK = (140, 18, 22)
DARK = (27, 24, 31)
CREAM = (247, 242, 230)
GOLD = (216, 164, 62)
TEAL = (18, 110, 110)


def masthead(d):
    y = 46
    R.rule(d, MARGIN, W - MARGIN, y, INK, 4)
    small = R.font("sans_bold", 25)
    d.text((MARGIN, y + 16), content.DATE_LINE, font=small, fill=INK)
    note = content.EDITION_NOTE
    d.text((W - MARGIN - R.text_width(d, note, small), y + 16), note, font=small, fill=MUTED)
    y += 66
    name_f = R.font("serif_black", 128)
    name = content.PAPER_NAME
    tw = R.text_width(d, name, name_f)
    d.text(((W - tw) / 2, y), name, font=name_f, fill=INK)
    y += 158
    tag_f = R.font("sans_bold", 30)
    tag = content.TAGLINE.upper()
    tw = R.tracked_width(d, tag, tag_f, 6)
    R.tracked_text(d, ((W - tw) / 2, y), tag, tag_f, RED, 6)
    y += 58
    R.rule(d, MARGIN, W - MARGIN, y, INK, 10)
    R.rule(d, MARGIN, W - MARGIN, y + 16, INK, 3)
    return y + 44


def lead(d, y):
    lead = content.LEAD
    chip_f = R.font("sans_black", 30)
    R.kicker_tag(d, (MARGIN, y), lead["kicker"], RED, CREAM, chip_f)
    y += 74
    head_f = R.font("serif_black", 108)
    y = R.draw_lines(d, (MARGIN, y), lead["headline"].split("\n"), head_f, INK, 116)
    y += 18
    col_w = 900
    stand_f = R.font("serif", 39)
    lines = R.wrap(d, lead["standfirst"], stand_f, col_w)
    y_text = R.draw_lines(d, (MARGIN, y), lines, stand_f, (52, 47, 40), 50)
    y_text += 14
    bullet_f = R.font("sans", 30)
    for point in lead["points"]:
        wrapped = R.wrap(d, point, bullet_f, col_w - 44)
        d.text((MARGIN + 4, y_text + 4), "\u25aa", font=R.font("sans_bold", 30), fill=RED)
        y_text = R.draw_lines(d, (MARGIN + 44, y_text), wrapped, bullet_f, INK, 40)
        y_text += 8
    panel_x = MARGIN + col_w + 44
    panel_w = W - MARGIN - panel_x
    d.rectangle([panel_x, y, W - MARGIN, y_text], fill=DARK)
    num_f = R.font("serif_black", 170)
    num = lead["big_number"]
    tw = R.text_width(d, num, num_f)
    d.text((panel_x + (panel_w - tw) / 2, y + 6), num, font=num_f, fill=GOLD)
    lab_f = R.font("sans_bold", 29)
    ly = y + 196
    for line in lead["big_label"].split("\n"):
        tw = R.text_width(d, line, lab_f)
        d.text((panel_x + (panel_w - tw) / 2, ly), line, font=lab_f, fill=CREAM)
        ly += 38
    R.tariff_bars(d, (panel_x + 36, ly + 18, W - MARGIN - 36, y_text - 26), GOLD, (96, 88, 70))
    return y_text + 40


def story_cell(d, x, y, w, story):
    chip_f = R.font("sans_black", 24)
    R.kicker_tag(d, (x, y), story["kicker"], INK, CREAM, chip_f, pad_x=11, pad_y=6, tracking=2)
    icon_x = x + w - 52
    if story["accent"] == "oil":
        R.draw_drop(d, icon_x, y + 24, 26, RED)
    elif story["accent"] == "fire":
        R.draw_flame(d, icon_x, y + 16, 26, RED)
    elif story["accent"] == "eu":
        R.draw_stars_circle(d, icon_x, y + 24, 27, TEAL)
    else:
        R.draw_orbit(d, icon_x, y + 24, 34, TEAL, RED)
    y += 66
    head_f = R.font("serif_bold", 45)
    y = R.draw_lines(d, (x, y), story["headline"].split("\n"), head_f, INK, 54)
    y += 8
    body_f = R.font("sans", 29)
    lines = R.wrap(d, story["body"], body_f, w)
    y = R.draw_lines(d, (x, y), lines, body_f, (56, 51, 44), 39)
    return y


def story_grid(d, y):
    gap = 56
    col_w = (CW - gap) // 2
    R.rule(d, MARGIN, W - MARGIN, y, INK, 3)
    y += 30
    row1 = max(
        story_cell(d, MARGIN, y, col_w, content.STORIES[0]),
        story_cell(d, MARGIN + col_w + gap, y, col_w, content.STORIES[1]),
    )
    y = row1 + 28
    R.rule(d, MARGIN, W - MARGIN, y, MUTED, 2)
    y += 28
    row2 = max(
        story_cell(d, MARGIN, y, col_w, content.STORIES[2]),
        story_cell(d, MARGIN + col_w + gap, y, col_w, content.STORIES[3]),
    )
    mid = MARGIN + col_w + gap // 2
    R.rule_vertical(d, mid, 0, 0, INK, 0) if hasattr(R, "rule_vertical") else None
    return row2 + 34


def markets(d, y):
    m = content.MARKETS
    d.rectangle([MARGIN, y, W - MARGIN, y + 252], fill=DARK)
    x = MARGIN + 40
    chip_f = R.font("sans_black", 24)
    R.kicker_tag(d, (x, y + 28), m["kicker"], GOLD, DARK, chip_f, pad_x=11, pad_y=6, tracking=2)
    head_f = R.font("serif_bold", 47)
    lines = R.wrap(d, m["headline"], head_f, 950)
    yy = R.draw_lines(d, (x, y + 82), lines, head_f, CREAM, 56)
    body_f = R.font("sans", 28)
    blines = R.wrap(d, m["body"], body_f, 950)
    yy = R.draw_lines(d, (x, yy + 6), blines, body_f, (205, 198, 182), 37)
    R.sparkline_down(d, (W - MARGIN - 330, y + 52, W - MARGIN - 50, y + 150), (240, 110, 100))
    stat_f = R.font("sans_black", 30)
    lab_f = R.font("sans_bold", 21)
    sx = x
    for label, value in m["stats"]:
        d.text((sx, y + 196), value, font=stat_f, fill=GOLD if "+" in value or value == "50,000+" else (240, 130, 120))
        d.text((sx, y + 168), label, font=lab_f, fill=(168, 160, 146))
        sx += R.text_width(d, value, stat_f) + 74
    return y + 252 + 34


def ticker(d, y):
    items = "   ///   ".join(content.TICKER)
    d.rectangle([MARGIN, y, W - MARGIN, y + 118], fill=RED)
    lab_f = R.font("sans_black", 26)
    d.rectangle([MARGIN, y, MARGIN + 196, y + 118], fill=RED_DARK)
    tw = R.tracked_width(d, "ALSO", lab_f, 3)
    R.tracked_text(d, (MARGIN + (196 - tw) / 2, y + 26), "ALSO", lab_f, CREAM, 3)
    tw = R.tracked_width(d, "TODAY", lab_f, 3)
    R.tracked_text(d, (MARGIN + (196 - tw) / 2, y + 62), "TODAY", lab_f, CREAM, 3)
    body_f = R.font("sans_bold", 27)
    lines = R.wrap(d, items, body_f, CW - 196 - 68)
    yy = y + 20
    for line in lines[:2]:
        d.text((MARGIN + 228, yy), line, font=body_f, fill=CREAM)
        yy += 40
    return y + 118 + 26


def footer(d, y):
    f = R.font("sans", 24)
    text = content.FOOTER
    tw = R.text_width(d, text, f)
    d.text(((W - tw) / 2, y), text, font=f, fill=MUTED)
    R.rule(d, MARGIN, W - MARGIN, y + 44, INK, 4)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = masthead(d)
    y = lead(d, y)
    R.rule(d, MARGIN, W - MARGIN, y, INK, 3)
    y = story_grid(d, y + 6)
    y = markets(d, y)
    y = ticker(d, y)
    footer(d, y)
    return img


def main():
    img = build()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG")
    print("wrote", path, img.size)


if __name__ == "__main__":
    main()
