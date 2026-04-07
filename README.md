# Scribd Downloader (scribdl-py) 📄

> Simple tool to save Scribd documents and embeds as PDF files.

![Version](https://img.shields.io/badge/version-3.0.0-purple.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Scribd Downloader (scribdl-py)** is a CLI tool that helps you save Scribd documents and embeds into high-quality PDF files for offline reading. It uses a headless browser engine to capture every page accurately and smoothly.

---

### ⚠️ Legal Disclaimer

This tool is intended for personal archival of documents you already have legal access to. Please respect Scribd's Terms of Service and the intellectual property of the authors. The developers are not responsible for any misuse of this tool.

---

### Key Features

- **Smart Waiting**: Automatically checks if the page is ready before saving.
- **High Quality**: Saves pages in HD for better reading and printing.
- **Pick Pages**: Download the whole file or just a few pages (e.g. `1-10`).
- **Join PDF**: Combines all pages into a single, clean PDF file.
- **Clean View**: Automatically hides annoying pop-ups and cookie banners.
- **History Log**: Keeps a record of each download in `history.json`.

### Installation

1. **Clone & Setup Environment**

   ```bash
   git clone https://github.com/coflyn/scribdl-py.git
   cd scribdl-py
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

### Usage

Simply run the script with the document URL:

```bash
python main.py <enter>
or
python main.py "SCRIBD_URL"
```

**Custom Settings:**
All default settings can be configured in `config.ini`. You can also override them via CLI:

- `-o, --output`: Custom output filename.
- `-p, --pages` : Page selection (`all` or `1-10`).
- `-d, --delay` : Custom delay per page (seconds).
- `-s, --scale` : Scale factor (1 or 2).

**Example:**

```bash
python main.py "https://www.scribd.com/document/..." --delay 1.0
```

---

### Supported Contents

- [x] Scribd Document
- [x] Scribd Embeds

---

### 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
