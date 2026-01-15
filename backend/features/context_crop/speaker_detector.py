# from pyannote.audio import Pipeline
# import subprocess
# import os

# # class SpeakerDetector:
# #     def __init__(self, video_path):
# #         self.pipeline = Pipeline.from_pretrained(
# #             "pyannote/speaker-diarization",
# #             revision="2.1",
# #             #  use_auth_token=os.getenv("HF_TOKEN")
# #             token=os.getenv("HF_TOKEN")
# #         )
# class SpeakerDetector:
#     def __init__(self, video_path):
#         self.video_path = video_path

#         self.pipeline = Pipeline.from_pretrained(
#             "pyannote/speaker-diarization",
#             # token=os.getenv("HF_TOKEN")
#             use_auth_token=os.getenv("HF_TOKEN")
#         )

#         self.audio_path = "temp_audio.wav"

#         subprocess.run(
#             [
#                 "ffmpeg", "-y",
#                 "-i", video_path,
#                 "-ac", "1",
#                 "-ar", "16000",
#                 self.audio_path
#             ],
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL
#         )

#         self.diarization = self.pipeline(self.audio_path)
from pyannote.audio import Pipeline
import subprocess

class SpeakerDetector:
    def __init__(self, video_path):
        self.video_path = video_path
        self.available = False
        self.pipeline = None
        self.diarization = None

        try:
            # ✅ no token, no use_auth_token
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization"
            )

            self.audio_path = "temp_audio.wav"

            subprocess.run(
                ["ffmpeg", "-y", "-i", video_path, "-ac", "1", "-ar", "16000", self.audio_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.diarization = self.pipeline(self.audio_path)
            self.available = True
        except Exception as e:
            print(f"⚠️  SpeakerDetector not available: {e}")
            print("⚠️  Proceeding without speaker detection")
            self.available = False

    def get_stable_speaker(self, time_sec, faces):
        """Return speaker ID if available, otherwise return None"""
        if not self.available or self.diarization is None:
            return None
        
        try:
            for segment, _, speaker in self.diarization.itertracks(yield_label=True):
                if segment.start <= time_sec <= segment.end:
                    return int(speaker.split("_")[1])
        except Exception as e:
            print(f"⚠️  Error getting speaker: {e}")
            return None
        
        return None
