<<<<<<< HEAD
from features.autoUpload import upload_short

upload_short(
    video_path="test_short.mp4",
    title="Testing PopShorts 🚀",
    description="This short was uploaded using AI automation.",
    tags=["shorts", "ai", "podcast", "testing"],
    privacy_status="public"
)
=======
# import importlib.util
# from pathlib import Path

# # Load autoUpload module directly
# module_path = Path(__file__).parent.parent.parent / "backend" / "features" / "autoUpload.py"
# spec = importlib.util.spec_from_file_location("autoUpload", module_path)
# autoUpload = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(autoUpload)

# upload_short = autoUpload.upload_short


# upload_short(
#     video_path=str(Path(__file__).parent.parent / "testing-assets" / "17_367-6de263de-70fe-4892-8f27-ffb92e29539c.mp4"),
#     title="Testing PopShorts 🚀",
#     description="This short was uploaded using AI automation.",
#     tags=["shorts", "ai", "podcast", "testing"],
#     privacy_status="public"
# )


# import pickle
# from pathlib import Path

# # ---- paths ----
# BASE_DIR = Path(__file__).parent.parent
# CREDENTIALS_PATH = BASE_DIR / "backend" / "secrets" / "youtube_credentials.pkl"
# VIDEO_PATH = BASE_DIR / "testing-assets" / "17_367-6de263de-70fe-4892-8f27-ffb92e29539c.mp4"

# # ---- load credentials ----
# if not CREDENTIALS_PATH.exists():
#     raise FileNotFoundError(
#         "OAuth credentials not found. Run web OAuth flow once to generate them."
#     )

# with open(CREDENTIALS_PATH, "rb") as f:
#     credentials = pickle.load(f)

# # ---- import upload function normally ----
# from backend.features.autoUpload import upload_short

# # ---- test upload ----
# upload_short(
#     credentials=credentials,
#     video_path=str(VIDEO_PATH),
#     title="Testing PopShorts 🚀",
#     description="This short was uploaded using AI automation.",
#     tags=["shorts", "ai", "podcast", "testing"],
#     privacy_status="public"
# )


import sys
import pickle
from pathlib import Path

# 🔥 FIX: make backend importable
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

def main():
    print("🔧 Starting PopShorts upload test...")

    CREDENTIALS_PATH = BASE_DIR / "secrets" / "youtube_credentials.pkl"
    VIDEO_PATH = (
        BASE_DIR
        / "testing"
        / "testing-assets"
        / "17_367-6de263de-70fe-4892-8f27-ffb92e29539c.mp4"
    )

    print(f"📁 Base dir: {BASE_DIR}")
    print(f"🔐 Credentials path: {CREDENTIALS_PATH}")
    print(f"🎞️ Video path: {VIDEO_PATH}")

    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(f"OAuth credentials not found at {CREDENTIALS_PATH}")

    with open(CREDENTIALS_PATH, "rb") as f:
        credentials = pickle.load(f)

    print("📦 Importing upload function...")
    from backend.features.autoUpload import upload_short

    print("🚀 Uploading video to YouTube (this may take 30–60s)...")

    upload_short(
        credentials=credentials,
        video_path=str(VIDEO_PATH),
        title="Testing PopShorts 🚀",
        description="This short was uploaded using AI automation.",
        tags=["shorts", "ai", "podcast", "testing"],
        privacy_status="public"
    )

    print("✅ Test upload finished successfully.")


if __name__ == "__main__":
    main()
>>>>>>> 643670f (autoUpload and oauth functionality completed and tested)
