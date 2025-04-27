![GitHub commit activity](https://img.shields.io/github/commit-activity/w/ArchooD2/posthaste) ![GitHub contributors](https://img.shields.io/github/contributors-anon/ArchooD2/posthaste) ![GitHub last commit](https://img.shields.io/github/last-commit/ArchooD2/posthaste) ![PyPI - License](https://img.shields.io/pypi/l/posthaste) ![PyPI - Downloads](https://img.shields.io/pypi/dd/posthaste)

---
# posthaste – Hastebin uploads, lightning fast

Based on [ylmcc/AutoHasteBin](https://github.com/ylmcc/AutoHastebin)

`posthaste` is a super-lightweight Python CLI tool for quickly uploading text or files to any Hastebin-compatible server — straight from your terminal.

Perfect for sharing code snippets, logs, notes, and more — without needing to open a browser. Pipe it, upload it, share it — done.

---

## ✨ Features

- Upload directly from stdin or from one or more files
- Supports authentication tokens (optional)
- Save tokens to your environment for later use
- Choose your own Hastebin server
- No dependencies beyond `requests` and my [in-house `argparse` sub-in](https://github.com/ArchooD2/snaparg)
- Blazing fast and easy to use

---

## 📦 Quick Start

- [`pip install posthaste`](https://pypi.org/project/posthaste/)

- then upload text:

```bash
echo "hello world" | posthaste
```

- or upload a file:

```bash
posthaste mylogfile.txt
```

- or upload multiple files:

```bash
posthaste file1.txt file2.txt
```

- save your API token (only needed if the server requires it):

```bash
posthaste --token YOUR_TOKEN_HERE
```

---

## 🔧 Example

```bash
$ echo "my example code" | posthaste
Uploading to: https://hastebin.com/documents
https://hastebin.com/share/abcd1234
```

```bash
$ posthaste error_log.txt
Uploading file: error_log.txt
https://hastebin.com/share/efgh5678
```

---

## 📄 License

This project is licensed under the GPL v3.0 License.  
See the [LICENSE](LICENSE) file for full details.
