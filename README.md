# Scribd Downloader (scribdl-py) 📄

> Simple tool to save Scribd documents and embeds as PDF files.

![Version](https://img.shields.io/badge/version-3.1.0-purple.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Scribd Downloader (scribdl-py)** is a CLI tool that helps you save Scribd documents and embeds into high-quality PDF files for offline reading. It uses a headless browser engine with Smart Waiting to capture every page accurately and smoothly.

---

### ⚠️ Legal Disclaimer

This tool is intended for personal archival of documents you already have legal access to. Please respect Scribd's Terms of Service and the intellectual property of the authors. The developers are not responsible for any misuse of this tool.

---

### Key Features

- **Smart Waiting**: Automatically verifies image assets and rendering status before capturing each page to prevent blank/white output.
- **Auto-Organized Output**: Downloaded PDFs are neatly saved into the `output/` folder by default.
- **Safe Naming**: Automatically sanitizes filenames so they work flawlessly across Windows, Mac, and Linux.
- **Reliable Cleanup**: Temporary files are handled safely and automatically cleaned up, even if you stop the script midway.
- **High Quality**: Saves pages in HD for better reading and printing.
- **Pick Pages**: Download the whole file or just specific pages (e.g., `1-10`).
- **Join PDF**: Combines all captured pages into a single, clean PDF file.
- **History Log**: Keeps a record of each download in `history.json`.

---

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

---

### Usage

Simply run the script with the document URL:

```bash
python main.py <enter>
# or
python main.py "SCRIBD_URL"
```

**CLI Options:**

- `-o, --output`: Custom output filename.
- `-p, --pages` : Page selection (`all`, `3`, or `1-10`).
- `-d, --delay` : Custom extra delay per page in seconds (e.g., `0.5`).
- `-s, --scale` : Scale factor (`1` for SD, `2` for HD).
- `-q, --quiet` : Disable progress output (silent mode).

**Example:**

```bash
python main.py "https://www.scribd.com/document/402293816/Technics-SA-EH550-pdf" --pages "1-10" --delay 0.5
```

---

### ⚙️ Configuration (`config.ini`)

You can set permanent default options in `config.ini` so you don't need to specify CLI flags every time:

```ini
[SETTINGS]
# Baseline extra delay per page capture in seconds (default: 0.5)
delay = 0.5

# Scale factor for page capture (2 = HD quality, 1 = Standard quality)
scale = 2

# Default output filename (Leave empty to auto-detect document title)
output = 
```

---

### Supported Contents

- [x] Scribd Document
- [x] Scribd Embeds

---

### 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the [issues page](https://github.com/coflyn/scribdl-py/issues) if you want to contribute.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Don't forget to give a ⭐ if you find this project useful!

---

### 🐛 Issue Reporting & Support

Found a bug, broken link extraction, or script error?
Please feel free to open an issue with the error traceback and the target URL:

👉 **[Open an Issue on GitHub](https://github.com/coflyn/scribdl-py/issues)**

---

### 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
