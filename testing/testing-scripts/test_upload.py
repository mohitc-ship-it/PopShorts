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
