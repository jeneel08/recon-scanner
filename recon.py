#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════╗
║         AutoRecon - Automated Recon Scanner           ║
║   Subdomain | Ports | Dirs | Vulns - All in One       ║
╚═══════════════════════════════════════════════════════╝
"""

import argparse
import os
import sys
import time
import json
from datetime import datetime
from modules import (
    subfinder_scan,
    httpx_probe,
    nmap_scan,
    ffuf_scan,
    nuclei_scan,
    reporter
)
from modules.utils import banner, check_tools, Colors, print_status

def parse_args():
    parser = argparse.ArgumentParser(
        description="AutoRecon - Automated Bug Bounty Recon Scanner",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-d", "--domain",    required=True,  help="Target domain (e.g. example.com)")
    parser.add_argument("-o", "--output",    default="output", help="Output directory (default: output)")
    parser.add_argument("-w", "--wordlist",  default="wordlists/common.txt", help="Wordlist for directory fuzzing")
    parser.add_argument("--skip-subdomain",  action="store_true", help="Skip subdomain enumeration")
    parser.add_argument("--skip-httpx",      action="store_true", help="Skip HTTP probing")
    parser.add_argument("--skip-nmap",       action="store_true", help="Skip port scanning")
    parser.add_argument("--skip-ffuf",       action="store_true", help="Skip directory fuzzing")
    parser.add_argument("--skip-nuclei",     action="store_true", help="Skip vulnerability scanning")
    parser.add_argument("--threads",         type=int, default=50, help="Number of threads (default: 50)")
    parser.add_argument("--timeout",         type=int, default=30, help="Timeout in seconds (default: 30)")
    parser.add_argument("--rate-limit",      type=int, default=150, help="Requests per second (default: 150)")
    parser.add_argument("--severity",        default="critical,high,medium", help="Nuclei severity filter")
    return parser.parse_args()


def main():
    args = parse_args()
    banner()
    
    # --- Check required tools ---
    check_tools()

    domain  = args.domain.strip().lower().removeprefix("http://").removeprefix("https://").split("/")[0]
    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.output, f"{domain}_{ts}")
    os.makedirs(out_dir, exist_ok=True)

    print_status(f"Target  : {domain}", Colors.CYAN)
    print_status(f"Output  : {out_dir}", Colors.CYAN)
    print_status(f"Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", Colors.CYAN)

    results = {
        "domain":     domain,
        "timestamp":  ts,
        "subdomains": [],
        "live_hosts": [],
        "open_ports": {},
        "directories":[],
        "vulns":      []
    }

    # ── Step 1 : Subdomain Enumeration ───────────────────────────────────────
    if not args.skip_subdomain:
        print_status("[1/5] Subdomain Enumeration (Subfinder)", Colors.YELLOW)
        subs = subfinder_scan.run(domain, out_dir, args.threads)
        results["subdomains"] = subs
        print_status(f"      Found {len(subs)} subdomains\n", Colors.GREEN)
    else:
        # If skipped, treat the domain itself as the only target
        subs_file = os.path.join(out_dir, "subdomains.txt")
        with open(subs_file, "w") as f:
            f.write(domain + "\n")
        results["subdomains"] = [domain]
        print_status("[1/5] Subdomain enumeration skipped\n", Colors.YELLOW)

    # ── Step 2 : HTTP Probing ─────────────────────────────────────────────────
    if not args.skip_httpx:
        print_status("[2/5] HTTP Probing (Httpx)", Colors.YELLOW)
        live = httpx_probe.run(out_dir, args.threads, args.timeout)
        results["live_hosts"] = live
        print_status(f"      {len(live)} live hosts\n", Colors.GREEN)
    else:
        results["live_hosts"] = [f"https://{domain}"]
        print_status("[2/5] HTTP probing skipped\n", Colors.YELLOW)

    # ── Step 3 : Port Scanning ────────────────────────────────────────────────
    if not args.skip_nmap:
        print_status("[3/5] Port Scanning (Nmap)", Colors.YELLOW)
        ports = nmap_scan.run(domain, out_dir)
        results["open_ports"] = ports
        total_ports = sum(len(v) for v in ports.values())
        print_status(f"      {total_ports} open ports found\n", Colors.GREEN)
    else:
        print_status("[3/5] Port scanning skipped\n", Colors.YELLOW)

    # ── Step 4 : Directory Fuzzing ────────────────────────────────────────────
    if not args.skip_ffuf:
        print_status("[4/5] Directory Fuzzing (FFUF)", Colors.YELLOW)
        if not os.path.isfile(args.wordlist):
            print_status(f"      Wordlist not found: {args.wordlist} — skipping FFUF", Colors.RED)
        else:
            dirs = ffuf_scan.run(results["live_hosts"], out_dir, args.wordlist,
                                 args.threads, args.rate_limit)
            results["directories"] = dirs
            print_status(f"      {len(dirs)} paths discovered\n", Colors.GREEN)
    else:
        print_status("[4/5] Directory fuzzing skipped\n", Colors.YELLOW)

    # ── Step 5 : Vulnerability Scanning ──────────────────────────────────────
    if not args.skip_nuclei:
        print_status("[5/5] Vulnerability Scanning (Nuclei)", Colors.YELLOW)
        vulns = nuclei_scan.run(out_dir, args.threads, args.severity)
        results["vulns"] = vulns
        print_status(f"      {len(vulns)} findings\n", Colors.GREEN)
    else:
        print_status("[5/5] Vulnerability scanning skipped\n", Colors.YELLOW)

    # ── Final Report ──────────────────────────────────────────────────────────
    print_status("Generating report...", Colors.CYAN)
    reporter.generate(results, out_dir)

    print(f"\n{Colors.GREEN}{'═'*55}")
    print(f"  Scan Complete! Results saved to: {out_dir}")
    print(f"{'═'*55}{Colors.RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
