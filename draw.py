#!/usr/bin/env python3
"""Ember Strait - news-image-20261125 renderer.

Draws a one-page newspaper front page summing up Wednesday
25 November 2026: 35 dated stories across six regions, a UTC
timeline, certainty tags, drawn scenes, a schematic world map
with numbered pins, and a date-check box for Tuesday's stories.

Original code written fresh for this entry. Pillow only.
Run:  python3 draw.py   (writes entry.png next to this file)
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "entry.png")

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 14
LEFT = MARGIN
RIGHT = PAGE_W - MARGIN
CONTENT_W = RIGHT - LEFT

# ---- palette (my own scheme) ----
PAPER = (246, 241, 229)        # warm newsprint
PAPER_SOFT = (238, 231, 214)   # slightly darker panel
INK = (28, 28, 44)             # near-black navy ink
INK_SOFT = (74, 74, 88)        # grey ink for secondary text
RED = (163, 22, 33)            # accent red
RED_SOFT = (253, 240, 239)     # date-check fill
TEAL = (15, 76, 92)            # deep teal
GOLD = (183, 121, 31)          # gold accent
GREEN = (30, 125, 50)          # CONFIRMED
BLUE = (21, 101, 192)          # REPORTED
ORANGE = (230, 81, 0)          # CLAIM
GREY = (97, 97, 97)            # PENDING
SEA = (220, 232, 236)          # map ocean
LAND = (232, 220, 192)         # map land
LAND_LINE = (176, 148, 96)     # map land outline
NIGHT = (13, 27, 62)           # night-scene sky
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

TAG_FILL = {
    "CONFIRMED": GREEN,
    "REPORTED": BLUE,
    "CLAIM": ORANGE,
    "ONGOING": RED,
    "PENDING": GREY,
}

REGION_FILL = {
    "EUROPE": (31, 78, 121),
    "MIDDLE EAST": (163, 22, 33),
    "ASIA-PACIFIC": (15, 76, 92),
    "AMERICAS": (46, 125, 50),
    "AFRICA": (183, 121, 31),
    "OCEANIA": (106, 27, 154),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _load(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except Exception:
        return ImageFont.load_default()


def serif(size, bold=False):
    return _load("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf", size)


def sans(size, bold=False):
    return _load("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)


def wrap(text, font, width):
    """Split text into lines that fit inside width (pixels)."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if font.getlength(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def para(draw, x, y, lines, font, fill, leading):
    """Draw a list of lines; return the y below the last line."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def hline(draw, x0, x1, y, fill=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vline(draw, x, y0, y1, fill=INK, width=1):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


def tag_chip(draw, x, y, label):
    """Draw a small coloured certainty tag; return its width."""
    font = sans(8, True)
    pad = 5
    text_w = int(font.getlength(label))
    w = text_w + pad * 2
    h = 13
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3,
                           fill=TAG_FILL.get(label, GREY))
    draw.text((x + pad, y + 2), label, font=font, fill=WHITE)
    return w


def rx(box, fx):
    x0, _y0, x1, _y1 = box
    return x0 + fx * (x1 - x0)


def ry(box, fy):
    _x0, y0, _x1, y1 = box
    return y0 + fy * (y1 - y0)


def point(box, fx, fy):
    return (rx(box, fx), ry(box, fy))


# ---- the day's data (all dated Wednesday 25 November 2026) ----

STATS = [
    ("2", "tankers hit by mines in Hormuz"),
    ("-6.16%", "KOSPI plunge in Seoul"),
    ("19", "civilians killed in Sudan strikes"),
    ("€115bn", "Ukraine aid ask for 2027"),
    ("4.0%", "eurozone inflation"),
    ("4.9%", "Australia October inflation"),
]

REGIONS = [
    ("EUROPE", 9),
    ("MIDDLE EAST", 4),
    ("ASIA-PACIFIC", 5),
    ("AMERICAS", 12),
    ("AFRICA", 3),
    ("OCEANIA", 2),
]

TIMELINE = [
    "04:56 UTC Shenzhou-24 docks",
    "Tankers hit mines in Hormuz",
    "KOSPI -6.16%",
    "Treaty signed in Canberra",
    "PCE 3.8% in line",
    "Tariff plan reported",
]

# (number, tag, place, region line, headline, body, source, scene kind)
HEROES = [
    ("1", "ONGOING", "STRAIT OF HORMUZ", "MIDDLE EAST · SHIPPING",
     "Tankers hit mines and burn in the Strait of Hormuz",
     "Iran's Revolutionary Guard says the tankers struck mines early "
     "Wednesday; crews fight the fires.",
     "IRGC · Reuters", "tanker"),
    ("2", "CONFIRMED", "SEOUL", "ASIA-PACIFIC · MARKETS",
     "KOSPI plunges 6.16% as Asia's AI rally unravels",
     "Samsung -9.9%, SK Hynix -11.1%; Nikkei -2.78%, Taiex ~-5% "
     "as AI-trade doubts spread.",
     "Dow Jones · Morningstar", "chart"),
    ("3", "REPORTED", "SAMARA, RUSSIA", "EUROPE · WAR",
     "Ukrainian drones set two Rosneft refineries ablaze",
     "Syzran and Kuibyshev hit overnight; one person killed and "
     "145 drones downed, Moscow says.",
     "Reuters · officials", "refinery"),
]

# (number, tag, place, headline, body, source, scene kind)
CARDS = [
    ("4", "CLAIM", "RAS TANURA",
     "Houthis claim strike on Ras Tanura refinery",
     "Yemen's Houthis say they hit the Saudi refinery; Riyadh has "
     "not confirmed.",
     "Houthi statement", "flame"),
    ("5", "REPORTED", "GAZA",
     "Israel kills Hamas security chief Abuelouf",
     "The colonel, his wife and two children die in a strike, "
     "Gaza medics say.",
     "Gaza officials · medics", "city"),
    ("6", "REPORTED", "SUDAN",
     "RSF drone strikes kill 19 civilians in Sudan",
     "19 dead, 20 wounded in two cities, Emergency Lawyers say.",
     "Emergency Lawyers", "desert"),
    ("7", "CONFIRMED", "BOGOR, INDONESIA",
     "Bogor mine flood toll reaches 6; ~20 trapped",
     "Three more bodies recovered Wednesday from the flooded "
     "illegal gold mine.",
     "Reuters", "mine"),
    ("8", "CONFIRMED", "CANBERRA",
     "Australia-Solomons sign security treaty",
     "The pact bars foreign military bases on the islands.",
     "AAP · Reuters", "treaty"),
    ("9", "CONFIRMED", "TIANGONG",
     "Shenzhou-24 docks; Pakistan's first astronaut in orbit",
     "Docking at 04:56 UTC, 3.5 hours after launch; a new crew "
     "for China.",
     "China Manned Space Agency", "rocket"),
    ("10", "CONFIRMED", "CARTAGENA, COLOMBIA",
     "All hostages freed in Cartagena supermarket siege",
     "Troops storm the store at dawn; one captor killed, the "
     "rest freed.",
     "Reuters · Colombia officials", "store"),
    ("11", "CONFIRMED", "WASHINGTON",
     "US inflation 3.8% - in line, before the Fed meets",
     "October PCE up 0.3% on the month; last read before December.",
     "Investopedia · BEA", "inflation"),
    ("12", "REPORTED", "WASHINGTON",
     "White House plans tariff hikes on China, dozens more",
     "WSJ reports a new round of increases as the US-China "
     "truce frays.",
     "Wall Street Journal", "tariff"),
    ("13", "CONFIRMED", "DAKAR",
     "CAS hands Senegal back its Africa Cup title",
     "Sport's top court rules for Senegal; Morocco vows to "
     "challenge.",
     "CAS · Reuters", "trophy"),
]

# (number, one-line summary) - stories 14 to 35
ALSO = [
    ("14", "Odesa — Russian strike kills 2, injures 3"),
    ("15", "Benghazi — Libya vows retaliation after officers killed"),
    ("16", "Kyiv — Zelenskyy: Ukraine needs €115bn aid for 2027"),
    ("17", "Washington — US defence chief pauses Patriot supplies"),
    ("18", "Warsaw — Poland pushes permanent US presence"),
    ("19", "Frankfurt — Eurozone inflation rises to 4.0%"),
    ("20", "Vatican — Pope Leo: COP31 failure a worry"),
    ("21", "Basel — Roche breast cancer pill wins 2nd FDA nod"),
    ("22", "Luton — EasyJet profit falls 89% on £244m fuel hit"),
    ("23", "Seattle — Amazon buys Decart to chase Nvidia in chips"),
    ("24", "Seattle — Hackers' AI agents broke into a university server"),
    ("25", "New York — Anthropic falls below IPO price; $1tn gone"),
    ("26", "Madrid — Abrego Garcia leaves US, reportedly for Spain"),
    ("27", "Caracas — Venezuela reveals $237bn debt load"),
    ("28", "Sydney — Australia's October inflation 4.9%; RBA on alert"),
    ("29", "Tokyo — Nikkei -2.78%; SoftBank -14.8% in AI sell-off"),
    ("30", "Taipei — Taiex falls ~5% as Asia's chip stocks slide"),
    ("31", "New York — Nasdaq futures -2.8% before Thanksgiving"),
    ("32", "Ottawa — Bank of Canada: inflation to stay persistent"),
    ("33", "Santiago — Chile's copper miners miss out on price surge"),
    ("34", "New York — Musk gains most from SpaceX-Tesla deal"),
    ("35", "Gulf — Oil climbs as Hormuz attack lifts WTI to $82.51"),
]

DATE_CHECK = (
    "Left out — they happened on Tuesday 24 Nov: Arsenal 1-1 Dortmund, "
    "Real Madrid 5-1 PSV, Man City 2-2 Napoli, Galatasaray 1-0 Aston "
    "Villa · Huawei convicted on 10 of 12 counts · Dell's record Q3: "
    "$54.9bn revenue, $22bn AI servers · Dow first close above 50,000 "
    "(50,018.70) · Houthi drone on Riyadh tower injures 11."
)

LEGEND = ("HOW TO READ THE TAGS — CONFIRMED official or 2+ outlets · "
          "REPORTED one source's account · CLAIM one side's claim, "
          "contested · ONGOING still developing · PENDING not settled yet")

SOURCES = ("Sources: Reuters, BBC, AP, Al Jazeera, AAP, Dow Jones, WSJ, "
           "Investopedia. Scenes are drawn illustrations, not photographs.")


# ---- drawn scenes (one small illustration per story) ----

def paint_scene(draw, box, kind):
    """Paint a small drawn scene inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    cx = x0 + w // 2

    if kind == "tanker":
        draw.rectangle(box, fill=NIGHT)
        draw.ellipse([x0 + int(w * 0.80), y0 + int(h * 0.10),
                      x0 + int(w * 0.90), y0 + int(h * 0.32)],
                     fill=(240, 235, 200))
        draw.rectangle([x0, y0 + int(h * 0.62), x1, y1], fill=(20, 42, 72))
        draw.line([(x0, y0 + int(h * 0.62)), (x1, y0 + int(h * 0.62))],
                  fill=(120, 160, 200), width=2)
        # hull
        draw.polygon([(x0 + int(w * 0.06), y0 + int(h * 0.52)),
                      (x0 + int(w * 0.94), y0 + int(h * 0.52)),
                      (x0 + int(w * 0.88), y0 + int(h * 0.68)),
                      (x0 + int(w * 0.12), y0 + int(h * 0.68))],
                     fill=(35, 35, 48))
        # superstructure + funnel
        draw.rectangle([x0 + int(w * 0.62), y0 + int(h * 0.34),
                        x0 + int(w * 0.76), y0 + int(h * 0.52)],
                       fill=(220, 220, 210))
        draw.rectangle([x0 + int(w * 0.20), y0 + int(h * 0.40),
                        x0 + int(w * 0.26), y0 + int(h * 0.52)],
                       fill=(200, 60, 40))
        # flames on deck
        for fx, fh in ((0.30, 0.30), (0.45, 0.38)):
            bx = x0 + int(w * fx)
            by = y0 + int(h * 0.52)
            draw.polygon([(bx - 12, by), (bx + 12, by),
                          (bx, by - int(h * fh))], fill=(255, 140, 0))
            draw.polygon([(bx - 6, by), (bx + 6, by),
                          (bx, by - int(h * fh * 0.55))],
                         fill=(255, 220, 60))
        # smoke
        for sx, sy, sr in ((0.30, 0.16, 7), (0.36, 0.10, 9),
                           (0.45, 0.12, 8), (0.50, 0.06, 6)):
            draw.ellipse([x0 + int(w * sx) - sr, y0 + int(h * sy) - sr,
                          x0 + int(w * sx) + sr, y0 + int(h * sy) + sr],
                         fill=(150, 150, 150))
        # wave lines
        for wy in (0.74, 0.84, 0.94):
            yy = y0 + int(h * wy)
            draw.line([(x0 + 6, yy), (x0 + int(w * 0.30), yy),
                       (x0 + int(w * 0.38), yy - 3),
                       (x0 + int(w * 0.62), yy),
                       (x0 + int(w * 0.70), yy - 3),
                       (x0 + int(w * 0.94), yy)], fill=(120, 170, 210))

    elif kind == "chart":
        draw.rectangle(box, fill=(243, 234, 210))
        for gy in (0.25, 0.50, 0.75):
            yy = y0 + int(h * gy)
            draw.line([(x0 + 8, yy), (x1 - 8, yy)], fill=(210, 198, 168))
        heights = (0.55, 0.48, 0.38, 0.28, 0.16)
        bw = int(w * 0.13)
        for i, hh in enumerate(heights):
            bx0 = x0 + int(w * 0.08) + i * int(w * 0.18)
            draw.rectangle([bx0, y0 + int(h * (0.85 - hh)),
                            bx0 + bw, y0 + int(h * 0.85)],
                           fill=(178, 34, 34))
        draw.line([(x0 + int(w * 0.10), y0 + int(h * 0.22)),
                   (x0 + int(w * 0.90), y0 + int(h * 0.68))],
                  fill=(163, 22, 33), width=3)
        ax, ay = x0 + int(w * 0.90), y0 + int(h * 0.68)
        draw.polygon([(ax, ay), (ax - 12, ay - 2), (ax - 4, ay - 12)],
                     fill=(163, 22, 33))
        draw.text((x0 + int(w * 0.06), y0 + int(h * 0.04)), "-6.16%",
                  font=sans(13, True), fill=(163, 22, 33))

    elif kind == "refinery":
        draw.rectangle(box, fill=NIGHT)
        for sx, sy in ((0.08, 0.12), (0.22, 0.06), (0.45, 0.14),
                       (0.68, 0.08), (0.88, 0.16), (0.95, 0.05)):
            draw.ellipse([x0 + int(w * sx) - 1, y0 + int(h * sy) - 1,
                          x0 + int(w * sx) + 1, y0 + int(h * sy) + 1],
                         fill=WHITE)
        draw.rectangle([x0, y0 + int(h * 0.78), x1, y1], fill=(24, 24, 34))
        # towers
        for tx, tw, th in ((0.10, 0.10, 0.42), (0.30, 0.12, 0.55),
                           (0.55, 0.10, 0.46)):
            bx0 = x0 + int(w * tx)
            draw.rectangle([bx0, y0 + int(h * (0.78 - th)),
                            bx0 + int(w * tw), y0 + int(h * 0.78)],
                           fill=(70, 70, 84))
            draw.line([(bx0 - 3, y0 + int(h * (0.78 - th * 0.6))),
                       (bx0 + int(w * tw) + 3,
                        y0 + int(h * (0.78 - th * 0.6)))],
                      fill=(110, 110, 130), width=2)
        # chimney + flame
        chx = x0 + int(w * 0.78)
        draw.rectangle([chx, y0 + int(h * 0.18), chx + int(w * 0.06),
                        y0 + int(h * 0.78)], fill=(90, 90, 104))
        draw.polygon([(chx - 4, y0 + int(h * 0.18)),
                      (chx + int(w * 0.06) + 4, y0 + int(h * 0.18)),
                      (chx + int(w * 0.03), y0 + int(h * 0.02))],
                     fill=(255, 160, 0))
        # drone dots
        for dx, dy in ((0.18, 0.30), (0.48, 0.22), (0.70, 0.34)):
            draw.ellipse([x0 + int(w * dx) - 2, y0 + int(h * dy) - 2,
                          x0 + int(w * dx) + 2, y0 + int(h * dy) + 2],
                         fill=(255, 220, 60))

    elif kind == "flame":
        draw.rectangle(box, fill=(58, 32, 20))
        draw.rectangle([x0, y0 + int(h * 0.55), x1, y1], fill=(38, 24, 16))
        draw.rectangle([x0 + int(w * 0.12), y0 + int(h * 0.42),
                        x0 + int(w * 0.88), y0 + int(h * 0.78)],
                       fill=(90, 78, 70))
        for fx in (0.28, 0.50, 0.70):
            bx = x0 + int(w * fx)
            by = y0 + int(h * 0.44)
            draw.polygon([(bx - 10, by), (bx + 10, by),
                          (bx, by - int(h * 0.30))], fill=(255, 140, 0))
            draw.polygon([(bx - 5, by), (bx + 5, by),
                          (bx, by - int(h * 0.16))], fill=(255, 220, 60))
        draw.ellipse([x0 + int(w * 0.42) - 8, y0 + int(h * 0.10) - 8,
                      x0 + int(w * 0.42) + 8, y0 + int(h * 0.10) + 8],
                     fill=(200, 200, 200))
        draw.ellipse([x0 + int(w * 0.58) - 6, y0 + int(h * 0.06) - 6,
                      x0 + int(w * 0.58) + 6, y0 + int(h * 0.06) + 6],
                     fill=(180, 180, 180))

    elif kind == "city":
        draw.rectangle(box, fill=(214, 222, 228))
        draw.rectangle([x0, y0 + int(h * 0.80), x1, y1], fill=(120, 128, 136))
        for bx, bw, bh in ((0.06, 0.20, 0.55), (0.32, 0.24, 0.68),
                           (0.62, 0.20, 0.48)):
            x = x0 + int(w * bx)
            draw.rectangle([x, y0 + int(h * (0.80 - bh)),
                            x + int(w * bw), y0 + int(h * 0.80)],
                           fill=(96, 104, 116))
            for wy in range(3):
                for wx in range(2):
                    draw.rectangle(
                        [x + 4 + wx * int(w * 0.08),
                         y0 + int(h * (0.80 - bh)) + 5 + wy * 12,
                         x + 9 + wx * int(w * 0.08),
                         y0 + int(h * (0.80 - bh)) + 10 + wy * 12],
                        fill=(255, 230, 140))
        # tilted damaged block
        draw.polygon([(x0 + int(w * 0.84), y0 + int(h * 0.80)),
                      (x0 + int(w * 0.98), y0 + int(h * 0.80)),
                      (x0 + int(w * 0.94), y0 + int(h * 0.46)),
                      (x0 + int(w * 0.80), y0 + int(h * 0.58))],
                     fill=(70, 76, 88))

    elif kind == "desert":
        draw.rectangle(box, fill=(224, 193, 136))
        draw.ellipse([x0 + int(w * 0.74), y0 + int(h * 0.08),
                      x0 + int(w * 0.88), y0 + int(h * 0.34)],
                     fill=(255, 214, 90))
        draw.arc([x0 - int(w * 0.2), y0 + int(h * 0.55),
                  x0 + int(w * 0.7), y0 + int(h * 1.15)],
                 180, 360, fill=(196, 158, 96), width=3)
        draw.arc([x0 + int(w * 0.35), y0 + int(h * 0.66),
                  x0 + int(w * 1.2), y0 + int(h * 1.25)],
                 180, 360, fill=(196, 158, 96), width=3)
        # small drone
        dx, dy = x0 + int(w * 0.30), y0 + int(h * 0.22)
        draw.line([(dx - 8, dy), (dx + 8, dy)], fill=(60, 50, 40), width=2)
        draw.line([(dx, dy - 8), (dx, dy + 8)], fill=(60, 50, 40), width=2)
        draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(60, 50, 40))

    elif kind == "mine":
        draw.rectangle(box, fill=(52, 44, 38))
        draw.arc([x0 + int(w * 0.18), y0 + int(h * 0.10),
                  x0 + int(w * 0.82), y0 + int(h * 1.05)],
                 180, 360, fill=(140, 124, 104), width=4)
        draw.ellipse([cx - 12, y0 + int(h * 0.30), cx + 12,
                      y0 + int(h * 0.30) + 24], fill=(255, 220, 90))
        draw.ellipse([cx - 5, y0 + int(h * 0.30) + 7, cx + 5,
                      y0 + int(h * 0.30) + 17], fill=(255, 244, 170))
        draw.rectangle([x0, y0 + int(h * 0.82), x1, y1], fill=(28, 90, 120))
        draw.polygon([(x0 + int(w * 0.08), y0 + int(h * 0.82)),
                      (x0 + int(w * 0.24), y0 + int(h * 0.66)),
                      (x0 + int(w * 0.40), y0 + int(h * 0.82))],
                     fill=(90, 80, 70))
        draw.polygon([(x0 + int(w * 0.62), y0 + int(h * 0.82)),
                      (x0 + int(w * 0.76), y0 + int(h * 0.70)),
                      (x0 + int(w * 0.92), y0 + int(h * 0.82))],
                     fill=(90, 80, 70))

    elif kind == "treaty":
        draw.rectangle(box, fill=(213, 228, 238))
        # two flag poles
        for px, col in ((0.24, (0, 48, 120)), (0.68, (0, 120, 60))):
            x = x0 + int(w * px)
            draw.line([(x, y0 + int(h * 0.18)), (x, y0 + int(h * 0.82))],
                      fill=(80, 70, 60), width=2)
            draw.polygon([(x, y0 + int(h * 0.18)),
                          (x + int(w * 0.20), y0 + int(h * 0.26)),
                          (x, y0 + int(h * 0.34))], fill=col)
        # document with seal
        draw.rectangle([x0 + int(w * 0.36), y0 + int(h * 0.52),
                        x0 + int(w * 0.62), y0 + int(h * 0.86)],
                       fill=WHITE, outline=(120, 120, 120))
        for ly in (0.60, 0.68, 0.76):
            draw.line([(x0 + int(w * 0.40), y0 + int(h * ly)),
                       (x0 + int(w * 0.58), y0 + int(h * ly))],
                      fill=(150, 150, 150))
        draw.ellipse([x0 + int(w * 0.52), y0 + int(h * 0.76),
                      x0 + int(w * 0.60), y0 + int(h * 0.76) + 8],
                     fill=(163, 22, 33))

    elif kind == "rocket":
        draw.rectangle(box, fill=NIGHT)
        for sx, sy in ((0.10, 0.10), (0.30, 0.06), (0.55, 0.12),
                       (0.80, 0.08), (0.92, 0.22), (0.15, 0.30)):
            draw.ellipse([x0 + int(w * sx) - 1, y0 + int(h * sy) - 1,
                          x0 + int(w * sx) + 1, y0 + int(h * sy) + 1],
                         fill=WHITE)
        # earth arc at bottom
        draw.ellipse([x0 - int(w * 0.3), y0 + int(h * 0.86),
                      x0 + int(w * 1.3), y0 + int(h * 1.5)],
                     fill=(40, 110, 180))
        # rocket body
        bx = cx
        draw.polygon([(bx - 9, y0 + int(h * 0.62)),
                      (bx - 9, y0 + int(h * 0.28)),
                      (bx, y0 + int(h * 0.14)),
                      (bx + 9, y0 + int(h * 0.28)),
                      (bx + 9, y0 + int(h * 0.62))], fill=(235, 235, 235))
        draw.polygon([(bx - 9, y0 + int(h * 0.28)),
                      (bx, y0 + int(h * 0.14)),
                      (bx + 9, y0 + int(h * 0.28)),
                      (bx + 9, y0 + int(h * 0.36)),
                      (bx - 9, y0 + int(h * 0.36))], fill=(200, 40, 40))
        draw.polygon([(bx - 9, y0 + int(h * 0.62)),
                      (bx - 18, y0 + int(h * 0.74)),
                      (bx - 9, y0 + int(h * 0.70))], fill=(200, 40, 40))
        draw.polygon([(bx + 9, y0 + int(h * 0.62)),
                      (bx + 18, y0 + int(h * 0.74)),
                      (bx + 9, y0 + int(h * 0.70))], fill=(200, 40, 40))
        draw.polygon([(bx - 6, y0 + int(h * 0.66)),
                      (bx + 6, y0 + int(h * 0.66)),
                      (bx, y0 + int(h * 0.84))], fill=(255, 160, 0))
        draw.ellipse([bx - 4, y0 + int(h * 0.42), bx + 4,
                      y0 + int(h * 0.42) + 8], fill=(15, 76, 92))

    elif kind == "store":
        draw.rectangle(box, fill=(238, 232, 214))
        draw.rectangle([x0 + int(w * 0.10), y0 + int(h * 0.30),
                        x0 + int(w * 0.90), y0 + int(h * 0.88)],
                       fill=(250, 246, 236), outline=(120, 110, 96))
        # striped awning
        for i in range(6):
            col = (163, 22, 33) if i % 2 == 0 else (250, 246, 236)
            draw.rectangle([x0 + int(w * (0.08 + i * 0.14)),
                            y0 + int(h * 0.16),
                            x0 + int(w * (0.08 + (i + 1) * 0.14)),
                            y0 + int(h * 0.32)], fill=col)
        draw.rectangle([x0 + int(w * 0.42), y0 + int(h * 0.52),
                        x0 + int(w * 0.58), y0 + int(h * 0.88)],
                       fill=(90, 70, 50))
        draw.rectangle([x0 + int(w * 0.16), y0 + int(h * 0.52),
                        x0 + int(w * 0.36), y0 + int(h * 0.72)],
                       fill=(160, 200, 220))
        draw.rectangle([x0 + int(w * 0.64), y0 + int(h * 0.52),
                        x0 + int(w * 0.84), y0 + int(h * 0.72)],
                       fill=(160, 200, 220))

    elif kind == "inflation":
        draw.rectangle(box, fill=(240, 244, 238))
        draw.line([(x0 + int(w * 0.10), y0 + int(h * 0.85)),
                   (x0 + int(w * 0.92), y0 + int(h * 0.85))],
                  fill=(150, 150, 150))
        draw.line([(x0 + int(w * 0.10), y0 + int(h * 0.12)),
                   (x0 + int(w * 0.10), y0 + int(h * 0.85))],
                  fill=(150, 150, 150))
        pts = [(0.14, 0.66), (0.32, 0.58), (0.50, 0.60),
               (0.68, 0.44), (0.86, 0.30)]
        px = [(x0 + int(w * fx), y0 + int(h * fy)) for fx, fy in pts]
        draw.line(px, fill=(30, 125, 50), width=3)
        for px_, py_ in px:
            draw.ellipse([px_ - 3, py_ - 3, px_ + 3, py_ + 3],
                         fill=(30, 125, 50))
        draw.text((x0 + int(w * 0.60), y0 + int(h * 0.06)), "3.8%",
                  font=sans(13, True), fill=(30, 125, 50))

    elif kind == "tariff":
        draw.rectangle(box, fill=(228, 228, 226))
        # stacked container boxes
        draw.rectangle([x0 + int(w * 0.10), y0 + int(h * 0.58),
                        x0 + int(w * 0.46), y0 + int(h * 0.82)],
                       fill=(120, 70, 50))
        draw.rectangle([x0 + int(w * 0.50), y0 + int(h * 0.58),
                        x0 + int(w * 0.86), y0 + int(h * 0.82)],
                       fill=(70, 100, 130))
        draw.rectangle([x0 + int(w * 0.28), y0 + int(h * 0.34),
                        x0 + int(w * 0.64), y0 + int(h * 0.58)],
                       fill=(150, 130, 60))
        for bx0, bx1, by0, by1 in (
                (0.10, 0.46, 0.58, 0.82), (0.50, 0.86, 0.58, 0.82),
                (0.28, 0.64, 0.34, 0.58)):
            draw.rectangle([x0 + int(w * bx0), y0 + int(h * by0),
                            x0 + int(w * bx1), y0 + int(h * by1)],
                           outline=(60, 50, 40))
        # red stamp
        draw.rectangle([x0 + int(w * 0.58), y0 + int(h * 0.10),
                        x0 + int(w * 0.92), y0 + int(h * 0.28)],
                       outline=(163, 22, 33), width=2)
        draw.text((x0 + int(w * 0.63), y0 + int(h * 0.14)), "TARIFF",
                  font=sans(10, True), fill=(163, 22, 33))

    elif kind == "trophy":
        draw.rectangle(box, fill=(18, 60, 44))
        # cup
        draw.polygon([(cx - 16, y0 + int(h * 0.14)),
                      (cx + 16, y0 + int(h * 0.14)),
                      (cx + 11, y0 + int(h * 0.46)),
                      (cx - 11, y0 + int(h * 0.46))],
                     fill=(255, 200, 60))
        draw.arc([cx - 26, y0 + int(h * 0.16), cx - 8,
                  y0 + int(h * 0.44)], 90, 270, fill=(255, 200, 60), width=3)
        draw.arc([cx + 8, y0 + int(h * 0.16), cx + 26,
                  y0 + int(h * 0.44)], 270, 90, fill=(255, 200, 60), width=3)
        draw.rectangle([cx - 3, y0 + int(h * 0.46), cx + 3,
                        y0 + int(h * 0.62)], fill=(255, 200, 60))
        draw.rectangle([cx - 14, y0 + int(h * 0.62), cx + 14,
                        y0 + int(h * 0.72)], fill=(255, 200, 60))
        draw.rectangle([cx - 20, y0 + int(h * 0.72), cx + 20,
                        y0 + int(h * 0.80)], fill=(220, 170, 40))

    else:
        draw.rectangle(box, fill=PAPER_SOFT)


