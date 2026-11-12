#!/usr/bin/env python3
"""Draws assets/img/logo.png (512x512) and assets/img/og.png (1200x630) with Pillow.

Run by the GitHub Actions workflow when the images are missing:
    pip install pillow && python3 tools/make_images.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
INK, SIGN, WHITE, MIST = (18, 58, 66), (255, 197, 49), (255, 255, 255), (207, 224, 228)


def font(size, bold=True):
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"]
    for base in ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation", "/usr/share/fonts/truetype", "/usr/share/fonts"]:
        for n in names:
            p = os.path.join(base, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def awning(d, width, stripe, top, depth):
    """Storefront awning: alternating yellow/white stripes with scalloped edge."""
    x, i = 0, 0
    while x < width:
        c = SIGN if i % 2 == 0 else WHITE
        d.rectangle([x, top, x + stripe, top + depth], fill=c)
        d.ellipse([x, top + depth - stripe // 2, x + stripe, top + depth + stripe // 2], fill=c)
        x += stripe
        i += 1


def logo():
    s = 512
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=96, fill=INK)
    # awning
    d.polygon([(64, 190), (448, 190), (410, 90), (102, 90)], fill=SIGN)
    for k in range(5):
        x0 = 64 + k * 77
        d.ellipse([x0, 150, x0 + 77, 250], fill=SIGN)
    # storefront
    d.line([(115, 255), (115, 425), (397, 425), (397, 255)], fill=WHITE, width=34, joint="curve")
    d.line([(224, 425), (224, 335), (288, 335), (288, 425)], fill=WHITE, width=30, joint="curve")
    im.save(os.path.join(IMG, "logo.png"))


def og():
    w, h = 1200, 630
    im = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(im)
    awning(d, w, 60, 0, 70)
    f1, f2, f3 = font(92), font(36, bold=False), font(30)
    d.text((80, 170), "Franchise", font=f1, fill=WHITE)
    fw = d.textlength("Franchise", font=f1)
    d.text((80 + fw, 170), "Connection", font=f1, fill=SIGN)
    d.text((80, 310), "Find, compare and finance the right franchise.", font=f2, fill=MIST)
    d.text((80, 360), "Free tools, 75 categories, brand-neutral guides.", font=f2, fill=MIST)
    d.text((80, 540), "franchiseconnection.com", font=f3, fill=SIGN)
    im.save(os.path.join(IMG, "og.png"), optimize=True)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    logo()
    og()
    print("images written")
