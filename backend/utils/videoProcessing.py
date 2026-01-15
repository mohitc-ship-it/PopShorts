# cut or trim or clip function
# get video dimensions
# video to audio extraction

import subprocess
import os
import json

def trim_video(video_path, start_time, end_time, output_path=None):
    """
    Trims a video between start_time and end_time.

    Args:
        video_path (str): Input video file path
        start_time (float): Start time in seconds
        end_time (float): End time in seconds
        output_path (str): Optional output file path

    Returns:
        str: Output trimmed video path
    """

    if not os.path.exists(video_path):
        raise FileNotFoundError("Video file not found")

    if end_time <= start_time:
        raise ValueError("end_time must be greater than start_time")

    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_trimmed{ext}"

    duration = end_time - start_time

    command = [
        "ffmpeg",
        "-y",                          # overwrite output
        "-ss", str(start_time),        # seek start
        "-i", video_path,
        "-t", str(duration),           # duration
        "-c:v", "libx264",              # re-encode for frame accuracy
        "-c:a", "aac",
        "-movflags", "+faststart",     # web friendly
        output_path
    ]

    subprocess.run(command, check=True)

    return output_path


# trimmed = trim_video(
#     video_path="podcast.mp4",
#     start_time=32.5,
#     end_time=57.2
# )

# print("Saved to:", trimmed)

def extract_audio(video_path, output_audio_path=None, format="wav", sample_rate=44100):
    """
    Extracts audio from a video file.

    Args:
        video_path (str): Path to video
        output_audio_path (str): Optional output path
        format (str): 'wav', 'mp3', 'aac', 'flac'
        sample_rate (int): Sample rate (e.g., 16000 for ASR, 44100 for music)

    Returns:
        str: Output audio file path
    """

    if not os.path.exists(video_path):
        raise FileNotFoundError("Video file not found")

    if output_audio_path is None:
        base = os.path.splitext(video_path)[0]
        output_audio_path = f"{base}.{format}"

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",                 # remove video
        "-acodec", "pcm_s16le" if format == "wav" else "aac",
        "-ar", str(sample_rate),
        "-ac", "2",            # stereo
        output_audio_path
    ]

    subprocess.run(command, check=True)

    return output_audio_path

def extract_audio_for_asr(video_path, output_path="audio.wav"):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path


# audio = extract_audio_for_asr("podcast.mp4")
# print("Audio saved:", audio)

def get_video_dimensions(video_path):
    """
    Returns width and height of a video.

    Args:
        video_path (str): Path to video file

    Returns:
        (width, height)
    """

    if not os.path.exists(video_path):
        raise FileNotFoundError("Video file not found")

    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        video_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)

    stream = data["streams"][0]
    return stream["width"], stream["height"]


# print(extract_audio_for_asr("../../test.mp4"))


def find_clip_times(words_array, phrases):
    start_time = None
    end_time = None
    start_index = None
    end_index = None

    phrase_index = 0
    phrase_words = phrases[phrase_index].split()
    match_index = 0

    for i, w in enumerate(words_array):
        if w["word"].lower() == phrase_words[match_index].lower():
            if match_index == 0 and start_time is None:
                start_time = w["start"]
                start_index = i

            match_index += 1

            if match_index == len(phrase_words):
                end_time = w["end"]
                end_index = i

                phrase_index += 1
                if phrase_index == len(phrases):
                    break

                phrase_words = phrases[phrase_index].split()
                match_index = 0

    return start_time, end_time, start_index, end_index


extract_audio_for_asr("test2_trimmed.mp4")