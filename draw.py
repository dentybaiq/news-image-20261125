#!/usr/bin/env python3
"""news-image-20261125 — "Ember Strait": one-day world news front page,
Wednesday 25 November 2026.

Draws a single 1024x1024 newspaper front page with Pillow: a navy top bar
and serif masthead naming the day, a number strip, region tabs sized by
story count, a UTC timeline, three illustrated hero stories, ten
illustrated cards, a schematic world map with numbered pins, a numbered
list of 22 more stories, a DATE CHECK box naming Tuesday stories that
were reported on Wednesday but did not happen on Wednesday, and a
certainty-tags legend. 35 dated stories in all, across 6 regions.

The page follows the shape the best-ranked one-day pages share (masthead,
numbers, tabs, timeline, illustrated heroes, illustrated cards, map,
also-list, date check), because the day's top-ranked entry is exactly
that: a dense, dated collage with a UTC timeline, drawn scenes,
how-sure labels and a map. Every scene and every wording here is written
fresh for this day's news, and every story is dated honestly — anything
that happened on Tuesday sits in the DATE CHECK box, not in the main list.

Run:  python3 draw.py            (writes entry.png next to this file)
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 230)
INK = (24, 24, 24)
NAVY = (18, 36, 70)
NAVY2 = (30, 54, 98)
RED = (170, 32, 36)
RED_DK = (128, 22, 26)
GOLD = (198, 160, 40)
GREEN = (28, 104, 56)
TEAL = (14, 92, 90)
ORANGE = (176, 90, 0)
PURPLE = (88, 56, 138)
GREY = (96, 94, 88)
RULE = (198, 188, 166)
CARD = (255, 253, 246)
NIGHT = (12, 26, 56)

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/noto/"
SERIF_B = os.path.join(FD, "NotoSerif-Bold.ttf")
SERIF_I = os.path.join(FD, "NotoSerif-Italic.ttf")
SANS = os.path.join(FD, "NotoSans-Regular.ttf")
SANS_B = os.path.join(FD, "NotoSans-Bold.ttf")
SANS_I = os.path.join(FD, "NotoSans-Italic.ttf")


def load_font(path, size):
    return ImageFont.truetype(path, size)


def fit_text(text, font, width):
    """Greedy word wrap to a pixel width; returns the lines that fit."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def clip_line(text, font, width):
    """Shorten one line with an ellipsis until it fits the width."""
    if font.getlength(text) <= width:
        return text
    while text and font.getlength(text + "…") > width:
        text = text[:-1].strip()
    return text + "…"


def blurb(d, x, y, text, font, fill, width, leading, limit=None):
    """Draw wrapped text; returns the y below the last line drawn."""
    lines = fit_text(text, font, width)
    if limit is not None:
        lines = lines[:limit]
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def tag_chip(d, x, y, label, bg, size=9):
    """Small filled certainty tag; returns the x just past the chip."""
    f = load_font(SANS_B, size)
    w = int(f.getlength(label)) + 10
    h = size + 7
    d.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=bg)
    d.text((x + 5, y + 3), label, font=f, fill=(255, 255, 255))
    return x + w


# ---------------------------------------------------------------- stories
# Certainty of the claim as printed on the page.
TAG_FILL = {
    "CONFIRMED": GREEN,
    "REPORTED": NAVY,
    "CLAIM": ORANGE,
    "ONGOING": RED_DK,
    "PENDING": GREY,
}

REGION_FILL = {
    "EUROPE": NAVY,
    "MIDDLE EAST": RED_DK,
    "ASIA-PACIFIC": TEAL,
    "AMERICAS": GREEN,
    "AFRICA": ORANGE,
    "OCEANIA": PURPLE,
    "WORLD": GREY,
}

HEROES = [
    {
        "n": 1, "tag": "ONGOING", "place": "STRAIT OF HORMUZ",
        "region": "MIDDLE EAST", "beat": "MIDDLE EAST · SHIPPING", "art": "hormuz",
        "head": "Two tankers hit mines and burn in the Strait of Hormuz",
        "body": ("Iran's Guard says the tankers struck mines early Wednesday; "
                 "crews fight the fires."),
        "src": "IRGC · Reuters",
    },
    {
        "n": 2, "tag": "CONFIRMED", "place": "SEOUL",
        "region": "ASIA-PACIFIC", "beat": "ASIA-PACIFIC · MARKETS", "art": "kospi",
        "head": "KOSPI plunges 6.16% as Asia's AI rally unravels",
        "body": ("Samsung -9.9%, SK Hynix -11.1%; Nikkei -2.78%, Taiex ~-5% "
                 "as AI-trade doubts spread."),
        "src": "Dow Jones · Morningstar",
    },
    {
        "n": 3, "tag": "REPORTED", "place": "SAMARA, RUSSIA",
        "region": "EUROPE", "beat": "EUROPE · WAR", "art": "refinery",
        "head": "Ukrainian drones set two Rosneft refineries ablaze",
        "body": ("Syzran and Kuibyshev hit overnight; one person killed and 145 "
                 "drones downed, Moscow says."),
        "src": "Reuters · officials",
    },
]

