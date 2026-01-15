# pipeline
from utils.llm import llm_query, llm_structured
from utils.transcription import get_word_array
from utils.videoProcessing import get_video_dimensions, extract_audio_for_asr, extract_audio, trim_video

def process_video(file_path,upload=False):

    # contextAwareCrop(video_path)

    width, height = get_video_dimensions(file_path)

    audio_path = extract_audio_for_asr(file_path)

    word_array = get_word_array(audio_path)

    script = ""
    for word in word_array:
        script += f"{word} "

    # trimmed_path = trim_video(file_path, start_time=0, end_time=60)

    llm_structured()


