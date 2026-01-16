# pipeline
import os
import json
from utils.llm import llm_query, llm_structured
from utils.transcription import get_word_array
from utils.videoProcessing import get_video_dimensions, extract_audio_for_asr, extract_audio, trim_video, find_clip_times, attach_audio_segment, combine_videos
from features.subtitleAddition import add_subtitles
from models import ContentIdeasList, ShortScript
from features.context_crop.contextAwareCrop import generate_context_aware_crop


def process_video(file_path, upload=False, mode="sequential"):

    temp_files = []

    # width, height = get_video_dimensions(file_path)

    # audio_path = extract_audio_for_asr(file_path)
    audio_path = "audio.wav"

    # word_array = get_word_array(audio_path)

    # with open(os.path.join(".", "word_array.json"), "w") as f:
    #     json.dump(word_array, f)

    with open(os.path.join("word_array.json"), "r") as f:
        word_array = json.load(f)

    script = ""
    for word in word_array:
        script += f"{word['word']} "


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

    print("shorts ", shorts_details)
    contentList = shorts_details.contentList

    # shorts = []
    # for index,content in enumerate(contentList):
    #     if index>1:
    #         break
    #     print("taking each content ", content)
    #     topic = content.topic
    #     quote = content.quote


    #     short = llm_structured(f"""SYSTEM:
    # You are a YouTube Shorts scriptwriter.

    # USER:
    # Create a 160-180 words short-form video script using ONLY the words from the transcript.

    # Base it on this clip idea:

    # Topic: {topic}
    # Core Quote: "{quote}"

    # extract the exact words that should be used (verbatim) from script 

    # {script}

    # Rules:
    # - You must only use words that appear in the transcript
    # - Do not paraphrase
    # - You may reorder or remove filler words
    # - Make it flow like a short-form viral clip

    # Return:
    # - final_short_text
    # - list of phrases in the order they appear
    # JSON only.
    # """,ShortScript)

    # shorts.append(short)


    # print("final shorts content . ", shorts)
    shorts = [ShortScript(final_short_text="You think about a person like that. You think of them as in this, like, static, fully formed version, right? You don't usually get to see. You went into so much depth about your rise and fall. It wasn't like a straight linear process. You see a guy who runs eight 100 mile races eight weekends in a row. It's an insane accomplishment. I fell on my ass. I started from scratch again. Scratch became my friend. Just a real raw version of how my life was. You're so honest about your vulnerabilities. For people that see someone who's a beast, who's done great things, you assume they're different than you. But then you hear about your insecurities and your pitfalls, and you realize, those are the same things that go wrong with me. Maybe I have that inside of me. We all have a jacked up life in one way or another. Life is one big psychological warfare that you play on yourself.", phrases=['You think about a person like that.', 'You think of them as in this, like, static,', 'fully formed version, right?', "You don't usually get to see.", 'You went into so much depth', 'about your rise and fall.', "It wasn't like a straight linear process.", 'You see a guy who runs', 'eight 100 mile races', 'eight weekends in a row.', "It's an insane accomplishment.", 'I fell on my ass.', 'I started from scratch again.', 'Scratch became my friend.', 'Just a real raw version of how my life was.', "You're so honest about your vulnerabilities.", "For people that see someone who's a beast,", "who's done great things,", "you assume they're different than you.", 'But then you hear about your insecurities', 'and your pitfalls,', 'and you realize,', 'those are the same things', 'that go wrong with me.', 'Maybe I have that inside of me.', 'We all have a jacked up life', 'in one way or another.', 'Life is one big psychological warfare', 'that you play on yourself.'])]
    final_shorts = []
    for index, short in enumerate(shorts):
        short_id_base = f"short_{index}"
        
        style = {
            "font_size": 48,
            "color": "#ffffff",
            "stroke_width": 2,
            "stroke_fill": "#000000",
            "position": "bottom",
            "margin": 60,
        }

        if mode == "sequential":
            # Attempt to find the full sequential text
            full_text = " ".join(short.phrases)
            start_time, end_time, start_index, end_index = find_clip_times(word_array, full_text)
            
            # Fallback if full sequence not matched exactly: use first and last phrase boundaries
            if start_time is None:
                # Try finding just the text block itself first if available
                if short.final_short_text:
                     start_time, end_time, start_index, end_index = find_clip_times(word_array, short.final_short_text)
                
                if start_time is None:
                    s_t, _, s_i, _ = find_clip_times(word_array, short.phrases[0])
                    _, e_t, _, e_i = find_clip_times(word_array, short.phrases[-1])
                    if s_t is not None and e_t is not None:
                        start_time, end_time = s_t, e_t
                        start_index, end_index = s_i, e_i
            
            if start_time is None:
                print(f"Could not find timestamps for sequential short {index}")
                continue

            trimmed_path = trim_video(file_path, start_time, end_time, os.path.join("shorts", f"{short_id_base}_seq_trim.mp4"))
            temp_files.append(trimmed_path)

            contextCroppedVideo = generate_context_aware_crop(trimmed_path, os.path.join("shorts", f"{short_id_base}_seq_crop.mp4"))
            temp_files.append(contextCroppedVideo)

            audio_path_out = os.path.join("shorts", f"{short_id_base}_seq_audio.mp4")
            attach_audio_segment(contextCroppedVideo, audio_path, start_time, end_time, audio_path_out)
            temp_files.append(audio_path_out)

            # Adjust timestamps for subtitles
            words_in_clip = word_array[start_index:end_index + 1]

            adjusted_words = []
            for w in words_in_clip:
                new_w = w.copy()
                new_w["start"] = max(0.0, round(float(w["start"]) - start_time, 2))
                new_w["end"]   = max(0.0, round(float(w["end"]) - start_time, 2))
                adjusted_words.append(new_w)

            final_video = os.path.join("shorts", f"{short_id_base}.mp4")
            subtitleAddedVideo = add_subtitles(
                audio_path_out,
                adjusted_words,
                style,
                final_video,
                mode="line"
            )

            final_shorts.append({
                "final_short_text": short.final_short_text,
                "phrases": short.phrases,
                "start_time": start_time,
                "end_time": end_time,
                "trimmed_path": trimmed_path,
                "subtitleAddedVideo": subtitleAddedVideo
            })
        
        elif mode == "combined":
            clips_to_combine = []
            
            for p_idx, phrase in enumerate(short.phrases):
                p_start, p_end, p_s_idx, p_e_idx = find_clip_times(word_array, phrase)
                
                if p_start is None:
                    print(f"Phrase not found: {phrase}")
                    continue
                
                # Trim
                p_trim = trim_video(file_path, p_start, p_end, os.path.join("shorts", f"{short_id_base}_p{p_idx}_trim.mp4"))
                temp_files.append(p_trim)
                
                # Crop
                p_crop = generate_context_aware_crop(p_trim, os.path.join("shorts", f"{short_id_base}_p{p_idx}_crop.mp4"))
                temp_files.append(p_crop)
                
                # Attach Audio
                p_audio_out = os.path.join("shorts", f"{short_id_base}_p{p_idx}_audio.mp4")
                attach_audio_segment(p_crop, audio_path, p_start, p_end, p_audio_out)
                temp_files.append(p_audio_out)
                
                # Subtitles
                # Get exact words for this phrase
                words = word_array[p_s_idx:p_e_idx+1]
                adj_words = []
                for w in words:
                    nw = w.copy()
                    nw["start"] = max(0.0, round(float(w["start"]) - p_start, 2))
                    nw["end"] = max(0.0, round(float(w["end"]) - p_start, 2))
                    adj_words.append(nw)
                
                p_sub = os.path.join("shorts", f"{short_id_base}_p{p_idx}_sub.mp4")
                add_subtitles(p_audio_out, adj_words, style, p_sub, mode="line")
                temp_files.append(p_sub)
                
                clips_to_combine.append(p_sub)
            
            if clips_to_combine:
                final_combined_video = os.path.join("shorts", f"{short_id_base}_combined.mp4")
                combine_videos(clips_to_combine, final_combined_video)
                
                final_shorts.append({
                    "final_short_text": short.final_short_text,
                    "phrases": short.phrases,
                    "subtitleAddedVideo": final_combined_video
                })
    
    with open(os.path.join("shorts", "shorts.json"), "w") as f:
        json.dump(final_shorts, f)

    # Cleanup temporary videos
    print("🧹 Cleaning up temporary videos...")
    for video_path in temp_files:
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
                print(f"Deleted temp file: {video_path}")
            except Exception as e:
                print(f"Error deleting {video_path}: {e}")

    # add_subtitles("test.mp4", words, style, "out_line.mp4", mode="line")
    
    # trimmed_path = trim_video(file_path, start_time=0, end_time=60)


# process_video(os.path.join("trimmed_output.mp4"), mode="combined")