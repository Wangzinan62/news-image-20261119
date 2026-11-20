#!/usr/bin/env python3
"""Draw the 19 November 2026 world-news front page as a 1024x1024 PNG.

Everything is drawn with PIL vector shapes and real Noto fonts -- no AI
image generation, so no text can come out garbled. Layout is measured with
PIL's own text metrics; every block asserts it stays inside its panel.

Layout: masthead -> huge date -> lead feature (left text, scales-of-justice
art right) -> five full-width story rows, each with a small icon at the
right -> dark ticker band at the bottom.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 28
CX0, CX1 = MARGIN, W - MARGIN          # content box: 28..996 (968 wide)
PAPER = (246, 241, 229)                # #f6f1e5
INK = (22, 24, 29)                     # #16181d
RED = (179, 49, 42)                    # #b3312a
NAVY = (36, 66, 92)                    # #24425c
CREAM = (246, 241, 229)

FONT_DIR = "/usr/share/fonts/truetype/noto/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF_BLACK = "NotoSerif-Black.ttf"
SERIF_BOLD = "NotoSerif-Bold.ttf"
SANS_BLACK = "NotoSans-Black.ttf"
SANS_BOLD = "NotoSans-Bold.ttf"
SANS_REG = "NotoSans-Regular.ttf"
COND_BOLD = "NotoSans-CondensedBold.ttf"


def wrap(draw, text, fnt, width):
    """Greedy word wrap measured with real glyph widths."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, text, fnt, lh, width, fill=INK):
    """Draw a wrapped left-aligned block; return the y just past it."""
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def hrule(draw, y, x0=CX0, x1=CX1, wdt=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=wdt)


# ---------------------------------------------------------------- icons
def icon_chip(d, x, y):
    """Computer chip with circuit pins, ~66x26 box at (x, y)."""
    d.rectangle([x + 2, y + 3, x + 30, y + 23], outline=NAVY, width=3)
    d.rectangle([x + 12, y + 9, x + 20, y + 17], fill=NAVY)
    for py in (7, 13, 19):
        d.line([(x - 6, y + py), (x + 2, y + py)], fill=NAVY, width=3)
        d.line([(x + 30, y + py), (x + 40, y + py)], fill=NAVY, width=3)
    d.line([(x + 40, y + 7), (x + 56, y + 7)], fill=NAVY, width=3)
    d.line([(x + 40, y + 19), (x + 50, y + 19), (x + 50, y + 24)],
           fill=NAVY, width=3)
    d.ellipse([x + 53, y + 4, x + 59, y + 10], fill=RED)


def icon_dish(d, x, y):
    """Probe / dish with signal arcs among stars, ~66x26 box."""
    d.arc([x, y + 2, x + 26, y + 26], start=300, end=120, fill=NAVY, width=3)
    d.line([(x + 13, y + 14), (x + 24, y + 4)], fill=NAVY, width=3)
    d.ellipse([x + 23, y + 2, x + 27, y + 6], fill=RED)
    d.line([(x + 8, y + 20), (x + 13, y + 13), (x + 18, y + 20)],
           fill=NAVY, width=3)
    for r in (7, 12):
        d.arc([x + 30, y - 2, x + 30 + 2 * r, y - 2 + 2 * r],
              start=270, end=360, fill=NAVY, width=2)
    for sx, sy in ((x + 52, y + 16), (x + 60, y + 6), (x + 46, y + 22)):
        d.line([(sx - 2, sy), (sx + 2, sy)], fill=NAVY, width=2)
        d.line([(sx, sy - 2), (sx, sy + 2)], fill=NAVY, width=2)


def icon_chart_down(d, x, y):
    """Plunging market chart: axes, descending line, red arrowhead."""
    d.line([(x, y + 26), (x + 62, y + 26)], fill=NAVY, width=3)
    d.line([(x, y), (x, y + 26)], fill=NAVY, width=3)
    pts = [(x + 4, y + 4), (x + 18, y + 8), (x + 30, y + 6),
           (x + 44, y + 16), (x + 56, y + 24)]
    d.line(pts, fill=RED, width=4, joint="curve")
    # arrowhead at the end of the fall
    d.polygon([(x + 56, y + 24), (x + 48, y + 20), (x + 52, y + 28)],
              fill=RED)


