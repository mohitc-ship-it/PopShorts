import os
import subprocess
import shutil
from typing import List, Dict, Optional

# ---------------------------------------------------
# Safe FFmpeg Escaping
# ---------------------------------------------------

def _escape_ffmpeg_value(s: str) -> str:
    # if not s:
    #     return ""

    s = str(s)
    # Escape backslash first
    s = s.replace("'", "")
    s = s.replace('"', '')
    s = s.replace('/', '')
    s = s.replace('\\', "")

    return s


def _hex_rgb(col) -> str:
    if not col:
        return "ffffff"
    if isinstance(col, (tuple, list)):
        return f"{int(col[0]):02x}{int(col[1]):02x}{int(col[2]):02x}"
    return str(col).lstrip("#")[:6]

def _ffmpeg_exists():
    return shutil.which("ffmpeg") is not None


# ---------------------------------------------------
# Line Builder (2–4 words per line)
# ---------------------------------------------------

def build_lines(words, min_words=2, max_words=4):
    lines = []
    buffer = []
    for w in words:
        buffer.append(w)

        if len(buffer) >= max_words:
            lines.append({
                "text": " ".join(x["word"] for x in buffer),
                "start": buffer[0]["start"],
                "end": buffer[-1]["end"],
            })
            buffer = []

    if buffer:
        lines.append({
            "text": " ".join(x["word"] for x in buffer),
            "start": buffer[0]["start"],
            "end": buffer[-1]["end"],
        })

    return lines


# ---------------------------------------------------
# Main Renderer
# ---------------------------------------------------

def add_subtitles(
    video_path,
    words,
    style,
    output_path,
    mode="word",     # "word" or "line"
    min_words=2,
    max_words=4,
):

    if not _ffmpeg_exists():
        raise RuntimeError("ffmpeg not found")

    style = style or {}

    # ---- Prepare units ----
    if mode == "line":
        units = build_lines(words, min_words, max_words)
        get_text = lambda u: u["text"]
        get_start = lambda u: u["start"]
        get_end = lambda u: u["end"]
    else:
        units = words
        get_text = lambda u: u["word"]
        get_start = lambda u: u["start"]
        get_end = lambda u: u["end"]

    # ---- Style ----
    font_size = int(style.get("font_size", 48))
    color_hex = _hex_rgb(style.get("color"))
    opacity = float(style.get("opacity", 1))
    stroke_w = int(style.get("stroke_width", 0))
    stroke_color = _hex_rgb(style.get("stroke_fill"))
    margin = int(style.get("margin", 50))

    fontfile = None
    if style.get("font_family") and os.path.isfile(style["font_family"]):
        fontfile = _escape_ffmpeg_value(style["font_family"])

    pos = style.get("position", "bottom")
    if pos == "top":
        x, y = "(w-text_w)/2", str(margin)
    elif pos == "center":
        x, y = "(w-text_w)/2", "(h-text_h)/2"
    else:
        x, y = "(w-text_w)/2", f"h-text_h-{margin}"

    # ---- Build filters ----
    filters = []

    for u in units:
        text = _escape_ffmpeg_value(get_text(u))
        start = get_start(u)
        end = get_end(u)

        parts = [f"drawtext=text='{text}'"]

        if fontfile:
            parts.append(f"fontfile='{fontfile}'")

        parts += [
            f"fontsize={font_size}",
            f"fontcolor=0x{color_hex}@{opacity}",
            f"x={x}",
            f"y={y}",
            f"enable='between(t,{start},{end})'",
        ]

        if stroke_w > 0:
            parts.append(f"borderw={stroke_w}")
            parts.append(f"bordercolor=0x{stroke_color}")

        filters.append(":".join(parts))

    vf = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-c:a", "aac",
        output_path
    ]

    print("\n".join(cmd))

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)


# ---------------------------------------------------
# Example
# ---------------------------------------------------

if __name__ == "__main__":
    words = [
        {"word": "Thi's", "start": 0.2, "end": 0.5},
        {"word": "is", "start": 0.5, "end": 0.7},
        {"word": "a", "start": 0.7, "end": 0.9},
        {"word": "reel", "start": 0.9, "end": 1.3},
        {"word": "style", "start": 1.3, "end": 1.7},
        {"word": "subtitle", "start": 1.7, "end": 2.3},
    ]

    style = {
        "font_size": 48,
        "color": "#ffffff",
        "stroke_width": 2,
        "stroke_fill": "#000000",
        "position": "bottom",
        "margin": 60,
    }

    add_subtitles("test.mp4", words, style, "out_line.mp4", mode="line")
    add_subtitles("test.mp4", words, style, "out_word.mp4", mode="word")
