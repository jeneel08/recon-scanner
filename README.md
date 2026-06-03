# 🔍 AutoRecon — Automated Reconnaissance Scanner

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Tools](https://img.shields.io/badge/Tools-Subfinder%20%7C%20Httpx%20%7C%20Nmap%20%7C%20FFUF%20%7C%20Nuclei-orange?style=flat-square)](https://github.com)

> **Automated Bug Bounty & Web Security Reconnaissance Toolkit**
> Subdomain Enumeration → HTTP Probing → Port Scanning → Directory Fuzzing → Vulnerability Detection — all in one command.

---

## 📋 Table of Contents
- [Features](#-features)
- [Tool Stack](#-tool-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Output](#-output)
- [Examples](#-examples)
- [Disclaimer](#-disclaimer)

---

## ✨ Features

| Step | Module | Description |
|------|--------|-------------|
| 1 | **Subfinder** | Passive subdomain enumeration using 40+ sources |
| 2 | **Httpx** | HTTP/HTTPS probing, status codes, tech detection |
| 3 | **Nmap** | Port scanning with service/version detection |
| 4 | **FFUF** | Fast directory & path fuzzing with auto-calibration |
| 5 | **Nuclei** | Template-based vulnerability detection |
| 6 | **Reporter** | Auto-generates HTML + JSON summary report |

---

## 🛠 Tool Stack

```
Python 3.10+       Orchestration & reporting
Subfinder          Subdomain enumeration
Httpx              HTTP probing
Nmap               Port scanning
FFUF               Directory fuzzing
Nuclei             Vulnerability scanning
Bash               Install script
```

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/autorecon.git
cd autorecon
```

### 2. Run the installer (Ubuntu / Debian / Kali)
```bash
chmod +x install.sh
bash install.sh
source ~/.bashrc
```

The installer will automatically set up:
- Go (required for ProjectDiscovery tools)
- Subfinder, Httpx, FFUF, Nuclei (Go-based)
- Nmap (apt)
- Common wordlist from SecLists

### 3. Verify installation
```bash
python3 recon.py --help
```

---

## 📖 Usage

### Basic scan
```bash
python3 recon.py -d example.com
```

### Full options
```bash
python3 recon.py -d example.com [OPTIONS]

Options:
  -d, --domain         Target domain (required)
  -o, --output         Output directory (default: output)
  -w, --wordlist       Path to wordlist for FFUF (default: wordlists/common.txt)
  --skip-subdomain     Skip Subfinder
  --skip-httpx         Skip Httpx
  --skip-nmap          Skip Nmap
  --skip-ffuf          Skip FFUF
  --skip-nuclei        Skip Nuclei
  --threads            Thread count (default: 50)
  --timeout            Timeout in seconds (default: 30)
  --rate-limit         Requests per second for FFUF (default: 150)
  --severity           Nuclei severity filter (default: critical,high,medium)
```

### Skip specific modules
```bash
# Only subdomain enum + HTTP probing (fast recon)
python3 recon.py -d example.com --skip-nmap --skip-ffuf --skip-nuclei

# Skip subdomain enum (already have targets)
python3 recon.py -d example.com --skip-subdomain

# Only vulnerability scan (fastest - needs existing live_hosts.txt)
python3 recon.py -d example.com --skip-subdomain --skip-nmap --skip-ffuf
```

---

## 📂 Output

Each scan creates a timestamped folder:

```
output/
└── example.com_20240601_143022/
    ├── subdomains.txt         # All discovered subdomains
    ├── live_hosts.txt         # Probed live URLs
    ├── httpx_details.json     # Httpx full JSON output
    ├── nmap_results.txt       # Nmap text report
    ├── nmap_results.xml       # Nmap XML (machine-readable)
    ├── ffuf/
    │   └── example.com.json   # FFUF results per host
    ├── nuclei_results.txt     # Nuclei findings (text)
    ├── nuclei_results.json    # Nuclei findings (JSON)
    ├── summary.json           # Combined JSON summary
    └── report.html            # ⭐ Visual HTML report
```

Open `report.html` in a browser for a clean dashboard view.

---

## 💡 Examples

```bash
# Bug bounty - full recon on a program target
python3 recon.py -d target.com --severity critical,high

# Quick scan - no vulnerability detection
python3 recon.py -d target.com --skip-nuclei --threads 100

# Use custom wordlist
python3 recon.py -d target.com -w /path/to/big-wordlist.txt

# Save to custom output folder
python3 recon.py -d target.com -o /home/user/bugbounty/target
```

---

## 📁 Project Structure

```
autorecon/
├── recon.py              # Main entry point
├── install.sh            # Tool installer
├── requirements.txt      # Python deps
├── modules/
│   ├── __init__.py
│   ├── utils.py          # Colors, banner, tool checker
│   ├── subfinder_scan.py # Subdomain enumeration
│   ├── httpx_probe.py    # HTTP probing
│   ├── nmap_scan.py      # Port scanning
│   ├── ffuf_scan.py      # Directory fuzzing
│   ├── nuclei_scan.py    # Vulnerability scanning
│   └── reporter.py       # HTML + JSON report generation
├── wordlists/
│   └── common.txt        # Directory wordlist (auto-downloaded)
├── output/               # Scan results (git-ignored)
└── README.md
```

---

## ⚙️ Configuration Tips

**Rate limiting**: Reduce `--rate-limit` on slow targets to avoid being blocked.

**Threads**: Higher threads = faster scan. Keep `--threads 50` for stability.

**Wordlists**: Use bigger lists from [SecLists](https://github.com/danielmiessler/SecLists) for deeper directory fuzzing.

**Nuclei severity**: Set `--severity critical,high` for quick scans, add `medium` for thorough ones.

---

## ⚠️ Disclaimer

> **This tool is intended for authorized security testing and bug bounty programs only.**
> Only scan targets you have explicit permission to test.
> Unauthorized scanning may be illegal in your jurisdiction.
> The author is not responsible for any misuse of this tool.

---

## 📜 License

MIT License — see [LICENSE](LICENSE)

---

## 🤝 Contributing

Pull requests welcome! Please open an issue first for major changes.

```bash
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```