def icon_flags(d, x, y):
    """Three small summit flags (US / China / Russia) on poles."""
    pole_top, pole_bot = y + 2, y + 26
    for i, fx in enumerate((x + 2, x + 24, x + 46)):
        d.line([(fx, pole_top), (fx, pole_bot)], fill=INK, width=2)
    fx = x + 4
    d.rectangle([fx, pole_top, fx + 16, pole_top + 10], fill=RED)
    d.rectangle([fx, pole_top, fx + 7, pole_top + 5], fill=NAVY)
    fx = x + 26
    d.rectangle([fx, pole_top, fx + 16, pole_top + 10], fill=RED)
    d.ellipse([fx + 2, pole_top + 2, fx + 5, pole_top + 5], fill=CREAM)
    fx = x + 48
    d.rectangle([fx, pole_top, fx + 16, pole_top + 3], fill=(240, 240, 240))
    d.rectangle([fx, pole_top + 3, fx + 16, pole_top + 7], fill=NAVY)
    d.rectangle([fx, pole_top + 7, fx + 16, pole_top + 10], fill=RED)


def icon_eu(d, x, y):
    """EU circle of stars: navy ring with cream stars."""
    cx, cy = x + 30, y + 13
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=NAVY, width=3)
    for i in range(8):
        ang = math.radians(i * 45 - 90)
        sx, sy = cx + 8 * math.cos(ang), cy + 8 * math.sin(ang)
        d.line([(sx - 2, sy), (sx + 2, sy)], fill=NAVY, width=2)
        d.line([(sx, sy - 2), (sx, sy + 2)], fill=NAVY, width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)


