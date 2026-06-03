"""
ffuf_scan.py — Directory/path discovery using FFUF
"""

import subprocess
import os
import json
from modules.utils import print_status, Colors


def run(live_hosts: list, out_dir: str, wordlist: str,
        threads: int = 50, rate: int = 150) -> list[dict]:
    """
    Run FFUF on each live host.
    Returns list of discovered paths across all hosts.
    Writes: <out_dir>/ffuf_<host>.json for each host
    """
    all_findings = []
    ffuf_dir = os.path.join(out_dir, "ffuf")
    os.makedirs(ffuf_dir, exist_ok=True)

    # Limit to first 10 hosts to avoid excessive runtime
    targets = live_hosts[:10]

    for host in targets:
        safe_name = host.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "_")
        out_file  = os.path.join(ffuf_dir, f"{safe_name}.json")

        # Ensure URL ends with /
        url = host.rstrip("/") + "/FUZZ"

        cmd = [
            "ffuf",
            "-u",        url,
            "-w",        wordlist,
            "-o",        out_file,
            "-of",       "json",
            "-t",        str(threads),
            "-rate",     str(rate),
            "-mc",       "200,201,204,301,302,307,401,403,405",  # match codes
            "-ac",       # auto-calibrate
            "-s",        # silent (no progress bar)
        ]

        print_status(f"      Fuzzing: {host}", Colors.CYAN)

        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            print_status(f"      [WARN] ffuf timed out on {host}", Colors.YELLOW)
            continue
        except FileNotFoundError:
            print_status("      [ERR] ffuf not found in PATH", Colors.RED)
            return []

        # Parse results
        findings = parse_ffuf_json(out_file, host)
        all_findings.extend(findings)

    return all_findings


def parse_ffuf_json(json_file: str, host: str) -> list[dict]:
    """Parse ffuf JSON output into list of path dicts."""
    findings = []
    if not os.path.isfile(json_file):
        return findings

    try:
        with open(json_file) as f:
            data = json.load(f)
        for result in data.get("results", []):
            findings.append({
                "url":    result.get("url"),
                "host":   host,
                "status": result.get("status"),
                "length": result.get("length"),
                "words":  result.get("words"),
            })
    except (json.JSONDecodeError, KeyError):
        pass

    return findings
