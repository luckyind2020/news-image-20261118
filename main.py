"""Draw Wednesday 18 November 2026's world news as one newspaper front page.

Pure Python 3 standard library. Renders a 1024x1024 PNG with a hand-built
5x7 bitmap font and a tiny PNG encoder, so the program runs with no network
and no installed packages. Every story below was reported on 18 Nov 2026.
"""

import os
import struct
import zlib
from math import cos, pi, sin

PAGE_W = 1024
PAGE_H = 1024

PAPER = (248, 244, 232)
INK = (22, 22, 22)
SOFT_INK = (74, 74, 74)
RED = (176, 32, 26)
DEEP_BLUE = (28, 74, 130)
GOLD = (176, 124, 24)
TEAL = (18, 110, 104)
PANEL = (255, 252, 244)
SKY = (214, 231, 240)
WHITE = (255, 255, 255)


# --------------------------------------------------------------------------
# 5x7 bitmap lettering. Each glyph is seven rows of five cells, '#' inked.
# --------------------------------------------------------------------------

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####..", "#...#.", "#...#.", "####..", "#...#.", "#...#.", "####.."),
    "C": (".####.", "#.....", "#.....", "#.....", "#.....", "#.....", ".####."),
    "D": ("####..", "#...#.", "#...#.", "#...#.", "#...#.", "#...#.", "####.."),
    "E": ("######", "#.....", "#.....", "####..", "#.....", "#.....", "######"),
    "F": ("######", "#.....", "#.....", "####..", "#.....", "#.....", "#....."),
    "G": (".####.", "#.....", "#.....", "#.####", "#...#.", "#...#.", ".###.."),
    "H": ("#...#.", "#...#.", "#...#.", "#####.", "#...#.", "#...#.", "#...#."),
    "I": ("#####.", "..#...", "..#...", "..#...", "..#...", "..#...", "#####."),
    "J": ("..####", "...#..", "...#..", "...#..", "...#..", "#..#..", ".##..."),
    "K": ("#...#.", "#..#..", "#.#...", "##....", "#.#...", "#..#..", "#...#."),
    "L": ("#.....", "#.....", "#.....", "#.....", "#.....", "#.....", "######"),
    "M": ("#...#.", "##.##.", "#.#.#.", "#.#.#.", "#...#.", "#...#.", "#...#."),
    "N": ("#...#.", "##..#.", "#.#.#.", "#..##.", "#...#.", "#...#.", "#...#."),
    "O": (".###..", "#...#.", "#...#.", "#...#.", "#...#.", "#...#.", ".###.."),
    "P": ("####..", "#...#.", "#...#.", "####..", "#.....", "#.....", "#....."),
    "Q": (".###..", "#...#.", "#...#.", "#...#.", "#.#.#.", "#..#..", ".##.#."),
    "R": ("####..", "#...#.", "#...#.", "####..", "#.#...", "#..#..", "#...#."),
    "S": (".####.", "#.....", "#.....", ".###..", "....#.", "....#.", "####.."),
    "T": ("#####.", "..#...", "..#...", "..#...", "..#...", "..#...", "..#..."),
    "U": ("#...#.", "#...#.", "#...#.", "#...#.", "#...#.", "#...#.", ".###.."),
    "V": ("#...#.", "#...#.", "#...#.", "#...#.", "#...#.", ".#.#..", "..#..."),
    "W": ("#...#.", "#...#.", "#...#.", "#.#.#.", "#.#.#.", "##.##.", "#...#."),
    "X": ("#...#.", "#...#.", ".#.#..", "..#...", ".#.#..", "#...#.", "#...#."),
    "Y": ("#...#.", "#...#.", ".#.#..", "..#...", "..#...", "..#...", "..#..."),
    "Z": ("#####.", "....#.", "...#..", "..#...", ".#....", "#.....", "#####."),
    "0": (".###..", "#...#.", "#..##.", "#.#.#.", "##..#.", "#...#.", ".###.."),
    "1": ("..#...", ".##...", "..#...", "..#...", "..#...", "..#...", ".###.."),
    "2": (".###..", "#...#.", "....#.", "...#..", "..#...", ".#....", "#####."),
    "3": ("####..", "....#.", "....#.", ".###..", "....#.", "....#.", "####.."),
    "4": ("...#..", "..##..", ".#.#..", "#..#..", "#####.", "...#..", "...#.."),
    "5": ("#####.", "#.....", "####..", "....#.", "....#.", "#...#.", ".###.."),
    "6": (".###..", "#.....", "#.....", "####..", "#...#.", "#...#.", ".###.."),
    "7": ("#####.", "....#.", "...#..", "...#..", "..#...", "..#...", "..#..."),
    "8": (".###..", "#...#.", "#...#.", ".###..", "#...#.", "#...#.", ".###.."),
    "9": (".###..", "#...#.", "#...#.", ".####.", "....#.", "....#.", ".###.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": ("......", "......", "......", "......", "......", ".##...", ".##..."),
    ",": ("......", "......", "......", "......", ".##...", ".##...", ".#...."),
    ":": ("......", ".##...", ".##...", "......", ".##...", ".##...", "......"),
    ";": ("......", ".##...", ".##...", "......", ".##...", ".##...", ".#...."),
    "-": ("......", "......", "......", "#####.", "......", "......", "......"),
    "'": ("..#...", "..#...", "..#...", "......", "......", "......", "......"),
    "/": ("....#.", "....#.", "...#..", "..#...", ".#....", "#.....", "#....."),
    "(": ("...##.", "..#...", ".#....", ".#....", ".#....", "..#...", "...##."),
    ")": ("##....", "..#...", "...#..", "...#..", "...#..", "..#...", "##...."),
    "!": ("..#...", "..#...", "..#...", "..#...", "..#...", "......", "..#..."),
    "?": (".###..", "#...#.", "....#.", "...#..", "..#...", "......", "..#..."),
    "+": ("......", "..#...", "..#...", "#####.", "..#...", "..#...", "......"),
    "=": ("......", "......", "#####.", "......", "#####.", "......", "......"),
}


