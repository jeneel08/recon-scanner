"""
subfinder_scan.py — Subdomain enumeration using Subfinder
"""

import subprocess
import os
from modules.utils import print_status, Colors


def run(domain: str, out_dir: str, threads: int = 50) -> list[str]:
    """
    Run subfinder and return list of discovered subdomains.
    Output file: <out_dir>/subdomains.txt
    """
    out_file = os.path.join(out_dir, "subdomains.txt")

    cmd = [
        "subfinder",
        "-d", domain,
        "-o", out_file,
        "-t", str(threads),
        "-silent",
        "-all",           # use all sources
    ]

    print_status(f"      CMD: {' '.join(cmd)}", Colors.CYAN)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0 and result.stderr:
            print_status(f"      [WARN] subfinder stderr: {result.stderr.strip()}", Colors.YELLOW)
    except subprocess.TimeoutExpired:
        print_status("      [WARN] subfinder timed out after 5 minutes", Colors.YELLOW)
    except FileNotFoundError:
        print_status("      [ERR] subfinder not found in PATH", Colors.RED)
        return []

    # Read results
    subdomains = []
    if os.path.isfile(out_file):
        with open(out_file) as f:
            subdomains = [line.strip() for line in f if line.strip()]

    # Always include the root domain
    if domain not in subdomains:
        subdomains.insert(0, domain)
        with open(out_file, "w") as f:
            f.write("\n".join(subdomains) + "\n")

    return subdomains
