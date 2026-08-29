<p align="center">
  <img src="assets/scribd_logo.png" alt="Scribd" width="350">
</p>

<h1 align="center">Scribd Downloader</h1>

<p align="center">
  <b>Save Scribd documents and embeds as PDF files for offline reading.</b>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  </a>
  <a href="https://playwright.dev/python/">
    <img src="https://img.shields.io/badge/Playwright-1.58+-green?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge" alt="MIT License">
  </a>
</p>

---

## Features

- **Automated Capture** - Loads and renders Scribd documents directly via Playwright headless browser
- **Smart Waiting** - Verifies DOM and image rendering status per page to prevent blank outputs
- **Page Selection** - Export the full document or specific page ranges (e.g. `1-10`, `5`)
- **High Resolution** - Configurable scaling factor up to 2x for HD rendering
- **Auto Sanitization** - Cleans document titles to produce safe filenames across OS environments
- **Automatic Cleanup** - Safely purges temporary screen buffers on completion or exit
- **History Tracking** - Maintains a structured download log in `history.json`

---

### ⚠️ Legal Disclaimer

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
