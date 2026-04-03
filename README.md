# scribdl-py 📄

> Simple Scribd document and embed archiver.

![Version](https://img.shields.io/badge/version-1.0.0-purple.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**scribdl-py** is a CLI tool that helps you save Scribd documents and embeds into high-quality PDF files. It uses a headless browser engine to capture every page accurately.

---

### ⚠️ Legal Disclaimer

This tool is intended for personal archival of documents you already have legal access to. Please respect Scribd's Terms of Service and the intellectual property of the authors. The developers are not responsible for any misuse of this tool.

---

### Key Features

- **Capture Monitoring**: Detects page loading states for clean captures.
- **HD Scaling**: Captures at 2.0x factor for better readability.
- **PDF Synthesis**: Merges all captured frames into a single PDF.
- **Header Blocks**: Skips intrusive analytics and cookie banners.

### Installation

1. **Clone & Setup Environment**

   ```bash
   git clone https://github.com/nezrt/scribdl-py.git
   cd scribdl-py
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

### Usage

Simply run the script with the document URL:

```bash
python main.py "SCRIBD_URL"
```

**Custom Settings:**
All default settings (delay, scale, output) can be configured in `config.ini`. You can also override them via CLI:

- `-o, --output`: Custom output filename.
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
