"""Generate PWA icons for the DAV web app manifest (M4).

Run from the repo root:  python frontend/scripts/generate_icons.py
Produces 192/512 PNGs plus a maskable variant with safe-zone padding.
"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
BG = (28, 25, 23)          # stone-900, matches index.css body background
FG = (250, 249, 249)       # stone-50
ACCENT = (234, 179, 8)     # yellow accent used by the backend status page


def draw_icon(size: int, maskable: bool) -> Image.Image:
    img = Image.new("RGBA", (size, size), BG + (255,))
    d = ImageDraw.Draw(img)

    # Maskable icons get cropped to a circle by the launcher, so keep the mark
    # inside the 80% safe zone and drop the tail (it points below centre).
    maskable_ = maskable
    scale = 0.58 if maskable_ else 0.78
    cx = cy = size / 2
    r = size * scale / 2

    # Rounded speech-bubble body: the app's core idea is voice.
    pad = size * 0.5 - r
    d.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=r * 0.38,
        fill=FG + (255,),
    )

    # Tail - omitted for maskable so the mark stays within the safe zone.
    if not maskable_:
        tail_w = r * 0.30
        tail_h = r * 0.42
        d.polygon(
            [
                (cx - tail_w * 0.55, size - pad - r * 0.06),
                (cx + tail_w * 0.75, size - pad - r * 0.06),
                (cx + tail_w * 0.15, size - pad + tail_h),
            ],
            fill=FG + (255,),
        )

    # Mic glyph in the bubble, drawn as a capsule + stand.
    mic_w = r * 0.30
    mic_h = r * 0.56
    mx1, my1 = cx - mic_w / 2, cy - mic_h / 2 - r * 0.06
    mx2, my2 = cx + mic_w / 2, cy + mic_h / 2 - r * 0.06
    d.rounded_rectangle([mx1, my1, mx2, my2], radius=mic_w / 2, fill=BG + (255,))

    # Arc under the capsule
    d.arc(
        [cx - mic_w * 1.15, my2 - mic_h * 0.30, cx + mic_w * 1.15, my2 + mic_h * 0.62],
        start=0,
        end=180,
        fill=BG + (255,),
        width=max(2, int(size * 0.018)),
    )
    # Stand
    stand_w = max(2, int(size * 0.018))
    d.line(
        [cx, my2 + mic_h * 0.30, cx, my2 + mic_h * 0.52],
        fill=BG + (255,),
        width=stand_w,
    )

    if not maskable:
        # Accent dot, echoing the status page badge.
        dr = size * 0.035
        d.ellipse(
            [size - dr * 3.2, dr * 1.2, size - dr * 1.2, dr * 3.2],
            fill=ACCENT + (255,),
        )

    return img


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for name, size, maskable in [
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, False),
        ("icon-maskable-512.png", 512, True),
        ("apple-touch-icon.png", 180, False),
    ]:
        path = os.path.join(OUT, name)
        draw_icon(size, maskable).save(path, "PNG", optimize=True)
        print(f"wrote {path} ({size}x{size})")


if __name__ == "__main__":
    main()