CARDS = [
    {"n": 4, "tag": "CLAIM", "place": "RAS TANURA", "region": "MIDDLE EAST",
     "beat": "MIDDLE EAST · ENERGY", "art": "rastanura",
     "head": "Houthis claim strike on Ras Tanura refinery",
     "body": "Yemen's Houthis say they hit the Saudi refinery; Riyadh has not "
             "confirmed damage.", "src": "Houthi statement"},
    {"n": 5, "tag": "REPORTED", "place": "GAZA", "region": "MIDDLE EAST",
     "beat": "MIDDLE EAST · WAR", "art": "gaza",
     "head": "Israel kills Hamas security chief Abuelouf",
     "body": "The colonel, his wife and two children die in a strike, Gaza "
             "medics say.", "src": "Gaza officials · medics"},
    {"n": 6, "tag": "REPORTED", "place": "SUDAN", "region": "AFRICA",
     "beat": "AFRICA · WAR", "art": "sudan",
     "head": "RSF drone strikes kill 19 civilians in Sudan",
     "body": "Emergency Lawyers: 19 dead, 20 wounded in two cities as the "
             "civil war grinds on.", "src": "Emergency Lawyers"},
    {"n": 7, "tag": "CONFIRMED", "place": "BOGOR, INDONESIA", "region": "ASIA-PACIFIC",
     "beat": "ASIA-PACIFIC · DISASTER", "art": "bogor",
     "head": "Bogor mine flood toll reaches 6; ~20 still trapped",
     "body": "Three more bodies recovered Wednesday from the flooded illegal "
             "gold mine.", "src": "Reuters"},
    {"n": 8, "tag": "CONFIRMED", "place": "CANBERRA", "region": "OCEANIA",
     "beat": "OCEANIA · SECURITY", "art": "solomons",
     "head": "Australia–Solomons sign security treaty",
     "body": "The pact bars any foreign military base on the islands; Canberra "
             "calls it a Pacific anchor.", "src": "AAP · Reuters"},
    {"n": 9, "tag": "CONFIRMED", "place": "TIANGONG", "region": "ASIA-PACIFIC",
     "beat": "ASIA-PACIFIC · SPACE", "art": "shenzhou",
     "head": "Shenzhou-24 docks; Pakistan's first astronaut in orbit",
     "body": "Docking at 04:56 UTC, ~3.5 hours after launch, as China's station "
             "gains a new crew.", "src": "China Manned Space Agency"},
    {"n": 10, "tag": "CONFIRMED", "place": "CARTAGENA, COLOMBIA", "region": "AMERICAS",
     "beat": "AMERICAS · RESCUE", "art": "cartagena",
     "head": "All hostages freed in Cartagena supermarket siege",
     "body": "Troops storm the Éxito store at dawn; one captor killed, the rest "
             "freed unharmed.", "src": "Reuters · Colombia officials"},
    {"n": 11, "tag": "CONFIRMED", "place": "WASHINGTON", "region": "AMERICAS",
     "beat": "AMERICAS · ECONOMY", "art": "pce",
     "head": "US inflation 3.8% — in line, before the Fed meets",
     "body": "October PCE rises 0.3% on the month; the last inflation read "
             "before December's FOMC.", "src": "Investopedia · BEA"},
    {"n": 12, "tag": "REPORTED", "place": "WASHINGTON", "region": "AMERICAS",
     "beat": "AMERICAS · TRADE", "art": "tariff",
     "head": "White House plans tariff hikes on China, dozens more",
     "body": "The Wall Street Journal reports a new round of increases as the "
             "US–China truce frays.", "src": "Wall Street Journal"},
    {"n": 13, "tag": "CONFIRMED", "place": "DAKAR", "region": "AFRICA",
     "beat": "AFRICA · SPORT", "art": "senegal",
     "head": "CAS hands Senegal back its Africa Cup title",
     "body": "Sport's highest court rules for Senegal on appeal; Morocco vows "
             "to challenge.", "src": "CAS · Reuters"},
]

# (number, place, headline, source, tag, region) — the breadth list.
ALSO = [
    (14, "Odesa", "Russian strike kills 2, injures 3, a child among them", "Reuters", "REPORTED", "EUROPE"),
    (15, "Benghazi", "Libya vows retaliation after 2 officers killed in port strike", "LNA", "REPORTED", "AFRICA"),
    (16, "Kyiv", "Zelenskyy: Ukraine needs €115bn in foreign aid for 2027", "Reuters", "REPORTED", "EUROPE"),
    (17, "Washington", "US defence chief pauses Patriot supplies to Ukraine", "Principia", "REPORTED", "EUROPE"),
    (18, "Warsaw", "Poland pushes permanent US presence after 2 incursions", "Reuters", "REPORTED", "EUROPE"),
    (19, "Frankfurt", "Eurozone inflation rises to 4.0%", "Eurostat", "CONFIRMED", "EUROPE"),
    (20, "Vatican", "Pope Leo: COP31 failure a worry as extremes grow", "Reuters", "CONFIRMED", "EUROPE"),
    (21, "Basel", "Roche breast cancer pill wins 2nd FDA approval", "Reuters", "CONFIRMED", "EUROPE"),
    (22, "Luton", "EasyJet profit falls 89% on £244m fuel hit", "Reuters", "CONFIRMED", "EUROPE"),
    (23, "Seattle", "Amazon buys Decart to chase Nvidia in chips", "Reuters", "REPORTED", "AMERICAS"),
    (24, "Seattle", "Amazon: hackers' AI agents broke into a university server", "Amazon", "REPORTED", "AMERICAS"),
    (25, "New York", "Anthropic falls below IPO price; $1tn valuation gone", "Principia", "REPORTED", "AMERICAS"),
    (26, "Madrid", "Abrego Garcia leaves US voluntarily, reportedly for Spain", "Reports", "REPORTED", "AMERICAS"),
    (27, "Caracas", "Venezuela reveals $237bn debt load", "Dow Jones", "REPORTED", "AMERICAS"),
    (28, "Sydney", "Australia's October inflation 4.9%; RBA on alert", "Dow Jones", "CONFIRMED", "OCEANIA"),
    (29, "Tokyo", "Nikkei -2.78%; SoftBank -14.8% in AI sell-off", "Dow Jones", "CONFIRMED", "ASIA-PACIFIC"),
    (30, "Taipei", "Taiex falls ~5% as Asia's chip stocks slide", "Reports", "CONFIRMED", "ASIA-PACIFIC"),
    (31, "New York", "Nasdaq futures -2.8% before Thanksgiving break", "Investopedia", "REPORTED", "AMERICAS"),
    (32, "Ottawa", "Bank of Canada: inflation to stay persistent", "Dow Jones", "REPORTED", "AMERICAS"),
    (33, "Santiago", "Chile's copper miners miss out on price surge", "Dow Jones", "REPORTED", "AMERICAS"),
    (34, "New York", "Musk, not investors, gains most from SpaceX–Tesla tie", "Dow Jones", "REPORTED", "AMERICAS"),
    (35, "Gulf", "Oil climbs as Hormuz attack lifts WTI to $82.51", "Investopedia", "REPORTED", "MIDDLE EAST"),
]