# ---- schematic world map ----

MAP_LAND = [
    [(18, 22), (55, 12), (95, 18), (118, 30), (108, 48), (80, 58),
     (55, 62), (28, 50), (12, 36)],
    [(105, 72), (128, 66), (140, 78), (132, 102), (116, 112), (102, 92)],
    [(168, 22), (196, 14), (210, 22), (200, 38), (178, 40), (164, 30)],
    [(168, 52), (196, 48), (208, 62), (198, 92), (180, 98), (168, 76)],
    [(212, 16), (268, 8), (310, 16), (318, 30), (296, 44), (262, 44),
     (236, 36), (214, 28)],
    [(272, 58), (286, 56), (292, 64), (278, 68)],
    [(282, 102), (308, 98), (316, 108), (300, 118), (284, 114)],
]

MAP_PINS = [
    (1, 238, 34), (2, 298, 26), (3, 218, 22), (4, 238, 42),
    (5, 214, 36), (6, 188, 72), (7, 284, 64), (8, 306, 112),
    (9, 286, 22), (10, 96, 74), (11, 48, 30), (12, 62, 42),
    (13, 162, 62),
]


def paint_map(draw, box):
    """Draw a schematic world map with numbered pins inside box."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=SEA, outline=LAND_LINE)
    sx = (x1 - x0) / 330.0
    sy = (y1 - y0) / 150.0

    def conv(px, py):
        return (x0 + px * sx, y0 + py * sy)

    for poly in MAP_LAND:
        pts = [conv(px, py) for px, py in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    for num, px, py in MAP_PINS:
        cxp, cyp = conv(px, py)
        r = 7
        draw.ellipse([cxp - r, cyp - r, cxp + r, cyp + r],
                     fill=RED, outline=WHITE, width=1)
        label = str(num)
        f = sans(8, True)
        tw = f.getlength(label)
        draw.text((cxp - tw / 2, cyp - 5), label, font=f, fill=WHITE)


# ---- page sections ----

def paint_header(draw, y):
    """Masthead: kicker row, big centred title, red subtitle."""
    left_txt = "THE WORLD IN ONE DAY"
    right_txt = "EMBER STRAIT · ONE PAGE"
    draw.text((LEFT, y), left_txt, font=sans(11, True), fill=INK)
    rf = sans(11, True)
    draw.text((RIGHT - rf.getlength(right_txt), y), right_txt,
              font=rf, fill=INK)
    y += 20
    hline(draw, LEFT, RIGHT, y, fill=INK, width=2)
    y += 6
    title = "Wednesday 25 November 2026"
    tf = serif(52, True)
    tw = tf.getlength(title)
    draw.text(((PAGE_W - tw) / 2, y), title, font=tf, fill=INK)
    y += 62
    sub = ("Tankers burn in Hormuz  ·  KOSPI plunges 6.16%  ·  "
           "Two Russian refineries ablaze")
    sf = serif(17, False)
    sw = sf.getlength(sub)
    draw.text(((PAGE_W - sw) / 2, y), sub, font=sf, fill=RED)
    y += 26
    hline(draw, LEFT, RIGHT, y, fill=RED, width=2)
    return y + 6


def paint_stats(draw, y):
    """Six numbered facts in a row."""
    cell_w = CONTENT_W // 6
    top = y
    for i, (big, label) in enumerate(STATS):
        x = LEFT + i * cell_w
        if i > 0:
            vline(draw, x, top + 4, top + 40, fill=(200, 190, 170))
        bf = sans(20, True)
        draw.text((x + 8, top), big, font=bf,
                  fill=RED if big.startswith("-") else INK)
        lines = wrap(label, sans(9, False), cell_w - 16)
        para(draw, x + 8, top + 24, lines[:1], sans(9, False),
             INK_SOFT, 11)
    hline(draw, LEFT, RIGHT, top + 44, fill=(200, 190, 170))
    return top + 50


def paint_regions(draw, y):
    """Coloured region chips with story counts."""
    cell_w = CONTENT_W // 6
    for i, (name, count) in enumerate(REGIONS):
        x = LEFT + i * cell_w
        fill = REGION_FILL[name]
        draw.rectangle([x, y, x + cell_w - 4, y + 20], fill=fill)
        label = "%s %d" % (name, count)
        f = sans(10, True)
        tw = f.getlength(label)
        draw.text((x + (cell_w - 4 - tw) / 2, y + 4), label,
                  font=f, fill=WHITE)
    return y + 26


def paint_timeline(draw, y):
    """Horizontal UTC timeline bar."""
    draw.rectangle([LEFT, y, RIGHT, y + 24], fill=(238, 234, 222),
                   outline=(200, 190, 170))
    label = "THE DAY IN UTC"
    lf = sans(10, True)
    draw.text((LEFT + 8, y + 6), label, font=lf, fill=GOLD)
    lx = LEFT + 8 + lf.getlength(label) + 12
    items = "   ·   ".join(TIMELINE)
    tf = sans(10, False)
    draw.text((lx, y + 6), items, font=tf, fill=INK)
    return y + 30


def paint_heroes(draw, y):
    """Three hero stories in columns, scene on top."""
    head_f = sans(12, True)
    draw.text((LEFT, y), "TOP STORIES", font=head_f, fill=INK)
    note = "All dated Wednesday 25 November 2026"
    nf = sans(9, False)
    draw.text((RIGHT - nf.getlength(note), y + 2), note,
              font=nf, fill=INK_SOFT)
    y += 18
    col_w = 324
    gap = 12
    scene_h = 104
    for i, hero in enumerate(HEROES):
        num, tag, place, region, headline, body, source, scene = hero
        x = LEFT + i * (col_w + gap)
        box = (x, y, x + col_w, y + scene_h)
        paint_scene(draw, box, scene)
        draw.rectangle(box, outline=(120, 110, 96))
        hline(draw, x, x + col_w, y + scene_h + 3, fill=GOLD, width=2)
        ty = y + scene_h + 9
        nf2 = sans(10, True)
        draw.text((x, ty), num, font=nf2, fill=RED)
        nx = x + 16
        w = tag_chip(draw, nx, ty, tag)
        draw.text((nx + w + 6, ty + 1), place, font=sans(10, True),
                  fill=INK)
        ty += 18
        draw.text((x, ty), region, font=sans(8, True), fill=INK_SOFT)
        ty += 12
        hf = sans(14, True)
        lines = wrap(headline, hf, col_w)
        ty = para(draw, x, ty, lines[:2], hf, INK, 17)
        ty += 2
        bf = sans(10, False)
        blines = wrap(body, bf, col_w)
        ty = para(draw, x, ty, blines[:2], bf, INK, 13)
        ty += 3
        draw.text((x, ty), source, font=sans(8, False), fill=INK_SOFT)
    return y + scene_h + 128


def paint_cards(draw, y):
    """Ten illustrated cards: five columns, two rows."""
    head_f = sans(12, True)
    draw.text((LEFT, y), "THE DAY IN TEN", font=head_f, fill=INK)
    note = "The stories that moved the world today"
    nf = sans(9, False)
    draw.text((RIGHT - nf.getlength(note), y + 2), note,
              font=nf, fill=INK_SOFT)
    y += 18
    col_w = 192
    gap = 9
    row_h = 124
    scene_h = 42
    for idx, card in enumerate(CARDS):
        num, tag, place, headline, body, source, scene = card
        row = idx // 5
        col = idx % 5
        x = LEFT + col * (col_w + gap)
        top = y + row * (row_h + 6)
        box = (x, top, x + col_w, top + scene_h)
        paint_scene(draw, box, scene)
        draw.rectangle(box, outline=(150, 142, 126))
        ty = top + scene_h + 5
        nf2 = sans(10, True)
        draw.text((x, ty), num, font=nf2, fill=RED)
        nx = x + 18
        w = tag_chip(draw, nx, ty, tag)
        draw.text((nx + w + 5, ty + 1), place, font=sans(9, True),
                  fill=INK)
        ty += 17
        hf = sans(11, True)
        lines = wrap(headline, hf, col_w)
        ty = para(draw, x, ty, lines[:2], hf, INK, 13)
        ty += 1
        bf = sans(9, False)
        blines = wrap(body, bf, col_w)
        ty = para(draw, x, ty, blines[:2], bf, INK, 11)
        ty += 2
        draw.text((x, ty), source, font=sans(8, False), fill=INK_SOFT)
    return y + 2 * row_h + 8


def paint_bottom(draw, y):
    """Map panel + date check on the left, 22 more stories on the right."""
    head_f = sans(12, True)
    draw.text((LEFT, y), "WHERE IT HAPPENED", font=head_f, fill=INK)
    note_f = sans(9, False)
    note = "pins match story numbers"
    draw.text((LEFT + 330 - note_f.getlength(note), y + 2), note,
              font=note_f, fill=INK_SOFT)
    right_title = "ALSO ON WEDNESDAY 25 NOVEMBER — 22 MORE STORIES"
    draw.text((356, y), right_title, font=head_f, fill=INK)
    y += 16
    # schematic map
    map_box = (LEFT, y, LEFT + 330, y + 118)
    paint_map(draw, map_box)
    # date-check box
    dc_top = y + 122
    dc_box = (LEFT, dc_top, LEFT + 330, dc_top + 78)
    draw.rectangle(dc_box, fill=RED_SOFT, outline=RED, width=2)
    draw.text((LEFT + 8, dc_top + 5), "DATE CHECK",
              font=sans(11, True), fill=RED)
    dfont = sans(8, False)
    dlines = wrap(DATE_CHECK, dfont, 330 - 16)
    para(draw, LEFT + 8, dc_top + 22, dlines[:6], dfont, INK, 10)
    # the 22 more stories, two columns of eleven
    col_w = 321
    for idx, (num, text) in enumerate(ALSO):
        col = idx // 11
        row = idx % 11
        x = 356 + col * (col_w + 12)
        iy = y + row * 18
        draw.text((x, iy), num, font=sans(9, True), fill=RED)
        draw.text((x + 22, iy), text, font=sans(9, False), fill=INK)
    # footer rule, legend, sources
    fy = dc_top + 78 + 6
    hline(draw, LEFT, RIGHT, fy, fill=(200, 190, 170))
    lf = sans(8, False)
    lw = lf.getlength(LEGEND)
    draw.text(((PAGE_W - lw) / 2, fy + 4), LEGEND, font=lf,
              fill=INK_SOFT)
    sf = sans(8, False)
    sw = sf.getlength(SOURCES)
    draw.text(((PAGE_W - sw) / 2, fy + 16), SOURCES, font=sf,
              fill=INK_SOFT)
    return fy + 26


def build():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(img)
    y = MARGIN
    y = paint_header(draw, y)
    y = paint_stats(draw, y)
    y = paint_regions(draw, y)
    y = paint_timeline(draw, y)
    y = paint_heroes(draw, y)
    y = paint_cards(draw, y)
    y = paint_bottom(draw, y)
    img.save(OUT_PATH, format="PNG")
    return y


if __name__ == "__main__":
    end_y = build()
    print("wrote %s (final y=%d)" % (OUT_PATH, end_y))
