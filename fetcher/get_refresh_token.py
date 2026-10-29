"""
One-time helper: log in to Google and print a refresh token.

Run this ONCE (and again only if the token stops working).
Copy the printed refresh token into the GitHub secret GMAIL_REFRESH_TOKEN.
This script never writes anything to disk, so nothing secret can be committed.

Usage (from the repo root, with the venv active):
    python fetcher/get_refresh_token.py
"""

import getpass
import os

from google_auth_oauthlib.flow import InstalledAppFlow

# Read-only access: the script can read emails but can never send, delete or change them.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# A fixed port makes the redirect URL predictable, which matters in Codespaces
# (see the "If the redirect fails" steps printed below).
PORT = 8080


def ask_for_value(env_name, prompt_text, hide_input):
    """Use the environment variable if it is set, otherwise ask the user to type it."""
    value = os.environ.get(env_name)
    if value:
        print(f"Using {env_name} from the environment.")
        return value.strip()

    # getpass hides what you type, so the secret does not show on screen.
    if hide_input:
        value = getpass.getpass(prompt_text)
    else:
        value = input(prompt_text)
    return value.strip()


def build_client_config(client_id, client_secret):
    """
    Build the same structure as the client_secret.json file Google lets you download.
    Building it in memory means we never need that file in the repo.
    """
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }
    return client_config


def print_redirect_help():
    print()
    print("A login link will appear below. Open it in your browser and sign in.")
    print()
    print("If the redirect fails (e.g. 'localhost refused to connect'):")
    print("  1. Copy the FULL URL from that failed browser tab.")
    print("     It starts with http://localhost:8080/?state=...&code=...")
    print("  2. Open a SECOND terminal in Codespaces and run:")
    print('         curl "PASTE_THE_URL_HERE"')
    print("  3. Come back to this terminal. The token should now be printed.")
    print()


def main():
    client_id = ask_for_value("GMAIL_CLIENT_ID", "Paste your OAuth client ID: ", False)
    client_secret = ask_for_value("GMAIL_CLIENT_SECRET", "Paste your OAuth client secret (hidden): ", True)

    if not client_id or not client_secret:
        print("Client ID and client secret are both required. Stopping.")
        return

    client_config = build_client_config(client_id, client_secret)
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

    print_redirect_help()

    # open_browser=False: Codespaces has no browser of its own, so we just print the link.
    # access_type="offline": asks Google for a refresh token, not just a 1-hour access token.
    # prompt="consent": forces the consent screen so Google sends a refresh token
    #                   even if you have logged in to this app before.
    credentials = flow.run_local_server(
        port=PORT,
        open_browser=False,
        access_type="offline",
        prompt="consent",
    )

    if not credentials.refresh_token:
        print("Google did not return a refresh token.")
        print("Remove the app at https://myaccount.google.com/permissions and run this again.")
        return

    print()
    print("=" * 60)
    print("Success! Your refresh token is:")
    print()
    print(credentials.refresh_token)
    print()
    print("Save it as the GitHub secret GMAIL_REFRESH_TOKEN.")
    print("Do NOT paste it into any file. Run 'clear' in this terminal afterwards.")
    print("=" * 60)


if __name__ == "__main__":
    main()
