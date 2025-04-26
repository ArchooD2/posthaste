import sys
import os
import requests
from snaparg import SnapArgumentParser as ArgumentParser

def upload(text, url):
    r = requests.post(f'{url}/documents', data=text.encode('utf-8'))
    r.raise_for_status()
    result = r.json()
    print(f'{url}/{result["key"]}')

def main():
    parser = ArgumentParser(description="Quickly upload text or files to a Hastebin-compatible server.")
    parser.add_argument('files', nargs='*', help='Files to upload (optional if piping input)')
    parser.add_argument('--url', default=os.environ.get('POSTHASTE_URL', 'https://hastebin.com'), help='Hastebin server URL')
    args = parser.parse_args()

    if args.files:
        for filepath in args.files:
            filepath = os.path.expanduser(filepath)
            if not os.path.isfile(filepath):
                print(f'Error: File {filepath} not found.', file=sys.stderr)
                continue
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            upload(text, args.url)
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
        if text.strip():
            upload(text, args.url)
        else:
            print('Error: No input provided.', file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
