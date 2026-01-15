# import pickle
# from pathlib import Path
# from google_auth_oauthlib.flow import Flow

# SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
# CLIENT_SECRETS = str(Path(__file__).parent.parent.parent / "secrets" / "client_secrets.json")
# REDIRECT_URI = "http://localhost:8080/"

# flow = Flow.from_client_secrets_file(
#     CLIENT_SECRETS,
#     scopes=SCOPES,
#     redirect_uri=REDIRECT_URI
# )

# auth_url, _ = flow.authorization_url(
#     access_type="offline",
#     prompt="consent"
# )

# print("\n🔑 Open this URL in your browser:\n")
# print(auth_url)

# # ---- user pastes redirected URL ----
# redirect_response = input("\nPaste the FULL redirected URL here:\n")

# flow.fetch_token(authorization_response=redirect_response)
# credentials = flow.credentials

# with open("secrets/youtube_credentials.pkl", "wb") as f:
#     pickle.dump(credentials, f)

# print("\n✅ Credentials saved successfully!")
# print("You will NOT need to login again.")

import pickle
from pathlib import Path
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# project root → PopShorts/
BASE_DIR = Path(__file__).parent.parent.parent

CLIENT_SECRETS = BASE_DIR / "secrets" / "client_secrets.json"
REDIRECT_URI = "http://localhost:8080/"

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

auth_url, _ = flow.authorization_url(
    access_type="offline",
    prompt="consent"
)

print("\n🔑 Open this URL in your browser:\n")
print(auth_url)

redirect_response = input("\nPaste the FULL redirected URL here:\n")

flow.fetch_token(authorization_response=redirect_response)
credentials = flow.credentials

# 🔧 FIX: save to correct absolute path
SECRETS_DIR = BASE_DIR / "secrets"
SECRETS_DIR.mkdir(exist_ok=True)

with open(SECRETS_DIR / "youtube_credentials.pkl", "wb") as f:
    pickle.dump(credentials, f)

print("\n✅ Credentials saved successfully!")
print("You will NOT need to login again.")
