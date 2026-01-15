
import os
import subprocess
import shutil
from typing import List, Dict, Optional
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

"""
Add word-level subtitles onto a video using per-word start/end times and ffmpeg drawtext filters.

This implementation removes the dependency on moviepy and instead calls `ffmpeg` via
`subprocess`. It builds a chain of `drawtext` filters, using `enable='between(t,start,end)'`
for each word. This keeps the overlay purely within ffmpeg and avoids creating intermediate
image files.

Dependencies:
    - ffmpeg available on PATH

Limitations / notes:
    - Complex styling features (per-character positioning, advanced fades) are intentionally
      kept simple for reliability. Fade-in/out is not implemented here.
    - If `ffmpeg` is not installed, the function will raise a RuntimeError.
"""


def _hex_rgb(col) -> str:
    """Return RRGGBB hex (no #) from '#RRGGBB' or tuple/list (r,g,b).
    If col is None returns 'ffffff'.
    """
    if not col:
        return "ffffff"
    if isinstance(col, (tuple, list)) and (len(col) >= 3):
        r, g, b = int(col[0]) & 255, int(col[1]) & 255, int(col[2]) & 255
        return f"{r:02x}{g:02x}{b:02x}"
    s = str(col).lstrip("#")
    if len(s) >= 6:
        return s[0:6]
    # pad or fallback
    return s.rjust(6, "f")


def _escape_text_for_drawtext(text: Optional[str]) -> str:
    """Escape characters that confuse ffmpeg drawtext filter.
    We escape colon, percent and backslash and single-quote.
    """
    if text is None:
        return ""
    t = str(text)
    t = t.replace("\\", "\\\\")
    t = t.replace(":", "\\:")
    t = t.replace("%", "\\%")
    t = t.replace("'", "\\'")
    return t


def _ffmpeg_exists() -> bool:
    return shutil.which("ffmpeg") is not None

def add_word_level_subtitles(video_path: str,
                             words: List[Dict],
                             style: Optional[Dict],
                             output_path: str,
                             fps: Optional[float] = None,
                             preset: str = "medium",
                             codec: str = "libx264",
                             audio_codec: str = "aac",
                             threads: int = 4) -> None:
    """
    Overlay word-level subtitles onto video using ffmpeg drawtext filters.

    words: list of {"word": str, "start": float, "end": float}
    style: dict with keys similar to previous implementation (font_family path, font_size, color, opacity,
           stroke_width, stroke_fill, bg_color, position ("top"/"center"/"bottom" or (x,y)), margin)
    """
    if not _ffmpeg_exists():
        raise RuntimeError("ffmpeg not found on PATH; please install ffmpeg to use this function")

    if not words:
        # nothing to overlay; copy
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-c", "copy",
            output_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"ffmpeg copy failed: {res.stderr}")
        return

    # build drawtext filters
    filters = []
    fontfile = style.get("font_family") if style and style.get("font_family") and os.path.isfile(style.get("font_family")) else None
    font_size = int(style.get("font_size", 48)) if style else 48
    color_hex = _hex_rgb(style.get("color")) if style else _hex_rgb(None)
    opacity = float(style.get("opacity", 1.0)) if style else 1.0
    stroke_w = int(style.get("stroke_width", 0)) if style else 0
    stroke_color = _hex_rgb(style.get("stroke_fill")) if style else _hex_rgb(None)
    bg_color = style.get("bg_color") if style else None
    margin = int(style.get("margin", 20)) if style else 20

    for item in words:
        word = str(item.get("word", ""))
        start = float(item.get("start", 0.0))
        end = float(item.get("end", start + 0.001))
        if not word or end <= start:
            continue

        t = _escape_text_for_drawtext(word)

        # position expressions
        pos = style.get("position", "bottom") if style else "bottom"
        if isinstance(pos, (tuple, list)) and len(pos) == 2:
            x_expr = str(int(pos[0]))
            y_expr = str(int(pos[1]))
        else:
            p = (pos or "bottom").lower()
            if p == "top":
                x_expr = "(w-text_w)/2"
                y_expr = str(margin)
            elif p == "center":
                x_expr = "(w-text_w)/2"
                y_expr = "(h-text_h)/2"
            else:
                x_expr = "(w-text_w)/2"
                y_expr = f"h-text_h-{margin}"

        # color and opacity
        fontcolor = f"0x{color_hex}@{opacity}"

        parts = [f"drawtext=text='{t}'"]
        if fontfile:
            parts.append(f"fontfile={fontfile}")
        parts.append(f"fontsize={font_size}")
        parts.append(f"fontcolor={fontcolor}")
        parts.append(f"x={x_expr}")
        parts.append(f"y={y_expr}")
        parts.append(f"enable='between(t,{start},{end})'")

        if stroke_w > 0:
            parts.append(f"borderw={stroke_w}")
            parts.append(f"bordercolor=0x{stroke_color}")

        if bg_color:
            bg_hex = _hex_rgb(bg_color)
            parts.append("box=1")
            parts.append(f"boxcolor=0x{bg_hex}@{opacity}")

        filter_str = ":".join(parts)
        filters.append(filter_str)

    vf = ",".join(filters)

    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", vf,
        "-c:v", codec,
        "-preset", preset,
        "-c:a", audio_codec,
        output_path
    ]

    print("final cmd command ", cmd)
    # run ffmpeg and capture output for clearer errors
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {res.stderr}")

if __name__ == "__main__":
    # Example usage
    example_words = [
        {"word": "Hello", "start": 0.5, "end": 1.0},
        {"word": "world!", "start": 1.1, "end": 2.0},
        {"word": "This", "start": 2.1, "end": 2.4},
        {"word": "is", "start": 2.45, "end": 2.6},
        {"word": "word-level", "start": 2.7, "end": 3.4},
        {"word": "subtitle.", "start": 3.45, "end": 4.2},
    ]
    example_style = {
        "font_family": None,       # path to .ttf or None to use system default
        "font_size": 48,
        "color": "#FFFFFF",
        "opacity": 1.0,
        "stroke_width": 2,
        "stroke_fill": "#000000",
        "bg_color": None,
        "position": "bottom",
        "margin": 60
    }
    # Replace these with actual paths to test
    input_video = "test.mp4"
    output_video = "output_with_subs.mp4"

    # if os.path.isfile(input_video):
    add_word_level_subtitles(input_video, example_words, example_style, output_video)
    # else:
    #     print("Example: place an 'input.mp4' next to this script to test, or call add_word_level_subtitles() programmatically.")
    