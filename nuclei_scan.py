"""
nuclei_scan.py — Vulnerability scanning using Nuclei
"""

import subprocess
import os
import json
from modules.utils import print_status, Colors


def run(out_dir: str, threads: int = 50, severity: str = "critical,high,medium") -> list[dict]:
    """
    Run nuclei against live hosts.
    Reads : <out_dir>/live_hosts.txt
    Writes: <out_dir>/nuclei_results.json
            <out_dir>/nuclei_results.txt
    Returns list of vulnerability findings.
    """
    in_file   = os.path.join(out_dir, "live_hosts.txt")
    json_out  = os.path.join(out_dir, "nuclei_results.json")
    txt_out   = os.path.join(out_dir, "nuclei_results.txt")

    if not os.path.isfile(in_file):
        print_status("      [WARN] live_hosts.txt not found — skipping nuclei", Colors.YELLOW)
        return []

    cmd = [
        "nuclei",
        "-l",          in_file,
        "-o",          txt_out,
        "-je",         json_out,       # JSON export
        "-c",          str(threads),
        "-severity",   severity,
        "-silent",
        "-follow-redirects",
        "-no-color",
    ]

    print_status(f"      CMD: {' '.join(cmd)}", Colors.CYAN)
    print_status("      This may take a few minutes...", Colors.YELLOW)

    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    except subprocess.TimeoutExpired:
        print_status("      [WARN] nuclei timed out after 20 minutes", Colors.YELLOW)
    except FileNotFoundError:
        print_status("      [ERR] nuclei not found in PATH", Colors.RED)
        return []

    return parse_nuclei_json(json_out)


def parse_nuclei_json(json_file: str) -> list[dict]:
    """
    Parse nuclei JSON export (newline-delimited JSON).
    Returns list of finding dicts.
    """
    findings = []
    if not os.path.isfile(json_file):
        return findings

    with open(json_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                findings.append({
                    "template":  item.get("template-id", ""),
                    "name":      item.get("info", {}).get("name", ""),
                    "severity":  item.get("info", {}).get("severity", ""),
                    "host":      item.get("host", ""),
                    "matched":   item.get("matched-at", ""),
                    "tags":      item.get("info", {}).get("tags", []),
                    "reference": item.get("info", {}).get("reference", []),
                })
            except json.JSONDecodeError:
                continue

    return findings
