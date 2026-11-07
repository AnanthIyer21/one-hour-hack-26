#!/usr/bin/env python3
"""Turn an animated Git Roulette run into demo.gif (needs Pillow; the tool itself doesn't).

    ROULETTE_SEED=2 ROULETTE_FORCE_COLOR=1 ROULETTE_FORCE_ANIM=1 ROULETTE_FAST=1 bash demo.sh > /tmp/anim.ansi 2>&1
    python3 render_gif.py /tmp/anim.ansi demo.gif [max_lines]

Every carriage return (the spinning reel) becomes a frame, and so does every new line.
"""
import sys

from PIL import Image, ImageDraw

from render_screenshot import BG, DIM, EMOJI, FG, PALETTE, SGR, font, parse

ROWS, COLS, LH = 36, 104, 20


def main():
    src, dst = sys.argv[1], sys.argv[2]
    max_lines = int(sys.argv[3]) if len(sys.argv) > 3 else 140
    text = open(src, encoding="utf-8", newline="").read()
    for k, v in EMOJI.items():
        text = text.replace(k, v)
    reg, bold = font(15)
    bold = bold or reg
    cw = reg.getbbox("M")[2]
    W, H = COLS * cw + 40, ROWS * LH + 70

    ref = Image.new("RGB", (16, 16), BG)
    rd = ImageDraw.Draw(ref)
    cols = [BG, FG, DIM, (255, 95, 86), (255, 189, 46), (39, 201, 63)] + list(PALETTE.values())
    for i, colr in enumerate(cols):
        rd.point((i % 16, i // 16), fill=colr)
    pal = ref.quantize(colors=len(cols))
    screen, cur = [], ""
    frames, durations = [], []

    def snap(ms):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            d.ellipse((16 + i * 22, 14, 28 + i * 22, 26), fill=col)
        d.text((W // 2 - 200, 10), "git roulette: whack() decides your fate", font=bold, fill=DIM)
        for row, line in enumerate((screen + [cur])[-ROWS:]):
            x, y = 20, 44 + row * LH
            for txt, colour, b in parse(line):
                f = bold if b else reg
                d.text((x, y), txt, font=f, fill=colour)
                x += d.textlength(txt, font=f)
        frames.append(img.quantize(palette=pal, dither=Image.Dither.NONE))
        durations.append(ms)

    lines_done = 0
    for ch in text:
        if ch == "\r":
            if SGR.sub("", cur).strip().startswith("["):
                snap(70)
            cur = ""
        elif ch == "\n":
            screen.append(cur)
            plain = SGR.sub("", cur)
            hold = 1300 if ("whack() rolled" in plain or "ACHIEVEMENT" in plain or "BLOCKED" in plain) else 90
            if "[ *****" in plain:
                hold = 600
            cur = ""
            lines_done += 1
            snap(hold)
            if lines_done >= max_lines:
                break
        else:
            cur += ch
    durations[-1] = 4000
    frames[0].save(dst, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    print(f"wrote {dst}: {len(frames)} frames, {sum(durations) / 1000:.0f}s")


if __name__ == "__main__":
    main()
