#!/usr/bin/env bash
# ============================================================
#  AutoRecon — Tool Installer
#  Installs: Go, Subfinder, Httpx, FFUF, Nuclei, Nmap
#  Tested on: Ubuntu / Debian / Kali Linux
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[*] $1${NC}"; }
ok()    { echo -e "${GREEN}[✓] $1${NC}"; }
warn()  { echo -e "${YELLOW}[!] $1${NC}"; }
error() { echo -e "${RED}[✗] $1${NC}"; exit 1; }

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║   AutoRecon Tool Installer           ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

# ── Privileges ──────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
  warn "Not running as root. Some installs may require sudo."
fi

# ── System deps ─────────────────────────────────────────────
info "Updating packages and installing base deps..."
sudo apt-get update -qq
sudo apt-get install -y -qq nmap python3 python3-pip curl wget unzip git 2>/dev/null
ok "System packages installed"

# ── Go ───────────────────────────────────────────────────────
install_go() {
  if command -v go &>/dev/null; then
    ok "Go already installed ($(go version | awk '{print $3}'))"
    return
  fi
  info "Installing Go..."
  GO_VER="1.22.4"
  ARCH=$(uname -m)
  [[ "$ARCH" == "x86_64" ]] && GOARCH="amd64" || GOARCH="arm64"
  wget -q "https://go.dev/dl/go${GO_VER}.linux-${GOARCH}.tar.gz" -O /tmp/go.tar.gz
  sudo rm -rf /usr/local/go
  sudo tar -C /usr/local -xzf /tmp/go.tar.gz
  rm /tmp/go.tar.gz

  # Add to PATH
  if ! grep -q "/usr/local/go/bin" ~/.bashrc; then
    echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
  fi
  export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
  ok "Go ${GO_VER} installed"
}

# ── Go-based tools ───────────────────────────────────────────
install_go_tool() {
  local name=$1
  local pkg=$2
  if command -v "$name" &>/dev/null; then
    ok "$name already installed"
    return
  fi
  info "Installing $name..."
  export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
  go install "$pkg"@latest 2>/dev/null
  ok "$name installed"
}

install_go
install_go_tool "subfinder" "github.com/projectdiscovery/subfinder/v2/cmd/subfinder"
install_go_tool "httpx"     "github.com/projectdiscovery/httpx/cmd/httpx"
install_go_tool "ffuf"      "github.com/ffuf/ffuf/v2"
install_go_tool "nuclei"    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei"

# ── Python deps ──────────────────────────────────────────────
info "Installing Python dependencies..."
pip3 install -r requirements.txt -q
ok "Python dependencies installed"

# ── Nuclei templates ─────────────────────────────────────────
export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
if command -v nuclei &>/dev/null; then
  info "Updating Nuclei templates..."
  nuclei -update-templates -silent 2>/dev/null || warn "Could not update nuclei templates"
  ok "Nuclei templates updated"
fi

# ── Wordlist ─────────────────────────────────────────────────
WORDLIST="wordlists/common.txt"
if [[ ! -f "$WORDLIST" ]]; then
  info "Downloading directory wordlist..."
  mkdir -p wordlists
  curl -sL "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt" \
    -o "$WORDLIST"
  ok "Wordlist saved to $WORDLIST"
fi

# ── Final check ──────────────────────────────────────────────
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
info "Tool check:"
for tool in subfinder httpx nmap ffuf nuclei; do
  if command -v "$tool" &>/dev/null; then
    ok "  $tool"
  else
    warn "  $tool — NOT found (may need: source ~/.bashrc)"
  fi
done
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}  Installation complete!${NC}"
echo -e "  Run: ${CYAN}source ~/.bashrc${NC}  (reload PATH)"
echo -e "  Run: ${CYAN}python3 recon.py -d example.com${NC}"
echo ""
