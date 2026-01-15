# pipeline
from utils.llm import llm_query, llm_structured
from utils.transcription import get_word_array
from utils.videoProcessing import get_video_dimensions, extract_audio_for_asr, extract_audio, trim_video, find_clip_times
from features.subtitleAddition import add_subtitles
from models import ContentIdeasList, ShortsList

def process_video(file_path,upload=False):

    contextCroppedVideo = contextAwareCrop(video_path)

    width, height = get_video_dimensions(file_path)

    audio_path = extract_audio_for_asr(file_path)

    word_array = get_word_array(audio_path)

    with open("./word_array.json", "w") as f:
        json.dump(word_array, f)

    script = ""
    for word in word_array:
        script += f"{word} "

    # shorts_details = llm_structured("extract chunks of 60-90seconds , where they talk about either there personal story or suggestion or something controversial , which is intriguiging for audience")


    shorts_details = llm_structured(f"""SYSTEM:
You are a YouTube Shorts content strategist.
Your job is to identify moments in a podcast that could become viral short-form clips.

USER:
Here is the full transcript of a podcast episode:

{script}

Return a list of 10–15 candidate clip ideas.

For each clip return:
- topic
- why it is interesting
- the exact quote that should be used (verbatim)
- the emotion or curiosity hook (e.g. shock, insight, controversy, humor)

Do not summarize. Use exact words from the transcript.
Return JSON only.
""",ContentIdeasList)


    shorts = lm_structured(f"""SYSTEM:
You are a YouTube Shorts scriptwriter.

USER:
Create a 30–60 second short-form video script using ONLY the words from the transcript.

Base it on this clip idea:

Topic: {topic}
Core Quote: "{quote}"

Rules:
- You must only use words that appear in the transcript
- Do not paraphrase
- You may reorder or remove filler words
- Make it flow like a short-form viral clip

Return:
- final_short_text
- list of phrases in the order they appear
JSON only.
""",ShortsList)

    final_shorts = []
    for short in shorts.shorts:
        start_time, end_time, start_index, end_index = find_clip_times(word_array, short.phrases)
        trimmed_path = trim_video(file_path, start_time, end_time,f"./shorts/{short.topic}.mp4")
        subtitleAddedVideo = add_subtitles(trimmed_path, word_array, style, f"./shorts/shorts_with_subs_{start_index}_{end_index}.mp4", mode="line")
        final_shorts.append({
            "topic": short.topic,
            "final_short_text": short.final_short_text,
            "phrases": short.phrases,
            "start_time": start_time,
            "end_time": end_time,
            "trimmed_path": trimmed_path,
            "start_index": start_index,
            "end_index": end_index,
            "subtitleAddedVideo": subtitleAddedVideo
        })
    
    with open("./shorts/shorts.json", "w") as f:
        json.dump(final_shorts, f)

    # add_subtitles("test.mp4", words, style, "out_line.mp4", mode="line")
    
    # trimmed_path = trim_video(file_path, start_time=0, end_time=60)


