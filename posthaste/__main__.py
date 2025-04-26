import sys
import requests
import os

def upload(text, url=None):
    if url is None:
        url = os.environ.get('POSTHASTE_URL', 'https://hastebin.com')
    r = requests.post(f'{url}/documents', data=text.encode('utf-8'))
    r.raise_for_status()
    result = r.json()
    print(f'{url}/{result["key"]}')

def main():
    url = os.environ.get('POSTHASTE_URL', 'https://hastebin.com')

    if not sys.stdin.isatty():
        text = sys.stdin.read()
        if text.strip():
            upload(text, url)
        else:
            print('Error: No input provided.', file=sys.stderr)
            sys.exit(1)
    elif len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                text = f.read()
            upload(text, url)
        except FileNotFoundError:
            print(f'Error: File {sys.argv[1]} not found.', file=sys.stderr)
            sys.exit(1)
    else:
        print('Usage: posthaste < file.txt\n       posthaste filename.txt', file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