for _rows in FONT.values():
    for _row in _rows:
        assert len(_row) >= 5, "every glyph row needs at least five cells"
FONT = {ch: tuple(row[:5] for row in rows) for ch, rows in FONT.items()}


def glyph_rows(ch):
    return FONT.get(ch, FONT["?"])


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_words(text, max_px, scale):
    """Greedy word wrap; returns a list of lines that fit max_px."""
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_px or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# --------------------------------------------------------------------------
# Canvas: an RGB raster with small drawing helpers.
# --------------------------------------------------------------------------

class Canvas:
    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * width * height)

    def put(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            at = (y * self.width + x) * 3
            self.pixels[at] = color[0]
            self.pixels[at + 1] = color[1]
            self.pixels[at + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            at = (yy * self.width + x0) * 3
            self.pixels[at:at + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y - thick // 2, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x - thick // 2, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        radius = thick // 2
        while True:
            for oy in range(-radius, radius + 1):
                for ox in range(-radius, radius + 1):
                    if ox * ox + oy * oy <= radius * radius + radius:
                        self.put(x0 + ox, y0 + oy, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, radius, color):
        for yy in range(cy - radius, cy + radius + 1):
            half = int((radius * radius - (yy - cy) ** 2) ** 0.5)
            self.rect(cx - half, yy, half * 2 + 1, 1, color)

    def ring(self, cx, cy, radius, color, thick=2):
        steps = max(24, radius * 4)
        for i in range(steps):
            a = 2 * pi * i / steps
            self.disc(int(cx + radius * cos(a)), int(cy + radius * sin(a)),
                      thick, color)

    def arc(self, cx, cy, radius, start_deg, end_deg, color, thick=2):
        steps = max(8, int(radius * (end_deg - start_deg) / 90))
        for i in range(steps + 1):
            a = pi * (start_deg + (end_deg - start_deg) * i / steps) / 180.0
            self.disc(int(cx + radius * cos(a)), int(cy + radius * sin(a)),
                      thick, color)

    def poly(self, points, color):
        """Scanline fill of a simple polygon."""
        if len(points) < 3:
            return
        top = min(p[1] for p in points)
        bottom = max(p[1] for p in points)
        edges = []
        count = len(points)
        for i in range(count):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % count]
            if y0 != y1:
                edges.append((x0, y0, x1, y1))
        for yy in range(top, bottom + 1):
            xs = []
            for x0, y0, x1, y1 in edges:
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), yy, max(1, int(xs[i + 1]) - int(xs[i])), 1, color)

    def draw_text(self, x, y, text, scale, color):
        cursor = x
        for ch in text.upper():
            rows = glyph_rows(ch)
            for r in range(7):
                row = rows[r]
                for c in range(5):
                    if row[c] == "#":
                        self.rect(cursor + c * scale, y + r * scale,
                                  scale, scale, color)
            cursor += 6 * scale

    def text_centered(self, cx, y, text, scale, color):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)