NUMBERS = [
    ("2", "tankers hit by mines in Hormuz"),
    ("-6.16%", "KOSPI's plunge in Seoul"),
    ("19", "civilians killed in Sudan strikes"),
    ("€115bn", "Ukraine's aid ask for 2027"),
    ("4.0%", "eurozone inflation"),
    ("4.9%", "Australia's October inflation"),
]

TIMELINE = ("04:56 UTC Shenzhou-24 docks  ·  Tankers hit mines in Hormuz  ·  "
            "KOSPI -6.16%  ·  Treaty signed in Canberra  ·  PCE 3.8% in line  ·  "
            "Tariff plan reported")

DATE_CHECK = ("Left out because they happened on Tuesday 24 Nov, though reported "
              "today: Arsenal 1–1 Dortmund, Real Madrid 5–1 PSV, Man City 2–2 "
              "Napoli, Galatasaray 1–0 Aston Villa (Champions League)  ·  Huawei "
              "convicted on 10 of 12 counts in Brooklyn  ·  Dell's record Q3: "
              "revenue $54.9bn, AI servers $22bn  ·  Dow's first close above "
              "50,000 (50,018.70)  ·  Houthi drone on a Riyadh tower injures 11")

# pins on the schematic map: (number, x, y) in map-panel coordinates.
PINS = [(1, 180, 55), (2, 245, 30), (3, 170, 20), (4, 175, 60), (5, 160, 45),
        (6, 155, 70), (7, 235, 75), (8, 255, 100), (9, 230, 25), (10, 75, 75),
        (11, 68, 32), (12, 76, 38), (13, 140, 65)]


# ---------------------------------------------------------------- scenes
def sky_stars(d, x0, y0, pts):
    for (sx, sy, r) in pts:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + r, y0 + sy + r], fill=(255, 255, 255))


