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


# def find_clip_times(words_array, phrases):
#     start_time = None
#     end_time = None
#     start_index = None
#     end_index = None

#     phrase_index = 0
#     phrase_words = phrases[phrase_index].split()
#     match_index = 0

#     for i, w in enumerate(words_array):
#         if w["word"].lower() == phrase_words[match_index].lower():
#             if match_index == 0 and start_time is None:
#                 start_time = w["start"]
#                 start_index = i

#             match_index += 1

#             if match_index == len(phrase_words):
#                 end_time = w["end"]
#                 end_index = i

#                 phrase_index += 1
#                 if phrase_index == len(phrases):
#                     break

#                 phrase_words = phrases[phrase_index].split()
#                 match_index = 0

#     return start_time, end_time, start_index, end_index

import string
import string

def normalize_word(word: str) -> str:
    return word.lower().translate(str.maketrans('', '', string.punctuation))


# def find_clip_times(words_array, phrases):
#     normalized_words = [normalize_word(w["word"]) for w in words_array]

#     start_time = None
#     end_time = None
#     start_index = None
#     end_index = None

#     current_pos = 0  # where we are in the transcript

#     for phrase in phrases:
#         phrase_words = [normalize_word(w) for w in phrase.split()]
#         phrase_len = len(phrase_words)

#         found = False

#         while current_pos <= len(normalized_words) - phrase_len:
#             # Check full sequence match
#             if normalized_words[current_pos:current_pos + phrase_len] == phrase_words:
#                 if start_time is None:
#                     start_time = words_array[current_pos]["start"]
#                     start_index = current_pos

#                 end_time = words_array[current_pos + phrase_len - 1]["end"]
#                 end_index = current_pos + phrase_len - 1

#                 current_pos = current_pos + phrase_len  # move forward
#                 found = True
#                 break

#             current_pos += 1

#         if not found:
#             break  # phrase not found → stop searching

#     return start_time, end_time, start_index, end_index

def find_clip_times(words_array, phrase):
    normalized_words = [normalize_word(w["word"]) for w in words_array]

    phrase_words = [normalize_word(w) for w in phrase.split()]
    phrase_len = len(phrase_words)

    for current_pos in range(len(normalized_words) - phrase_len + 1):
        # Check full sequence match
        if normalized_words[current_pos:current_pos + phrase_len] == phrase_words:
            start_time = words_array[current_pos]["start"]
            end_time = words_array[current_pos + phrase_len - 1]["end"]
            start_index = current_pos
            end_index = current_pos + phrase_len - 1
            return start_time, end_time, start_index, end_index

    # Phrase not found
    return None, None, None, None



def attach_audio_segment(
    video_chunk_path: str,
    full_audio_path: str,
    start_time: float,
    end_time: float,
    output_path: str,
    overwrite: bool = True
):
    """
    Attach a specific audio segment from full audio to a chunked video.

    Args:
        video_chunk_path (str): Cropped / chunked video (video-only or muted)
        full_audio_path (str): Original full audio file
        start_time (float): Start time in seconds
        end_time (float): End time in seconds
        output_path (str): Final output video
        overwrite (bool): Overwrite output file if exists
    """

    video_chunk_path = video_chunk_path
    full_audio_path = full_audio_path
    output_path = output_path

    if not os.path.exists(video_chunk_path):
        raise FileNotFoundError(f"Video chunk not found: {video_chunk_path}")
    if not os.path.exists(full_audio_path):
        raise FileNotFoundError(f"Full audio not found: {full_audio_path}")
    if end_time <= start_time:
        raise ValueError("end_time must be greater than start_time")

    duration = end_time - start_time

    cmd = [
        "ffmpeg",
        "-y" if overwrite else "-n",

        # Input video
        "-i", str(video_chunk_path),

        # Audio segment from full audio
        "-ss", str(start_time),
        "-t", str(duration),
        "-i", str(full_audio_path),

        # Stream mapping
        "-map", "0:v:0",
        "-map", "1:a:0",

        # Codecs
        "-c:v", "copy",      # no video re-encode
        "-c:a", "aac",

        # Safety
        "-shortest",

        str(output_path)
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed:\n{e.stderr}")


# extract_audio_for_asr("test2_trimmed.mp4")

# trim_video("test2.mp4", start_time=0, end_time=300,output_path="trimmed_output.mp4")

def combine_videos(video_paths, output_path):
    """
    Combines multiple video files into a single video file sequentially.

    Args:
        video_paths (list): List of paths to input video files
        output_path (str): Path for the combined output video

    Returns:
        str: Path to the combined video
    """
    
    if not video_paths:
        raise ValueError("No video paths provided for combination")

    # Create a temporary file listing all inputs
    list_path = f"inputs_{os.path.basename(output_path)}.txt"
    list_path = os.path.abspath(list_path)
    
    try:
        with open(list_path, "w") as f:
            for path in video_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")

        # Run ffmpeg concat
        command = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path,
            "-c", "copy",
            output_path
        ]
        
        subprocess.run(command, check=True)
        
    finally:
        # Cleanup input list file
        if os.path.exists(list_path):
            os.remove(list_path)
            
    return output_path