# --------------------------------------------------------------------------
# Little pictograms, one per story. All geometric, drawn from scratch.
# --------------------------------------------------------------------------

def draw_plane(cv, x, y, w, h, color):
    cv.rect(x, y, w, h, SKY)
    cv.disc(x + int(w * 0.82), y + int(h * 0.2), int(h * 0.11), GOLD)
    for cx, cw in ((0.08, 0.22), (0.55, 0.3)):
        bx = x + int(w * cx)
        by = y + int(h * 0.24)
        cv.rect(bx, by, int(w * cw), int(h * 0.1), WHITE)
        cv.disc(bx, by + int(h * 0.05), int(h * 0.05), WHITE)
        cv.disc(bx + int(w * cw), by + int(h * 0.05), int(h * 0.05), WHITE)
    # Skyline along the bottom.
    base = y + h
    for i, (fx, fw, fh) in enumerate(((0.02, 0.12, 0.3), (0.17, 0.09, 0.42),
                                     (0.29, 0.13, 0.26), (0.45, 0.1, 0.5),
                                     (0.58, 0.12, 0.34), (0.73, 0.09, 0.46),
                                     (0.85, 0.12, 0.3))):
        cv.rect(x + int(w * fx), base - int(h * fh), int(w * fw), int(h * fh),
                (58, 74, 96) if i % 2 == 0 else (88, 102, 122))
    # Airplane in side view, nose to the right.
    px, py = x + int(w * 0.16), y + int(h * 0.34)
    pw, ph = int(w * 0.68), int(h * 0.16)
    cv.poly([(px, py + ph // 2), (px + pw // 2, py), (px + int(pw * 0.82), py),
             (px + pw, py + ph // 2), (px + int(pw * 0.82), py + ph),
             (px + pw // 2, py + ph)], color)
    cv.poly([(px + int(pw * 0.1), py), (px + int(pw * 0.22), py - int(ph * 1.5)),
             (px + int(pw * 0.3), py - int(ph * 1.5)), (px + int(pw * 0.3), py)],
            color)
    cv.poly([(px + int(pw * 0.42), py + ph), (px + int(pw * 0.58), py + ph + int(ph * 1.9)),
             (px + int(pw * 0.68), py + ph + int(ph * 1.9)), (px + int(pw * 0.62), py + ph)],
            color)
    cv.poly([(px + int(pw * 0.62), py + ph), (px + int(pw * 0.74), py + ph + int(ph * 1.1)),
             (px + int(pw * 0.8), py + ph + int(ph * 1.1)), (px + int(pw * 0.72), py + ph)],
            color)
    for i in range(4):
        wx = px + int(pw * (0.34 + 0.1 * i))
        cv.rect(wx, py + int(ph * 0.28), int(pw * 0.045), int(ph * 0.42), WHITE)


def draw_bridge(cv, x, y, w, h, color):
    cv.rect(x, y, w, h, (228, 236, 242))
    deck_y = y + int(h * 0.62)
    cv.rect(x, deck_y, w, int(h * 0.07), INK)
    for tx in (0.24, 0.68):
        txp = x + int(w * tx)
        cv.rect(txp - int(w * 0.02), y + int(h * 0.12), int(w * 0.04),
                deck_y - y - int(h * 0.12), INK)
        cv.rect(txp - int(w * 0.045), y + int(h * 0.08), int(w * 0.09),
                int(h * 0.05), INK)
    # Main cable sagging between the towers, plus suspenders.
    left = x + int(w * 0.24)
    right = x + int(w * 0.68)
    top = y + int(h * 0.14)
    mid = y + int(h * 0.5)
    prev = None
    for i in range(33):
        t = i / 32.0
        cx = int(left + (right - left) * t)
        cy = int(top + (mid - top) * 4 * t * (1 - t) * 1.9)
        if prev is not None:
            cv.line(prev[0], prev[1], cx, cy, color, 3)
        prev = (cx, cy)
    for i in range(1, 8):
        t = i / 8.0
        cx = int(left + (right - left) * t)
        cy = int(top + (mid - top) * 4 * t * (1 - t) * 1.9)
        cv.vline(cx, cy, deck_y - cy, color, 2)
    for i, wy in enumerate((0.72, 0.8, 0.88)):
        cv.hline(x + int(w * 0.08), y + int(h * wy), int(w * 0.84),
                 DEEP_BLUE if i % 2 == 0 else TEAL, 3)


def draw_drone_radar(cv, x, y, w, h, color):
    cv.rect(x, y, w, h, (226, 232, 226))
    cx, cy = x + w // 2, y + int(h * 0.34)
    cv.rect(cx - int(w * 0.1), cy - int(h * 0.06), int(w * 0.2), int(h * 0.12), INK)
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ax = cx + sx * int(w * 0.26)
        ay = cy + sy * int(h * 0.16)
        cv.line(cx, cy, ax, ay, INK, 3)
        cv.hline(ax - int(w * 0.09), ay, int(w * 0.18), INK, 4)
        cv.disc(ax, ay, int(h * 0.035), INK)
    cv.line(cx, cy + int(h * 0.06), cx, y + int(h * 0.62), INK, 3)
    cv.arc(cx, y + int(h * 0.78), int(w * 0.3), 200, 340, color, 4)
    cv.arc(cx, y + int(h * 0.78), int(w * 0.2), 200, 340, color, 3)
    cv.arc(cx, y + int(h * 0.78), int(w * 0.1), 200, 340, color, 3)
    cv.disc(cx, y + int(h * 0.78), int(h * 0.03), color)


def draw_flags(cv, x, y, w, h, color):
    cv.rect(x, y, w, h, (238, 232, 214))
    pole_y0 = y + int(h * 0.14)
    pole_y1 = y + int(h * 0.88)
    for fx, flag in ((0.14, "china"), (0.56, "canada")):
        px = x + int(w * fx)
        cv.vline(px, pole_y0, pole_y1 - pole_y0, INK, 3)
        fw = int(w * 0.3)
        fh = int(h * 0.3)
        if flag == "china":
            cv.rect(px + 2, pole_y0, fw, fh, RED)
            cv.disc(px + 2 + int(fw * 0.28), pole_y0 + int(fh * 0.3),
                    int(fh * 0.1), GOLD)
            cv.disc(px + 2 + int(fw * 0.62), pole_y0 + int(fh * 0.24),
                    int(fh * 0.06), GOLD)
            cv.disc(px + 2 + int(fw * 0.72), pole_y0 + int(fh * 0.5),
                    int(fh * 0.06), GOLD)
        else:
            cv.rect(px + 2, pole_y0, fw, fh, WHITE)
            cv.rect(px + 2, pole_y0, int(fw * 0.22), fh, RED)
            cv.rect(px + 2 + int(fw * 0.78), pole_y0, int(fw * 0.22), fh, RED)
            cv.disc(px + 2 + fw // 2, pole_y0 + fh // 2, int(fh * 0.16), RED)
    cv.hline(x + int(w * 0.08), pole_y1, int(w * 0.84), INK, 3)


def draw_gavel(cv, x, y, w, h, color):
    cv.rect(x, y, w, h, (236, 228, 220))
    cv.line(x + int(w * 0.2), y + int(h * 0.3), x + int(w * 0.66),
            y + int(h * 0.3), color, 16)
    cv.line(x + int(w * 0.42), y + int(h * 0.36), x + int(w * 0.62),
            y + int(h * 0.82), INK, 6)
    cv.rect(x + int(w * 0.5), y + int(h * 0.84), int(w * 0.3), int(h * 0.08), INK)
    cv.disc(x + int(w * 0.84), y + int(h * 0.2), int(h * 0.07), GOLD)
    cv.disc(x + int(w * 0.14), y + int(h * 0.78), int(h * 0.05), GOLD)


def draw_cyclone(cv, x, y, w, h, color):
    cv.rect(x, y, w, h, (220, 230, 238))
    cx, cy = x + w // 2, y + int(h * 0.52)
    span = min(w, int(h * 1.4))
    for radius, start, end in ((0.34, 20, 300), (0.24, 140, 420), (0.14, 260, 540)):
        cv.arc(cx, cy, int(span * radius), start, end, color, 5)
    cv.disc(cx, cy, int(h * 0.05), RED)
    for i in range(5):
        rx = x + int(w * (0.12 + 0.18 * i))
        ry = y + int(h * (0.86 + (0.04 if i % 2 else 0.0)))
        cv.line(rx, ry, rx - int(w * 0.03), ry + int(h * 0.07), DEEP_BLUE, 3)


def draw_cricket(cv, x, y, w, h, color):
    cv.rect(x, y, w, h, (232, 240, 222))
    bx, by = x + int(w * 0.3), y + int(h * 0.16)
    cv.poly([(bx, by), (bx + int(w * 0.16), by), (bx + int(w * 0.16), by + int(h * 0.5)),
             (bx + int(w * 0.1), by + int(h * 0.58)), (bx, by + int(h * 0.5))], color)
    cv.rect(bx + int(w * 0.05), by - int(h * 0.16), int(w * 0.06), int(h * 0.18), INK)
    cv.disc(x + int(w * 0.72), y + int(h * 0.66), int(h * 0.13), RED)
    cv.arc(x + int(w * 0.72), y + int(h * 0.66), int(h * 0.08), 60, 240, WHITE, 3)


PICTOGRAMS = {
    "plane": draw_plane,
    "bridge": draw_bridge,
    "drone": draw_drone_radar,
    "flags": draw_flags,
    "gavel": draw_gavel,
    "cyclone": draw_cyclone,
    "cricket": draw_cricket,
}


# --------------------------------------------------------------------------
# The day's stories. Headlines and standfirsts follow what was reported
# on Wednesday 18 November 2026; nothing here invents a number or a quote.
# --------------------------------------------------------------------------

LEAD = {
    "kicker": "ASIA - DIPLOMACY",
    "headline": "TRUMP LANDS IN MANILA FOR QUAD TALKS",
    "standfirst": "Asia trip opens as the ASEAN summit ends; China visit next.",
    "pictogram": "plane",
    "accent": DEEP_BLUE,
}

SECOND = {
    "kicker": "WAR IN UKRAINE",
    "headline": "UKRAINE HITS CRIMEA BRIDGE AGAIN",
    "standfirst": "Second day of strikes; Russia hits Kyiv bridges.",
    "pictogram": "bridge",
    "accent": RED,
}

SMALL = [
    {
        "kicker": "MIDDLE EAST",
        "headline": "IRAN DRONE ATTACK ON US RADAR IN BAHRAIN",
        "standfirst": "Tehran claims a US drone downed.",
        "pictogram": "drone",
        "accent": TEAL,
    },
    {
        "kicker": "TRADE",
        "headline": "CANADA AND CHINA EXTEND TRADE DEALS",
        "standfirst": "Xi meets Carney ahead of APEC.",
        "pictogram": "flags",
        "accent": RED,
    },
    {
        "kicker": "BRITAIN",
        "headline": "BRITAIN SANCTIONS ISRAELI SETTLEMENT FIRMS",
        "standfirst": "To protect the two-state solution.",
        "pictogram": "gavel",
        "accent": DEEP_BLUE,
    },
    {
        "kicker": "WEATHER",
        "headline": "CYCLONE AKVAN BEARS DOWN ON BAY OF BENGAL",
        "standfirst": "Severe storm warning from IMD.",
        "pictogram": "cyclone",
        "accent": TEAL,
    },
]

STRIP = [
    {
        "kicker": "SPORT",
        "headline": "DHONI ENDS IPL PLAYING CAREER",
        "standfirst": "Chennai Super Kings name him mentor.",
        "pictogram": "cricket",
        "accent": GOLD,
    },
]


# --------------------------------------------------------------------------
# Page composition.
# --------------------------------------------------------------------------

def story_panel(cv, x, y, w, h, story, head_scale, sub_scale, pic_h=92):
    cv.rect(x, y, w, h, PANEL)
    cv.rect(x, y, w, 4, story["accent"])
    cv.rect(x, y, 2, h, story["accent"])
    cv.rect(x + w - 2, y, 2, h, story["accent"])
    cv.rect(x, y + h - 2, w, 2, story["accent"])
    pad = 14
    inner = w - 2 * pad
    cursor = y + 16
    cv.draw_text(x + pad, cursor, story["kicker"], 2, story["accent"])
    cursor += 24
    PICTOGRAMS[story["pictogram"]](cv, x + pad, cursor, inner, pic_h,
                                   story["accent"])
    cursor += pic_h + 14
    for line in wrap_words(story["headline"], inner, head_scale):
        cv.draw_text(x + pad, cursor, line, head_scale, INK)
        cursor += 7 * head_scale + 5
    for line in wrap_words(story["standfirst"], inner, sub_scale):
        cv.draw_text(x + pad, cursor, line, sub_scale, SOFT_INK)
        cursor += 7 * sub_scale + 4


def strip_panel(cv, x, y, w, h, story):
    cv.rect(x, y, w, h, PANEL)
    cv.rect(x, y, w, 4, story["accent"])
    cv.rect(x, y, 2, h, story["accent"])
    cv.rect(x + w - 2, y, 2, h, story["accent"])
    cv.rect(x, y + h - 2, w, 2, story["accent"])
    pic = 96
    PICTOGRAMS[story["pictogram"]](cv, x + 14, y + (h - pic) // 2, pic, pic,
                                   story["accent"])
    tx = x + 14 + pic + 18
    avail = x + w - 14 - tx
    cv.draw_text(tx, y + 20, story["kicker"], 2, story["accent"])
    cursor = y + 46
    for line in wrap_words(story["headline"], avail, 4):
        cv.draw_text(tx, cursor, line, 4, INK)
        cursor += 7 * 4 + 5
    for line in wrap_words(story["standfirst"], avail, 2):
        cv.draw_text(tx, cursor, line, 2, SOFT_INK)
        cursor += 7 * 2 + 4


def compose():
    cv = Canvas(PAGE_W, PAGE_H, PAPER)
    cv.rect(8, 8, PAGE_W - 16, PAGE_H - 16, INK)
    cv.rect(10, 10, PAGE_W - 20, PAGE_H - 20, PAPER)
    cv.rect(16, 16, PAGE_W - 32, PAGE_H - 32, INK)
    cv.rect(17, 17, PAGE_W - 34, PAGE_H - 34, PAPER)

    # Masthead.
    cv.text_centered(PAGE_W // 2, 34, "ONE DAY - ONE PICTURE", 2, SOFT_INK)
    cv.text_centered(PAGE_W // 2, 56, "WORLD NEWS", 8, INK)
    cv.rect(24, 128, PAGE_W - 48, 44, RED)
    cv.text_centered(PAGE_W // 2, 140, "WEDNESDAY 18 NOVEMBER 2026", 4, WHITE)
    cv.text_centered(PAGE_W // 2, 182, "THE DAY'S NEWS, IN ONE PICTURE", 2, SOFT_INK)

    # Lead row: Trump in Manila, Ukraine bridge.
    story_panel(cv, 24, 208, 594, 292, LEAD, 4, 2)
    story_panel(cv, 634, 208, 366, 292, SECOND, 4, 2)

    # Four smaller stories across regions and fields.
    small_w = 232
    for i, story in enumerate(SMALL):
        story_panel(cv, 24 + i * (small_w + 12), 516, small_w, 304,
                    story, 3, 2, pic_h=84)

    # Sport strip.
    strip_panel(cv, 24, 836, 976, 124, STRIP[0])

    # Footer repeats the date so the day is unmistakable.
    cv.text_centered(PAGE_W // 2, 978, "ALL EVENTS REPORTED ON 18 NOVEMBER 2026",
                     2, SOFT_INK)
    return cv


# --------------------------------------------------------------------------
# Minimal PNG encoder: signature, IHDR, IDAT (zlib, filter 0), IEND.
# --------------------------------------------------------------------------

def png_chunk(kind, payload):
    out = struct.pack(">I", len(payload)) + kind + payload
    out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    stride = cv.width * 3
    for yy in range(cv.height):
        raw.append(0)
        start = yy * stride
        raw += cv.pixels[start:start + stride]
    ihdr = struct.pack(">IIBBBBB", cv.width, cv.height, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n"
    blob += png_chunk(b"IHDR", ihdr)
    blob += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    blob += png_chunk(b"IEND", b"")
    return blob


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(compose())
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)
    print("wrote %s (%d bytes)" % (target, len(data)))


if __name__ == "__main__":
    main()