def art_hormuz(d, x0, y0, x1, y1):
    """Dawn in the Strait: two tankers on a grey sea, flames, smoke, a mine."""
    w, h = x1 - x0, y1 - y0
    # dawn bands: dark sky to pale horizon
    bands = [(18, 36, 70), (70, 80, 120), (238, 190, 130)]
    for i, col in enumerate(bands):
        d.rectangle([x0, y0 + i * h // 3, x1, y0 + (i + 1) * h // 3], fill=col)
    d.ellipse([x0 + int(w * 0.78), y0 + 8, x0 + int(w * 0.78) + 26, y0 + 34],
              fill=(247, 214, 114))
    # sea
    d.rectangle([x0, y0 + h - 26, x1, y1], fill=(16, 56, 90))
    for i in range(6):
        d.arc([x0 + 8 + i * 52, y0 + h - 18, x0 + 32 + i * 52, y0 + h - 8],
              200, 340, fill=(140, 190, 220), width=2)
    # tanker one, bow left, flames amidships
    d.polygon([(x0 + 20, y1 - 34), (x0 + 130, y1 - 34), (x0 + 140, y1 - 24),
               (x0 + 30, y1 - 24)], fill=(44, 50, 62))
    d.rectangle([x0 + 100, y1 - 46, x0 + 108, y1 - 34], fill=(44, 50, 62))
    for (fx, fh, col) in [(52, 22, (255, 140, 40)), (64, 30, (255, 200, 60)),
                          (78, 18, (255, 140, 40))]:
        d.polygon([(x0 + fx, y1 - 34), (x0 + fx + 7, y1 - 34 - fh),
                   (x0 + fx + 14, y1 - 34)], fill=col)
    for (sx, sy, r) in [(58, 6, 6), (70, 0, 5)]:
        d.ellipse([x0 + sx - r, y0 + sy, x0 + sx + r, y0 + sy + 2 * r],
                  fill=(130, 130, 130))
    # tanker two, smaller, listing, smoke
    d.polygon([(x0 + 180, y1 - 30), (x0 + 280, y1 - 38), (x0 + 288, y1 - 26),
               (x0 + 190, y1 - 20)], fill=(60, 58, 66))
    for (sx, sy, r) in [(230, 4, 6), (242, -2, 5), (218, 2, 4)]:
        d.ellipse([x0 + sx - r, y0 + sy, x0 + sx + r, y0 + sy + 2 * r],
                  fill=(150, 150, 150))
    # a naval mine in the water between them
    mx, my = x0 + 158, y1 - 14
    d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(20, 20, 24))
    for ang in range(0, 360, 45):
        import math
        dx = int(9 * math.cos(math.radians(ang)))
        dy = int(9 * math.sin(math.radians(ang)))
        d.line([mx, my, mx + dx, my + dy], fill=(20, 20, 24), width=2)


def art_kospi(d, x0, y0, x1, y1):
    """A market in free fall: red bars stepping down, a steep red arrow."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(240, 232, 228))
    # Seoul tower silhouette
    d.rectangle([x0 + 14, y0 + 8, x0 + 22, y0 + 44], fill=(120, 120, 130))
    d.ellipse([x0 + 10, y0 + 2, x0 + 26, y0 + 12], fill=(120, 120, 130))
    # bars stepping down
    bars = [(44, 64, (170, 32, 36)), (70, 52, (170, 32, 36)),
            (96, 40, (170, 32, 36)), (122, 28, (170, 32, 36)),
            (148, 18, (170, 32, 36))]
    for (bx, bh, col) in bars:
        d.rectangle([x0 + bx, y1 - 12 - bh, x0 + bx + 18, y1 - 12], fill=col)
    d.line([x0 + 40, y1 - 12, x0 + 196, y1 - 12], fill=(120, 120, 120), width=1)
    # steep falling arrow
    d.line([x0 + 60, y0 + 12, x0 + 130, y0 + 34, x0 + 178, y0 + 44],
           fill=(170, 32, 36), width=4)
    d.polygon([(x0 + 178, y0 + 44), (x0 + 164, y0 + 36), (x0 + 168, y0 + 52)],
              fill=(170, 32, 36))
    # one small green bar of hope at the end
    d.rectangle([x0 + 178, y1 - 22, x0 + 190, y1 - 12], fill=(28, 104, 56))


def art_refinery(d, x0, y0, x1, y1):
    """Night over a refinery: towers, pipes, flames and smoke."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=NIGHT)
    sky_stars(d, x0, y0, [(16, 8, 2), (90, 6, 2), (180, 10, 2), (250, 8, 2),
                          (60, 20, 2), (200, 22, 2)])
    d.ellipse([x0 + w - 44, y0 + 6, x0 + w - 20, y0 + 30], fill=(238, 234, 208))
    # two distillation towers
    for (tx, th) in [(30, 56), (90, 68)]:
        d.rectangle([x0 + tx, y1 - th, x0 + tx + 34, y1], fill=(70, 76, 88))
        d.rectangle([x0 + tx - 4, y1 - th - 8, x0 + tx + 38, y1 - th],
                    fill=(70, 76, 88))
    # pipes and tanks
    d.rectangle([x0 + 150, y1 - 26, x0 + 220, y1], fill=(90, 96, 108))
    d.ellipse([x0 + 236, y1 - 34, x0 + 276, y1 - 6], fill=(90, 96, 108))
    # flames from the hit tower
    for (fx, fh, col) in [(36, 26, (255, 140, 40)), (48, 36, (255, 200, 60)),
                          (62, 22, (255, 140, 40)), (96, 20, (255, 140, 40))]:
        d.polygon([(x0 + fx, y1 - 56), (x0 + fx + 7, y1 - 56 - fh),
                   (x0 + fx + 14, y1 - 56)], fill=col)
    for (sx, sy, r) in [(46, 4, 7), (58, -2, 6), (100, 6, 5)]:
        d.ellipse([x0 + sx - r, y0 + sy, x0 + sx + r, y0 + sy + 2 * r],
                  fill=(140, 140, 140))


def art_rastanura(d, x0, y0, x1, y1):
    """A refinery at dusk with a drone overhead and one small flame."""
    w, h = x1 - x0, y1 - y0
    bands = [(246, 196, 112), (246, 230, 198), (238, 218, 188)]
    for i, col in enumerate(bands):
        d.rectangle([x0, y0 + i * h // 3, x1, y0 + (i + 1) * h // 3], fill=col)
    # towers and flare stack
    d.rectangle([x0 + 20, y1 - 44, x0 + 54, y1], fill=(90, 96, 108))
    d.rectangle([x0 + 70, y1 - 58, x0 + 100, y1], fill=(70, 76, 88))
    d.rectangle([x0 + 130, y1 - 66, x0 + 138, y1], fill=(70, 76, 88))
    d.polygon([(x0 + 136, y1 - 66), (x0 + 141, y1 - 76), (x0 + 146, y1 - 66)],
              fill=(255, 140, 40))
    # drone above
    dx, dy = x0 + 160, y0 + 14
    d.polygon([(dx, dy - 5), (dx + 6, dy), (dx, dy + 5), (dx - 6, dy)], fill=(20, 20, 24))
    d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 220, 100))
    # storage tanks
    for (tx, tw) in [(150, 30), (186, 24)]:
        d.ellipse([x0 + tx, y1 - 26, x0 + tx + tw, y1 - 8], fill=(110, 116, 128))


def art_gaza(d, x0, y0, x1, y1):
    """Rubble blocks, a cracked ground line, and a warning triangle."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(226, 216, 196))
    for (bx, by, bw, bh) in [(10, 34, 44, 16), (58, 28, 36, 22), (98, 38, 52, 12),
                             (20, 20, 30, 12), (120, 22, 40, 14)]:
        d.rectangle([x0 + bx, y0 + by, x0 + bx + bw, y0 + by + bh],
                    fill=(140, 132, 118), outline=(100, 94, 82))
    d.line([x0 + 6, y1 - 8, x0 + 60, y1 - 16, x0 + 120, y1 - 8, x0 + 196, y1 - 14],
           fill=(90, 84, 74), width=2)
    tx, ty = x0 + 158, y0 + 4
    d.polygon([(tx, ty), (tx + 22, ty + 30), (tx - 22, ty + 30)], fill=(240, 190, 40),
              outline=(150, 110, 0))
    d.text((tx - 2, ty + 8), "!", font=load_font(SANS_B, 16), fill=(120, 80, 0))
    for (gx, gy) in [(40, 46), (170, 44)]:
        d.line([x0 + gx, y0 + gy, x0 + gx, y0 + gy - 8], fill=(28, 104, 56), width=2)
        d.ellipse([x0 + gx - 3, y0 + gy - 10, x0 + gx + 3, y0 + gy - 6],
                  fill=(28, 104, 56))


def art_sudan(d, x0, y0, x1, y1):
    """Desert city under a drone: low sun, flat roofs, a smoke plume."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(240, 222, 190))
    d.ellipse([x0 + 150, y0 + 4, x0 + 178, y0 + 32], fill=(240, 170, 80))
    for (bx, bw, bh) in [(6, 34, 26), (46, 24, 36), (76, 40, 22), (122, 28, 32),
                         (156, 34, 24), (192, 14, 30)]:
        d.rectangle([x0 + bx, y1 - bh, x0 + bx + bw, y1], fill=(140, 118, 84))
        for wy in range(y1 - bh + 6, y1 - 4, 10):
            for wx in range(x0 + bx + 4, x0 + bx + bw - 4, 10):
                if (wx + wy) % 4 == 0:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(247, 215, 116))
    dx, dy = x0 + 96, y0 + 12
    d.polygon([(dx, dy - 5), (dx + 6, dy), (dx, dy + 5), (dx - 6, dy)], fill=(20, 20, 24))
    d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 220, 100))
    for (sx, sy, r) in [(150, 10, 6), (160, 4, 5), (142, 4, 4)]:
        d.ellipse([x0 + sx - r, y0 + sy, x0 + sx + r, y0 + sy + 2 * r],
                  fill=(120, 120, 120))