# ---------------------------------------------------------------- lead art
def lead_art(d, x0, y0, x1, y1):
    """Scales of justice with court columns behind, in box (x0,y0)-(x1,y1)."""
    # fluted court columns at the back
    for cx in (x0 + 26, x0 + 96, x0 + 166):
        d.rectangle([cx - 12, y0 + 14, cx + 12, y1 - 8], fill=NAVY)
        d.rectangle([cx - 18, y0 + 6, cx + 18, y0 + 14], fill=NAVY)
        d.rectangle([cx - 18, y1 - 8, cx + 18, y1], fill=NAVY)
    # scales: central pillar, crossbeam, two hanging pans
    cx = (x0 + x1) // 2
    top, bot = y0 + 34, y1 - 6
    d.line([(cx, top), (cx, bot)], fill=INK, width=5)
    d.line([(cx - 78, top + 22), (cx + 78, top + 22)], fill=INK, width=5)
    d.ellipse([cx - 6, top - 8, cx + 6, top + 4], fill=RED)  # finial
    for sgn in (-1, 1):
        px = cx + sgn * 78
        d.line([(px, top + 22), (px - 26, top + 62)], fill=INK, width=3)
        d.line([(px, top + 22), (px + 26, top + 62)], fill=INK, width=3)
        d.line([(px, top + 22), (px, top + 62)], fill=INK, width=3)
        # pan: shallow bowl
        d.arc([px - 28, top + 52, px + 28, top + 82], start=0, end=180,
              fill=INK, width=4)
        d.line([(px - 28, top + 67), (px + 28, top + 67)], fill=INK, width=3)
    # base
    d.rectangle([cx - 46, bot, cx + 46, bot + 6], fill=INK)
    d.rectangle([cx - 30, bot - 10, cx + 30, bot], fill=INK)


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead ------------------------------------------------------
    hrule(d, 16, wdt=3)
    hrule(d, 22, wdt=1)
    d.text(((CX0 + CX1) / 2, 28), "THE WORLD IN ONE PICTURE",
           font=font(SERIF_BLACK, 30), fill=INK, anchor="ma")
    hrule(d, 70, wdt=2)

    # the date -- the single most important element ------------------
    d.text(((CX0 + CX1) / 2, 76), "THURSDAY",
           font=font(SERIF_BLACK, 76), fill=INK, anchor="ma")
    d.text(((CX0 + CX1) / 2, 152), "19 NOVEMBER 2026",
           font=font(SERIF_BOLD, 40), fill=RED, anchor="ma")
    hrule(d, 196, wdt=5)
    hrule(d, 205, wdt=1)

    # lead story ------------------------------------------------------
    lead_top, lead_bot = 217, 402
    d.text((40, lead_top + 6), "WORLD COURT",
           font=font(SANS_BOLD, 22), fill=RED)
    y = block(d, 40, lead_top + 36,
              "MYANMAR COMMITTED GENOCIDE, WORLD COURT RULES",
              font(SANS_BLACK, 32), 37, 700)
    y = block(d, 40, y + 6,
              "The International Court of Justice finds Myanmar responsible "
              "for genocide against the Rohingya in its 2017 clearance "
              "operations, in a 9–6 vote in Gambia v. Myanmar, and orders "
              "restitution.",
              font(SANS_REG, 19), 22, 700)
    assert y <= lead_bot, f"lead text overflows: {y} > {lead_bot}"
    lead_art(d, 762, lead_top + 4, 984, lead_bot - 4)
    hrule(d, 410, wdt=2)

    # five story rows -------------------------------------------------
    rows = [
        ("SUMMIT", "TRUMP, XI AND PUTIN ISSUE JOINT PEACE DECLARATION",
         "The three leaders sign a four-point 'Declaration toward Peace' "
         "on the APEC sidelines in Shenzhen, pledging nuclear-risk "
         "dialogue — but no major peace deal.", icon_flags),
        ("MARKETS", "DOW PLUNGES 1,100 AS SELL-OFF DEEPENS",
         "The Dow falls 2.2% to 49,097 and the S&P 500 drops for a sixth "
         "straight session as the AI-driven sell-off spreads.",
         icon_chart_down),
        ("TECH", "ANTHROPIC'S RECORD $81BN IPO DEBUTS",
         "The Claude maker's shares price at $83, open at $111.50 and "
         "close near $97 in the largest IPO ever.", icon_chip),
        ("EUROPE", "EU PROPOSES €45BN LOAN TO BACK UKRAINE",
         "Brussels unveils a €45 billion loan to support Ukraine as the "
         "war grinds on.", icon_eu),
        ("SCIENCE", "VOYAGER 1 PASSES ONE LIGHT-DAY FROM EARTH",
         "NASA's probe reaches about 16 billion miles from home, though "
         "a computer glitch is blocking its science data.", icon_dish),
    ]
    row_top, row_h = 420, 105
    for i, (kicker, head, deck, icon) in enumerate(rows):
        ry = row_top + i * row_h
        d.text((CX0, ry + 4), kicker, font=font(SANS_BOLD, 18), fill=RED)
        head_lines = wrap(d, head, font(SANS_BLACK, 28), 860)
        assert len(head_lines) == 1, f"row {kicker} headline wraps: {head_lines}"
        d.text((CX0, ry + 26), head, font=font(SANS_BLACK, 28), fill=INK)
        y = block(d, CX0, ry + 57, deck, font(SANS_REG, 18), 21, 860)
        assert y <= ry + row_h, f"row {kicker} overflows: {y} > {ry + row_h}"
        icon(d, CX1 - 70, ry + 34)
        if i < len(rows) - 1:
            hrule(d, ry + row_h - 2, wdt=1)

    # ticker -------------------------------------------------------------
    band_top, band_bot = 948, 1014
    d.rectangle([0, band_top, W, band_bot], fill=INK)
    ticker = ("ALSO TODAY · US Senate rejects Iran war-powers resolution "
              "51–48 · Trump posthumously pardons Pete Rose · Texans beat "
              "Colts 26–3 as Stroud throws 3 TDs")
    lines = wrap(d, ticker, font(COND_BOLD, 24), 940)
    assert len(lines) <= 2, f"ticker needs {len(lines)} lines"
    ty = band_top + (band_bot - band_top - len(lines) * 28) // 2
    for line in lines:
        d.text((W / 2, ty), line, font=font(COND_BOLD, 24), fill=CREAM,
               anchor="ma")
        ty += 28

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
