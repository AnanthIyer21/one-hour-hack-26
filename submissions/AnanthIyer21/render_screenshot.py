#!/usr/bin/env python3
"""Render ANSI-coloured terminal output into a PNG (needs Pillow; the tool itself doesn't).

    ROULETTE_SEED=1 ROULETTE_FORCE_COLOR=1 bash demo.sh > /tmp/demo.ansi 2>&1
    python3 render_screenshot.py /tmp/demo.ansi screenshot.png [columns]
"""
import re
import sys

from PIL import Image, ImageDraw, ImageFont

PALETTE = {
    "30": (40, 42, 54), "31": (255, 85, 85), "32": (80, 250, 123), "33": (241, 250, 140),
    "34": (98, 154, 255), "35": (255, 121, 198), "36": (139, 233, 253), "37": (240, 240, 240),
    "91": (255, 110, 103), "93": (255, 220, 90), "95": (220, 140, 255), "96": (120, 240, 255),
}
FG, BG, DIM = (220, 223, 228), (24, 25, 33), (120, 124, 140)
EMOJI = {"🎰": "$$", "🦆": "D>", "🎉": "*", "📖": "#", "─": "-", "═": "=", "┌": "+", "🔥": "!!", "🍕": "<>"}
SGR = re.compile(r"\x1b\[([0-9;]*)m")


def font(size):
    for p in ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/SFNSMono.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]:
        try:
            return ImageFont.truetype(p, size), ImageFont.truetype(p, size, index=1) if p.endswith("ttc") else None
        except OSError:
            continue
    return ImageFont.load_default(), None


def parse(line):
    spans, colour, bold, dim, pos = [], FG, False, False, 0
    for m in SGR.finditer(line):
        if m.start() > pos:
            spans.append((line[pos:m.start()], DIM if dim else colour, bold))
        for code in (m.group(1) or "0").split(";"):
            if code in ("0", ""):
                colour, bold, dim = FG, False, False
            elif code == "1":
                bold = True
            elif code == "2":
                dim = True
            elif code in PALETTE:
                colour = PALETTE[code]
        pos = m.end()
    if pos < len(line):
        spans.append((line[pos:], DIM if dim else colour, bold))
    return spans


def main():
    src, dst = sys.argv[1], sys.argv[2]
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    text = open(src, encoding="utf-8").read()
    for k, v in EMOJI.items():
        text = text.replace(k, v)
    lines = [l.split("\r")[-1] for l in text.splitlines() if "demo repo left in" not in l]
    reg, bold = font(15)
    bold = bold or reg
    cw = reg.getbbox("M")[2]
    lh = 20
    per = -(-len(lines) // cols)
    width_chars = max(len(SGR.sub("", l)) for l in lines)
    colw = min(width_chars, 100) * cw + 40
    W, H = colw * cols + 40, per * lh + 90
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((20 + i * 24, 18, 34 + i * 24, 32), fill=c)
    d.text((W // 2 - 220, 14), "git roulette: whack() decides your fate", font=bold, fill=DIM)
    for idx, line in enumerate(lines):
        col, row = divmod(idx, per)
        x, y = 30 + col * colw, 56 + row * lh
        for txt, colour, b in parse(line):
            txt = txt[: max(0, 100 - int((x - 30 - col * colw) / cw))]
            d.text((x, y), txt, font=bold if b else reg, fill=colour)
            x += d.textlength(txt, font=bold if b else reg)
    img.save(dst)
    print(f"wrote {dst} ({W}x{H}, {len(lines)} lines in {cols} columns)")


if __name__ == "__main__":
    main()