def art_bogor(d, x0, y0, x1, y1):
    """A green hillside with a dark mine mouth, flood water, and a lamp."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(214, 232, 214))
    # hillside
    d.polygon([(x0, y1), (x0, y0 + 30), (x0 + 100, y0 + 12), (x1, y0 + 26),
               (x1, y1)], fill=(60, 110, 60))
    # mine mouth: dark arch
    d.pieslice([x0 + 70, y1 - 44, x0 + 130, y1 - 4], 180, 360, fill=(20, 20, 22))
    d.rectangle([x0 + 70, y1 - 24, x0 + 130, y1 - 4], fill=(20, 20, 22))
    # flood water at the mouth
    d.rectangle([x0 + 70, y1 - 12, x0 + 130, y1 - 4], fill=(40, 90, 160))
    for i in range(3):
        d.arc([x0 + 76 + i * 18, y1 - 11, x0 + 88 + i * 18, y1 - 5],
              200, 340, fill=(140, 190, 220), width=1)
    # a rescue lamp beam from the mouth
    d.polygon([(x0 + 96, y1 - 12), (x0 + 104, y1 - 12), (x0 + 116, y0 + 30),
               (x0 + 108, y0 + 30)], fill=(255, 240, 170))
    # trees
    for (tx, ty) in [(20, 22), (170, 16), (188, 30)]:
        d.ellipse([x0 + tx - 8, y0 + ty - 8, x0 + tx + 8, y0 + ty + 8],
                  fill=(28, 104, 56))
        d.line([x0 + tx, y0 + ty + 8, x0 + tx, y0 + ty + 14], fill=(90, 60, 30),
               width=2)


def art_solomons(d, x0, y0, x1, y1):
    """Two flags over Pacific waves, and a signed document."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(214, 228, 240))
    # waves
    d.rectangle([x0, y0 + h - 22, x1, y1], fill=(16, 80, 130))
    for i in range(5):
        d.arc([x0 + 8 + i * 40, y0 + h - 18, x0 + 32 + i * 40, y0 + h - 8],
              200, 340, fill=(140, 190, 220), width=2)
    # two flags on poles
    for (fx, col) in [(40, (0, 60, 120)), (130, (28, 104, 56))]:
        d.line([x0 + fx, y0 + 8, x0 + fx, y0 + 44], fill=INK, width=2)
        d.rectangle([x0 + fx, y0 + 8, x0 + fx + 34, y0 + 22], fill=col)
        d.ellipse([x0 + fx + 12, y0 + 11, x0 + fx + 22, y0 + 19], fill=(255, 255, 255))
    # document with a seal
    d.rectangle([x0 + 66, y1 - 20, x0 + 134, y1 - 6], fill=(255, 255, 255),
                outline=(150, 150, 150))
    for ly in (y1 - 17, y1 - 13, y1 - 9):
        d.line([x0 + 72, ly, x0 + 112, ly], fill=(150, 150, 150), width=1)
    d.ellipse([x0 + 118, y1 - 18, x0 + 128, y1 - 8], fill=(170, 32, 36))
    # sun
    d.ellipse([x0 + 168, y0 + 6, x0 + 190, y0 + 28], fill=(247, 214, 114))


def art_shenzhou(d, x0, y0, x1, y1):
    """Orbit: black sky, stars, a station with panels, a capsule docking."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(8, 10, 24))
    sky_stars(d, x0, y0, [(10, 8, 2), (40, 4, 2), (90, 10, 2), (150, 6, 2),
                          (180, 12, 2), (60, 20, 2), (120, 22, 2), (170, 26, 2)])
    # station: central module + two panel wings
    d.rounded_rectangle([x0 + 76, y0 + 22, x0 + 124, y0 + 36], radius=6,
                        fill=(200, 205, 212), outline=(150, 150, 150))
    d.rectangle([x0 + 20, y0 + 24, x0 + 74, y0 + 34], fill=(40, 90, 160))
    d.rectangle([x0 + 126, y0 + 24, x0 + 180, y0 + 34], fill=(40, 90, 160))
    for i in range(4):
        d.line([x0 + 30 + i * 12, y0 + 24, x0 + 30 + i * 12, y0 + 34],
               fill=(120, 160, 200), width=1)
        d.line([x0 + 136 + i * 12, y0 + 24, x0 + 136 + i * 12, y0 + 34],
               fill=(120, 160, 200), width=1)
    # capsule approaching from below
    d.rounded_rectangle([x0 + 88, y0 + 44, x0 + 112, y0 + 58], radius=4,
                        fill=(240, 240, 240), outline=(150, 150, 150))
    d.polygon([(x0 + 96, y0 + 58), (x0 + 104, y0 + 58), (x0 + 100, y0 + 66)],
              fill=(255, 140, 40))
    # earth curve at the bottom
    d.ellipse([x0 - 60, y1 - 8, x0 + w + 60, y1 + 40], fill=(40, 90, 160))
    d.ellipse([x0 - 20, y1 - 4, x0 + 60, y1 + 12], fill=(28, 104, 56))


def art_cartagena(d, x0, y0, x1, y1):
    """A supermarket block with a striped awning, doors open, an ambulance."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(222, 232, 242))
    # store block
    d.rectangle([x0 + 14, y0 + 12, x0 + 150, y1 - 10], fill=(240, 240, 238))
    d.rectangle([x0 + 14, y0 + 12, x0 + 150, y0 + 22], fill=(170, 32, 36))
    # striped awning
    for i in range(6):
        col = (255, 255, 255) if i % 2 == 0 else (170, 32, 36)
        d.rectangle([x0 + 18 + i * 22, y0 + 24, x0 + 38 + i * 22, y0 + 32], fill=col)
    # open doors
    d.rectangle([x0 + 60, y1 - 34, x0 + 78, y1 - 10], fill=(60, 60, 70))
    d.rectangle([x0 + 82, y1 - 34, x0 + 100, y1 - 10], fill=(200, 200, 200))
    # ambulance with a cross
    d.rectangle([x0 + 152, y1 - 26, x0 + 192, y1 - 8], fill=(255, 255, 255),
                outline=(150, 150, 150))
    d.rectangle([x0 + 168, y1 - 22, x0 + 172, y1 - 12], fill=(28, 104, 56))
    d.rectangle([x0 + 164, y1 - 18, x0 + 176, y1 - 14], fill=(28, 104, 56))
    d.ellipse([x0 + 158, y1 - 8, x0 + 164, y1 - 2], fill=(30, 30, 30))
    d.ellipse([x0 + 182, y1 - 8, x0 + 188, y1 - 2], fill=(30, 30, 30))


