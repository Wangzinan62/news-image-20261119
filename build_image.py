#!/usr/bin/env python3
"""Draw the 19 November 2026 front page: 'The World in One Picture'.

A broadsheet-style newspaper front page rendered entirely with PIL shapes
and text (no generated imagery, so every letter stays crisp). Run it and it
writes entry.png next to this file.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "entry.png")

PAGE_W, PAGE_H = 1024, 1024
PAPER = (246, 241, 229)   # #f6f1e5
INK = (22, 24, 29)       # #16181d
RED = (179, 49, 42)      # #b3312a
NAVY = (36, 66, 92)      # #24425c
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/noto"

SERIF_BLACK = os.path.join(FONT_DIR, "NotoSerif-Black.ttf")
SANS_BLACK = os.path.join(FONT_DIR, "NotoSans-Black.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")

MARGIN = 28
TEXT_W = PAGE_W - 2 * MARGIN          # 968, full-width text column
ICON_W = 78                           # reserved strip at the right of rows
ROW_TEXT_W = TEXT_W - ICON_W - 12     # text width inside a story row


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_lines(draw, text, font, max_width, limit):
    """Wrap text and clip to at most `limit` lines."""
    return wrap_text(draw, text, font, max_width)[:limit]


def double_rule(draw, y, x0=MARGIN, x1=PAGE_W - MARGIN, gap=6):
    draw.line([(x0, y), (x1, y)], fill=INK, width=2)
    draw.line([(x0, y + gap), (x1, y + gap)], fill=INK, width=1)


def single_rule(draw, y, x0=MARGIN, x1=PAGE_W - MARGIN):
    draw.line([(x0, y), (x1, y)], fill=INK, width=1)


def centered(draw, y, text, font, fill):
    w = draw.textlength(text, font=font)
    draw.text(((PAGE_W - w) / 2, y), text, font=font, fill=fill)


# ---------------------------------------------------------------- icons

def draw_flags(draw, cx, cy):
    """Three small flags on poles, for the summit story."""
    colours = [RED, NAVY, RED]
    for i, colour in enumerate(colours):
        x = cx - 30 + i * 30
        draw.line([(x, cy - 16), (x, cy + 20)], fill=INK, width=2)
        draw.rectangle([x, cy - 16, x + 24, cy - 2], fill=colour)
        draw.line([(x, cy - 2), (x + 24, cy - 2)], fill=WHITE, width=2)


def draw_chart(draw, cx, cy):
    """A plunging line chart, for the markets story."""
    x0, y0 = cx - 32, cy - 18
    draw.line([(x0, y0 + 34), (x0 + 64, y0 + 34)], fill=NAVY, width=2)
    draw.line([(x0, y0 + 34), (x0, y0)], fill=NAVY, width=2)
    pts = [(x0 + 4, y0 + 6), (x0 + 18, y0 + 10), (x0 + 30, y0 + 9),
           (x0 + 42, y0 + 20), (x0 + 54, y0 + 26), (x0 + 62, y0 + 30)]
    draw.line(pts, fill=RED, width=3, joint="curve")
    draw.ellipse([pts[-1][0] - 3, pts[-1][1] - 3,
                  pts[-1][0] + 3, pts[-1][1] + 3], fill=RED)


def draw_chip(draw, cx, cy):
    """A computer chip, for the tech story."""
    draw.rectangle([cx - 22, cy - 16, cx + 22, cy + 16],
                   outline=NAVY, width=3)
    draw.rectangle([cx - 10, cy - 8, cx + 10, cy + 8],
                   outline=NAVY, width=2)
    for dx in (-14, 0, 14):
        draw.line([(cx + dx, cy - 24), (cx + dx, cy - 16)], fill=NAVY, width=2)
        draw.line([(cx + dx, cy + 16), (cx + dx, cy + 24)], fill=NAVY, width=2)
    for dy in (-8, 8):
        draw.line([(cx - 30, cy + dy), (cx - 22, cy + dy)], fill=NAVY, width=2)
        draw.line([(cx + 22, cy + dy), (cx + 30, cy + dy)], fill=NAVY, width=2)
    draw.ellipse([cx + 14, cy - 20, cx + 20, cy - 14], fill=RED)


def draw_star_circle(draw, cx, cy):
    """A ring of twelve stars (small dots), for the Europe story."""
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        x = cx + 20 * math.cos(a)
        y = cy + 20 * math.sin(a)
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=NAVY)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)


def draw_dish(draw, cx, cy):
    """A satellite dish beaming a signal, for the science story."""
    draw.arc([cx - 30, cy - 26, cx + 6, cy + 10], start=270, end=90,
             fill=NAVY, width=4)
    draw.line([(cx - 12, cy - 8), (cx + 10, cy + 10)], fill=NAVY, width=3)
    draw.line([(cx - 2, cy + 16), (cx + 14, cy + 16)], fill=NAVY, width=3)
    for r in (16, 24):
        draw.arc([cx + 2, cy - 22 - r, cx + 2 + 2 * r, cy - 22 + r],
                 start=300, end=60, fill=RED, width=2)


def draw_scales(draw, x0, y0, x1, y1):
    """Scales of justice standing between two navy columns."""
    # Two columns with capitals and bases.
    col_w = 26
    for cx in (x0 + 8, x1 - 8 - col_w):
        draw.rectangle([cx, y0, cx + col_w, y1 - 14], fill=NAVY)
        draw.rectangle([cx - 5, y0, cx + col_w + 5, y0 + 8], fill=NAVY)
        draw.rectangle([cx - 5, y1 - 22, cx + col_w + 5, y1 - 14], fill=NAVY)
    mid = (x0 + x1) // 2
    # Central post, beam and pans.
    draw.line([(mid, y0 + 26), (mid, y1 - 26)], fill=INK, width=4)
    draw.line([(mid - 62, y0 + 34), (mid + 62, y0 + 34)], fill=INK, width=3)
    draw.ellipse([mid - 5, y0 + 18, mid + 5, y0 + 28], fill=RED)
    for end in (mid - 62, mid + 62):
        draw.line([(end, y0 + 34), (end - 20, y0 + 62)], fill=INK, width=2)
        draw.line([(end, y0 + 34), (end + 20, y0 + 62)], fill=INK, width=2)
        draw.line([(end - 20, y0 + 62), (end + 20, y0 + 62)], fill=INK, width=2)
        draw.arc([end - 20, y0 + 48, end + 20, y0 + 76], start=0, end=180,
                 fill=INK, width=2)
    draw.rectangle([mid - 30, y1 - 26, mid + 30, y1 - 14], fill=INK)


# ---------------------------------------------------------------- page

def build():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(img)

    masthead_f = load(SERIF_BLACK, 36)
    weekday_f = load(SERIF_BLACK, 92)
    date_f = load(SERIF_BLACK, 40)
    kicker_f = load(SANS_BOLD, 18)
    lead_head_f = load(SANS_BLACK, 42)
    head_f = load(SANS_BLACK, 34)
    deck_f = load(SANS_BOLD, 18)
    lead_deck_f = load(SANS_BOLD, 19)
    ticker_f = load(SANS_BOLD, 20)

    # ---- header: double rule, masthead, weekday, red date, double rule
    double_rule(draw, 10)
    centered(draw, 22, "THE WORLD IN ONE PICTURE", masthead_f, INK)
    single_rule(draw, 64)
    centered(draw, 70, "THURSDAY", weekday_f, INK)
    centered(draw, 166, "19 NOVEMBER 2026", date_f, RED)
    double_rule(draw, 214)

    # ---- lead story
    lead_top = 232
    lead_text_w = 700
    draw.text((MARGIN, lead_top), "WORLD COURT", font=kicker_f, fill=RED)
    lead_head = ["MYANMAR COMMITTED GENOCIDE,", "WORLD COURT RULES"]
    hy = lead_top + 24
    for line in lead_head:
        draw.text((MARGIN, hy), line, font=lead_head_f, fill=INK)
        hy += 44
    lead_deck = ("The International Court of Justice finds Myanmar "
                 "responsible for genocide against the Rohingya in its "
                 "2017 clearance operations, in a 9–6 vote in Gambia v. "
                 "Myanmar, and orders restitution.")
    dy = hy + 4
    for line in fit_lines(draw, lead_deck, lead_deck_f, lead_text_w, 3):
        draw.text((MARGIN, dy), line, font=lead_deck_f, fill=INK)
        dy += 23
    draw_scales(draw, 790, lead_top + 4, 996, lead_top + 178)
    single_rule(draw, 420)

    # ---- five story rows
    stories = [
        ("SUMMIT", "TRUMP, XI AND PUTIN ISSUE JOINT PEACE DECLARATION",
         "The three leaders sign a four-point 'Declaration toward Peace' "
         "on the APEC sidelines in Shenzhen, pledging nuclear-risk "
         "dialogue — but no major peace deal.", draw_flags, True),
        ("MARKETS", "DOW PLUNGES 1,100 AS SELL-OFF DEEPENS",
         "The Dow falls 2.2% to 49,097 and the S&P 500 drops for a sixth "
         "straight session as the AI-driven sell-off spreads.", draw_chart,
         False),
        ("TECH", "ANTHROPIC'S RECORD $81BN IPO DEBUTS",
         "The Claude maker's shares price at $83, open at $111.50 and "
         "close near $97 in the largest IPO ever.", draw_chip, False),
        ("EUROPE", "EU PROPOSES €45BN LOAN TO BACK UKRAINE",
         "Brussels unveils a €45 billion loan to support Ukraine as the "
         "war grinds on.", draw_star_circle, False),
        ("SCIENCE", "VOYAGER 1 PASSES ONE LIGHT-DAY FROM EARTH",
         "NASA's probe reaches about 16 billion miles from home, though "
         "a computer glitch is blocking its science data.", draw_dish,
         False),
    ]

    y = 428
    for kicker, headline, deck, icon, two_line_head in stories:
        draw.text((MARGIN, y), kicker, font=kicker_f, fill=RED)
        if two_line_head:
            # The summit headline is too long for one 34px line, so it
            # takes two lines and this row gets extra height.
            parts = ["TRUMP, XI AND PUTIN ISSUE", "JOINT PEACE DECLARATION"]
            hy2 = y + 21
            for line in parts:
                draw.text((MARGIN, hy2), line, font=head_f, fill=INK)
                hy2 += 35
            dy2 = hy2 + 6
            row_h = 138
        else:
            draw.text((MARGIN, y + 21), headline, font=head_f, fill=INK)
            dy2 = y + 58
            row_h = 100
        for line in fit_lines(draw, deck, deck_f, ROW_TEXT_W, 2):
            draw.text((MARGIN, dy2), line, font=deck_f, fill=INK)
            dy2 += 20
        icon_cx = PAGE_W - MARGIN - 38
        icon_cy = y + row_h // 2
        icon(draw, icon_cx, icon_cy)
        y += row_h
        single_rule(draw, y)

    # ---- bottom ticker band
    band_top = y + 4
    draw.rectangle([0, band_top, PAGE_W, PAGE_H], fill=NAVY)
    ticker = ("ALSO TODAY · US Senate rejects Iran war-powers resolution "
              "51–48 · Trump posthumously pardons Pete Rose · Texans beat "
              "Colts 26–3 as Stroud throws 3 TDs")
    ty = band_top + 6
    for line in fit_lines(draw, ticker, ticker_f, TEXT_W, 2):
        centered(draw, ty, line, ticker_f, WHITE)
        ty += 24

    img.save(OUT_PATH, "PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    print(f"Wrote {OUT_PATH}: {img.size[0]}x{img.size[1]}, {size} bytes")
    assert size <= 1_048_576, f"entry.png too large: {size} bytes"


if __name__ == "__main__":
    build()
