"""
utils.py — Shared helpers: colors, banner, tool checker, status printer
"""

import shutil
import sys


class Colors:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"


def print_status(msg: str, color: str = Colors.RESET):
    print(f"{color}{msg}{Colors.RESET}")


def banner():
    art = f"""
{Colors.CYAN}{Colors.BOLD}
 █████╗ ██╗   ██╗████████╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
███████║██║   ██║   ██║   ██║   ██║██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██║██║   ██║   ██║   ██║   ██║██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
{Colors.RESET}
{Colors.YELLOW}  Automated Recon Scanner  |  Bug Bounty & Web Security Testing
  Tools: Subfinder • Httpx • Nmap • FFUF • Nuclei
{Colors.RESET}"""
    print(art)


REQUIRED_TOOLS = {
    "subfinder": "https://github.com/projectdiscovery/subfinder",
    "httpx":     "https://github.com/projectdiscovery/httpx",
    "nmap":      "https://nmap.org/download",
    "ffuf":      "https://github.com/ffuf/ffuf",
    "nuclei":    "https://github.com/projectdiscovery/nuclei",
}


def check_tools():
    print_status("Checking required tools...", Colors.CYAN)
    missing = []
    for tool, url in REQUIRED_TOOLS.items():
        if shutil.which(tool):
            print_status(f"  [✓] {tool}", Colors.GREEN)
        else:
            print_status(f"  [✗] {tool} — install: {url}", Colors.RED)
            missing.append(tool)

    if missing:
        print_status(
            f"\n  Missing tools: {', '.join(missing)}\n"
            f"  Run: bash install.sh   to install everything.\n",
            Colors.RED
        )
        sys.exit(1)
    print()