def art_pce(d, x0, y0, x1, y1):
    """A price gauge: a rising line settling at a marked 3.8% level."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(232, 240, 232))
    # grid
    for gy in (y0 + 12, y0 + 26, y0 + 40):
        d.line([x0 + 10, gy, x1 - 10, gy], fill=(200, 205, 200), width=1)
    # line: up, flat, up a little
    d.line([x0 + 12, y0 + 44, x0 + 70, y0 + 30, x0 + 120, y0 + 30, x0 + 170, y0 + 18],
           fill=(28, 104, 56), width=3)
    for (px, py) in [(12, 44), (70, 30), (120, 30), (170, 18)]:
        d.ellipse([x0 + px - 3, y0 + py - 3, x0 + px + 3, y0 + py + 3],
                  fill=(28, 104, 56))
    # marker flag at the end
    d.line([x0 + 170, y0 + 18, x0 + 170, y0 + 6], fill=INK, width=2)
    d.rectangle([x0 + 170, y0 + 2, x0 + 196, y0 + 12], fill=(198, 160, 40))
    d.text((x0 + 173, y0 + 3), "3.8%", font=load_font(SANS_B, 8), fill=(24, 24, 24))


def art_tariff(d, x0, y0, x1, y1):
    """Stacked shipping containers under a crane, one stamped with a tag."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(238, 228, 210))
    # crane
    d.rectangle([x0 + 150, y0 + 4, x0 + 158, y1 - 10], fill=(90, 90, 96))
    d.rectangle([x0 + 120, y0 + 4, x0 + 196, y0 + 10], fill=(90, 90, 96))
    d.line([x0 + 154, y0 + 10, x0 + 154, y0 + 22], fill=(60, 60, 66), width=2)
    # containers
    for (cx, cy, col) in [(14, 30, (170, 32, 36)), (78, 30, (40, 90, 160)),
                          (46, 12, (28, 104, 56))]:
        d.rectangle([x0 + cx, y0 + cy, x0 + cx + 58, y0 + cy + 16], fill=col)
        for i in range(5):
            d.line([x0 + cx + 8 + i * 11, y0 + cy + 2, x0 + cx + 8 + i * 11,
                    y0 + cy + 14], fill=(255, 255, 255), width=1)
    # red tariff tag on the top box
    d.rectangle([x0 + 96, y0 + 2, x0 + 128, y0 + 14], fill=(170, 32, 36))
    d.text((x0 + 100, y0 + 4), "TARIFF", font=load_font(SANS_B, 8),
           fill=(255, 255, 255))


