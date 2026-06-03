"""
httpx_probe.py — HTTP probing using Httpx
Reads subdomains.txt, writes live_hosts.txt
"""

import subprocess
import os
from modules.utils import print_status, Colors


def run(out_dir: str, threads: int = 50, timeout: int = 30) -> list[str]:
    """
    Probe subdomains with httpx and return list of live URLs.
    Reads  : <out_dir>/subdomains.txt
    Writes : <out_dir>/live_hosts.txt
             <out_dir>/httpx_details.json
    """
    in_file   = os.path.join(out_dir, "subdomains.txt")
    out_file  = os.path.join(out_dir, "live_hosts.txt")
    json_file = os.path.join(out_dir, "httpx_details.json")

    if not os.path.isfile(in_file):
        print_status("      [ERR] subdomains.txt not found", Colors.RED)
        return []

    cmd = [
        "httpx",
        "-l",       in_file,
        "-o",       out_file,
        "-json",    "-jo", json_file,
        "-threads", str(threads),
        "-timeout", str(timeout),
        "-silent",
        "-follow-redirects",
        "-status-code",
        "-title",
        "-tech-detect",
        "-web-server",
        "-ip",
    ]

    print_status(f"      CMD: {' '.join(cmd)}", Colors.CYAN)

    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        print_status("      [WARN] httpx timed out", Colors.YELLOW)
    except FileNotFoundError:
        print_status("      [ERR] httpx not found in PATH", Colors.RED)
        return []

    live = []
    if os.path.isfile(out_file):
        with open(out_file) as f:
            live = [line.strip() for line in f if line.strip()]

    return live
