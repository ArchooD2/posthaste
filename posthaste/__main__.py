import sys
import os
import requests
import webbrowser
import subprocess
from snaparg import SnapArgumentParser as ArgumentParser

DOCS_URL = 'https://www.toptal.com/developers/hastebin'

def save_token_to_env(token):
    """Save the token permanently and immediately as best as possible."""
    os.environ['POSTHASTE_TOKEN'] = token
    if os.name == 'nt':
        subprocess.run(f'setx POSTHASTE_TOKEN "{token}"', shell=True)
        print("\n✅ Token saved to POSTHASTE_TOKEN environment variable.")
        print("⚡ Open a new terminal window to pick up the change!")
    else:
        shell = os.environ.get('SHELL', '')
        profile_paths = [
            os.path.expanduser("~/.bashrc"),
            os.path.expanduser("~/.bash_profile"),
            os.path.expanduser("~/.zshrc"),
            os.path.expanduser("~/.profile"),
        ]
        updated = False
        for profile_path in profile_paths:
            if os.path.exists(profile_path):
                with open(profile_path, 'a', encoding='utf-8') as f:
                    f.write(f'\n# Added by posthaste\nexport POSTHASTE_TOKEN="{token}"\n')
                print(f"\n✅ Token appended to {profile_path}")
                updated = True
                break
        if not updated:
            print("\n⚠️ Could not find a profile file (.bashrc, .zshrc, etc.) to update.")
            print(f"👉 Please manually add:\nexport POSTHASTE_TOKEN=\"{token}\"")
    print("\n✅ Token applied to this session!")

def upload(text, url, token=None, timeout=5, verbose=False):
    headers = {
        'Content-Type': 'text/plain'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    if verbose:
        print("\n🔍 Upload details:")
        print("➡️ URL:", f'{url.rstrip("/")}/documents')
        print("🧾 Headers:", headers)
        print("📄 Payload preview:", repr(text[:200]) + ('...' if len(text) > 200 else ''))

    try:
        response = requests.post(f'{url.rstrip("/")}/documents', headers=headers, data=text.encode('utf-8'), timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print(f"\n{e}\nUnauthorized! You probably need to run this with -t YOURTOKEN.")
            sys.exit(1)
        else:
            print(f"Error: HTTP error during upload: {e}", file=sys.stderr)
            sys.exit(1)
    except requests.RequestException as e:
        print(f"Error: Failed to connect or upload: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = response.json()
        key = result.get('key')
        if not key:
            print("Error: Server response missing 'key'.", file=sys.stderr)
            sys.exit(1)
    except ValueError:
        print("Error: Failed to parse JSON response.", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print("✅ Upload response:", result)

    print(f'{url.rstrip("/")}/share/{key}')

def main():
    parser = ArgumentParser(description="Quickly upload text or files to a Hastebin-compatible server.")
    parser.add_argument('files', nargs='*', help='Files to upload (optional if piping input)')
    parser.add_argument('-t', '--token', nargs='?', help='Hastebin API token')
    parser.add_argument('--url', default=os.environ.get('POSTHASTE_URL', 'https://hastebin.com'), help='Hastebin server URL')
    parser.add_argument('--timeout', type=int, default=5, help='Request timeout in seconds')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    if "toptal.com" in args.url:
        print("❌ Error: https://toptal.com is not a valid API endpoint. Use https://hastebin.com instead.")
        sys.exit(1)

    if ('-t' in sys.argv or '--token' in sys.argv):
        if args.token is None:
            print(f"Provide a token after -t or --token once attained.\nPlease visit: {DOCS_URL}")
            webbrowser.open(DOCS_URL)
            sys.exit(1)
        else:
            save_token_to_env(args.token)
            sys.exit(0)

    token = os.environ.get('POSTHASTE_TOKEN')

    if args.files:
        for filepath in args.files:
            filepath = os.path.expanduser(filepath)
            if not os.path.isfile(filepath):
                print(f'Error: File {filepath} not found.', file=sys.stderr)
                sys.exit(1)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            if not text:
                print(f'Error: File {filepath} is empty.', file=sys.stderr)
                sys.exit(1)
            print(f"\n📄 Uploading file: {filepath}")
            upload(text, args.url, token=token, timeout=args.timeout, verbose=args.verbose)
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
        if text.strip():
            upload(text, args.url, token=token, timeout=args.timeout, verbose=args.verbose)
        else:
            print('Error: No input provided.', file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