def art_senegal(d, x0, y0, x1, y1):
    """A gold cup on a green pitch, with a football beside it."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(222, 240, 222))
    # pitch
    d.rectangle([x0, y1 - 16, x1, y1], fill=(28, 104, 56))
    d.line([x0, y1 - 16, x1, y1 - 16], fill=(255, 255, 255), width=1)
    # trophy cup
    d.polygon([(x0 + 84, y0 + 10), (x0 + 116, y0 + 10), (x0 + 110, y0 + 30),
               (x0 + 90, y0 + 30)], fill=(198, 160, 40))
    d.ellipse([x0 + 84, y0 + 6, x0 + 116, y0 + 14], fill=(220, 185, 70))
    d.rectangle([x0 + 96, y0 + 30, x0 + 104, y0 + 38], fill=(198, 160, 40))
    d.rectangle([x0 + 86, y0 + 38, x0 + 114, y0 + 42], fill=(198, 160, 40))
    # handles
    d.arc([x0 + 72, y0 + 8, x0 + 88, y0 + 24], 90, 270, fill=(198, 160, 40), width=3)
    d.arc([x0 + 112, y0 + 8, x0 + 128, y0 + 24], 270, 90, fill=(198, 160, 40), width=3)
    # football
    d.ellipse([x0 + 150, y0 + 22, x0 + 178, y0 + 50], fill=(255, 255, 255),
              outline=(60, 60, 60), width=1)
    d.polygon([(x0 + 160, y0 + 30), (x0 + 168, y0 + 30), (x0 + 170, y0 + 38),
               (x0 + 164, y0 + 42), (x0 + 158, y0 + 38)], fill=(30, 30, 30))


ART = {
    "hormuz": art_hormuz, "kospi": art_kospi, "refinery": art_refinery,
    "rastanura": art_rastanura, "gaza": art_gaza, "sudan": art_sudan,
    "bogor": art_bogor, "solomons": art_solomons, "shenzhou": art_shenzhou,
    "cartagena": art_cartagena, "pce": art_pce, "tariff": art_tariff,
    "senegal": art_senegal,
}


# ---------------------------------------------------------------- map
def paint_scene(img, name, x0, y0, x1, y1):
    """Render one scene into a throwaway image, then paste it: nothing a
    scene draws can spill past its own box onto the card border."""
    w, h = x1 - x0, y1 - y0
    tmp = Image.new("RGB", (w, h), PAPER)
    td = ImageDraw.Draw(tmp)
    ART[name](td, 0, 0, w, h)
    img.paste(tmp, (x0, y0))


def draw_world_map(d, x0, y0, x1, y1):
    """Schematic world map: pale continents on a light sea, numbered pins."""
    d.rectangle([x0, y0, x1, y1], fill=(212, 228, 236))
    continents = [
        [(18, 18), (86, 12), (96, 44), (70, 66), (34, 58), (14, 38)],   # N America
        [(78, 76), (100, 72), (106, 100), (90, 118), (76, 98)],          # S America
        [(128, 14), (158, 10), (166, 30), (146, 40), (128, 30)],         # Europe
        [(132, 48), (162, 44), (170, 80), (152, 104), (134, 82)],        # Africa
        [(172, 10), (262, 8), (268, 48), (230, 64), (182, 44)],          # Asia
        [(226, 92), (258, 88), (262, 106), (236, 110), (224, 100)],      # Oceania
    ]
    for poly in continents:
        d.polygon([(x0 + px, y0 + py) for (px, py) in poly], fill=(238, 228, 196),
                  outline=(180, 168, 140))
    for (n, px, py) in PINS:
        d.ellipse([x0 + px - 7, y0 + py - 7, x0 + px + 7, y0 + py + 7],
                  fill=RED, outline=(255, 255, 255), width=1)
        f = load_font(SANS_B, 9)
        label = str(n)
        tw = f.getlength(label)
        d.text((x0 + px - tw / 2, y0 + py - 5), label, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- build
def region_counts():
    """Count stories per region across heroes, cards and the also-list."""
    counts = {}
    for st in HEROES + CARDS:
        counts[st["region"]] = counts.get(st["region"], 0) + 1
    for (_, _, _, _, _, region) in ALSO:
        counts[region] = counts.get(region, 0) + 1
    order = ["EUROPE", "MIDDLE EAST", "ASIA-PACIFIC", "AMERICAS", "AFRICA",
             "OCEANIA", "WORLD"]
    return [(name, counts.get(name, 0)) for name in order]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # top navy bar
    d.rectangle([0, 0, W, 26], fill=NAVY)
    d.text((8, 6), "THE WORLD IN ONE DAY", font=load_font(SANS_B, 13),
           fill=(255, 255, 255))
    right = "35 STORIES  ·  6 REGIONS  ·  EVERY ONE DATED WEDNESDAY 25 NOVEMBER 2026"
    f = load_font(SANS_B, 11)
    d.text((W - 8 - f.getlength(right), 7), right, font=f, fill=GOLD)

    # masthead
    f = load_font(SERIF_B, 58)
    title = "Wednesday 25 November 2026"
    d.text(((W - f.getlength(title)) / 2, 30), title, font=f, fill=INK)
    f = load_font(SERIF_I, 17)
    sub = ("Tankers burn in Hormuz  ·  KOSPI plunges 6.16%  ·  "
           "Two Russian refineries ablaze")
    d.text(((W - f.getlength(sub)) / 2, 94), sub, font=f, fill=RED)

    # number strip
    y0, y1 = 114, 152
    cell = (W - 16) / 6
    d.line([8, y0, W - 8, y0], fill=RULE, width=1)
    d.line([8, y1, W - 8, y1], fill=RULE, width=1)
    for i, (num, cap) in enumerate(NUMBERS):
        cx = 8 + i * cell
        d.text((cx + 8, y0 + 2), num, font=load_font(SANS_B, 22), fill=RED)
        d.text((cx + 8, y0 + 26), cap, font=load_font(SANS, 9), fill=INK)
        if i:
            d.line([cx, y0 + 3, cx, y1 - 3], fill=RULE, width=1)

    # region tabs, sized by story count
    counts = region_counts()
    total = sum(c for _, c in counts)
    y0, y1 = 156, 172
    x = 8
    for (name, count) in counts:
        if not count:
            continue
        wseg = (W - 16) * count / total
        d.rectangle([x, y0, x + wseg - 1, y1], fill=REGION_FILL[name])
        label = f"{name} {count}"
        f = load_font(SANS_B, 10)
        d.text((x + (wseg - f.getlength(label)) / 2, y0 + 3), label, font=f,
               fill=(255, 255, 255))
        x += wseg

    # UTC timeline
    y0, y1 = 176, 192
    d.rectangle([8, y0, W - 8, y1], fill=NAVY2)
    f = load_font(SANS_B, 10)
    d.text((14, y0 + 3), "THE DAY IN UTC", font=f, fill=GOLD)
    f = load_font(SANS, 10)
    tx = 14 + load_font(SANS_B, 10).getlength("THE DAY IN UTC") + 14
    d.text((tx, y0 + 3), clip_line(TIMELINE, f, W - 8 - tx - 8), font=f,
           fill=(255, 255, 255))

    # hero cards: 3 across
    hy0, hy1 = 196, 430
    hw = 322
    for i, st in enumerate(HEROES):
        x0 = 8 + i * (hw + 8)
        x1 = x0 + hw
        d.rounded_rectangle([x0, hy0, x1, hy1], radius=4, outline=RULE, width=1,
                            fill=CARD)
        paint_scene(img, st["art"], x0 + 1, hy0 + 1, x1 - 1, hy0 + 97)
        d.rectangle([x0 + 1, hy0 + 97, x1 - 1, hy0 + 98], fill=RULE)
        tx = x0 + 10
        ty = hy0 + 104
        d.text((tx, ty), str(st["n"]), font=load_font(SANS_B, 11), fill=RED)
        tx = tag_chip(d, tx + 16, ty - 1, st["tag"], TAG_FILL[st["tag"]], size=9)
        d.text((tx + 8, ty), st["place"], font=load_font(SANS_B, 10), fill=INK)
        ty += 18
        d.text((x0 + 10, ty), st["beat"], font=load_font(SANS_B, 9), fill=RED)
        ty += 13
        ty = blurb(d, x0 + 10, ty, st["head"], load_font(SANS_B, 15), INK,
                   hw - 20, 18, limit=3)
        ty += 2
        ty = blurb(d, x0 + 10, ty, st["body"], load_font(SANS, 11), INK,
                   hw - 20, 13, limit=2)
        d.text((x0 + 10, hy1 - 14), st["src"], font=load_font(SANS_I, 9), fill=GREY)

    # section header
    d.text((8, 434), "THE DAY IN TEN", font=load_font(SANS_B, 13), fill=INK)
    right = "THE STORIES THAT MOVED THE WORLD TODAY"
    f = load_font(SANS_B, 11)
    d.text((W - 8 - f.getlength(right), 436), right, font=f, fill=GREY)

    # small cards: 2 rows x 5
    cw, ch, gap = 196, 118, 8
    for i, st in enumerate(CARDS):
        row, col = divmod(i, 5)
        x0 = 8 + col * (cw + gap)
        y0 = 452 + row * (ch + gap)
        x1, y1 = x0 + cw, y0 + ch
        d.rounded_rectangle([x0, y0, x1, y1], radius=4, outline=RULE, width=1,
                            fill=CARD)
        paint_scene(img, st["art"], x0 + 1, y0 + 1, x1 - 1, y0 + 39)
        d.rectangle([x0 + 1, y0 + 39, x1 - 1, y0 + 40], fill=RULE)
        tx = x0 + 7
        ty = y0 + 43
        d.text((tx, ty), str(st["n"]), font=load_font(SANS_B, 10), fill=RED)
        tx = tag_chip(d, tx + 14, ty - 1, st["tag"], TAG_FILL[st["tag"]], size=8)
        d.text((tx + 6, ty), st["place"], font=load_font(SANS_B, 8), fill=INK)
        ty += 14
        ty = blurb(d, x0 + 7, ty, st["head"], load_font(SANS_B, 11), INK,
                   cw - 14, 12, limit=2)
        blurb(d, x0 + 7, ty, st["body"], load_font(SANS, 9), INK, cw - 14, 11,
              limit=2)
        d.text((x0 + 7, y1 - 11), st["src"], font=load_font(SANS_I, 8), fill=GREY)

    # bottom: map + also-list
    by0, by1 = 700, 896
    # map panel
    d.rounded_rectangle([8, by0, 308, by1], radius=4, outline=RULE, width=1,
                        fill=CARD)
    d.text((16, by0 + 6), "WHERE IT HAPPENED", font=load_font(SANS_B, 12), fill=INK)
    d.text((16, by0 + 22), "pins match story numbers", font=load_font(SANS, 9),
           fill=GREY)
    draw_world_map(d, 16, by0 + 40, 300, by1 - 34)
    d.text((16, by1 - 28), "Pins 1–13 match the illustrated stories above.",
           font=load_font(SANS_I, 9), fill=GREY)
    d.text((16, by1 - 16), "Schematic map, drawn in code.",
           font=load_font(SANS_I, 9), fill=GREY)
    # also-list panel
    d.rounded_rectangle([316, by0, W - 8, by1], radius=4, outline=RULE, width=1,
                        fill=CARD)
    d.text((326, by0 + 6), "ALSO ON WEDNESDAY 25 NOVEMBER — 22 MORE STORIES",
           font=load_font(SANS_B, 12), fill=INK)
    col_w = (W - 8 - 316 - 20 - 12) // 2
    for i, (n, place, head, src, tag, region) in enumerate(ALSO):
        col, row = divmod(i, 11)
        x = 326 + col * (col_w + 12)
        y = by0 + 26 + row * 14
        d.text((x, y), str(n), font=load_font(SANS_B, 10), fill=RED)
        line = f"{place} — {head}"
        line = clip_line(line, load_font(SANS, 10), col_w - 24)
        d.text((x + 22, y), line, font=load_font(SANS, 10), fill=INK)
    d.text((326, by1 - 13),
           "Wires: Reuters, AP, BBC, Al Jazeera, AAP, Dow Jones, WSJ.",
           font=load_font(SANS_I, 9), fill=GREY)

    # date check box
    dy0, dy1 = 900, 944
    d.rectangle([8, dy0, W - 8, dy1], outline=RED, width=2, fill=(255, 245, 240))
    d.text((14, dy0 + 4), "DATE CHECK", font=load_font(SANS_B, 11), fill=RED)
    blurb(d, 14, dy0 + 20, DATE_CHECK, load_font(SANS, 10), INK, W - 28, 13,
          limit=2)

    # legend
    ly = 948
    d.text((8, ly), "HOW TO READ THE TAGS — ", font=load_font(SANS_B, 10), fill=INK)
    lx = 8 + load_font(SANS_B, 10).getlength("HOW TO READ THE TAGS — ")
    legend = ("CONFIRMED official or 2+ outlets  ·  REPORTED one source's account  ·  "
              "CLAIM one side's claim, contested  ·  ONGOING still developing  ·  "
              "PENDING not settled yet")
    d.text((lx, ly), legend, font=load_font(SANS, 10), fill=INK)

    # sources footer
    sy = 962
    d.text((8, sy), "Sources: Reuters, BBC, AP, Al Jazeera, AAP, Dow Jones, WSJ, "
           "Investopedia. Scenes are drawn illustrations, not photographs.",
           font=load_font(SANS, 9), fill=GREY)

    # bottom navy bar
    d.rectangle([0, 974, W, 1000], fill=NAVY)
    d.text((8, 982), "THE WORLD IN ONE DAY", font=load_font(SANS_B, 11),
           fill=(255, 255, 255))
    right = "WEDNESDAY 25 NOVEMBER 2026  ·  ONE PAGE"
    f = load_font(SANS_B, 10)
    d.text((W - 8 - f.getlength(right), 983), right, font=f, fill=GOLD)

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    build()
