"""
nmap_scan.py — Port scanning using Nmap
"""

import subprocess
import os
import xml.etree.ElementTree as ET
from modules.utils import print_status, Colors


def run(domain: str, out_dir: str) -> dict:
    """
    Run nmap against the target domain.
    Returns dict: { host: [open_ports] }
    Writes: <out_dir>/nmap_results.xml
            <out_dir>/nmap_results.txt
    """
    xml_out  = os.path.join(out_dir, "nmap_results.xml")
    txt_out  = os.path.join(out_dir, "nmap_results.txt")

    cmd = [
        "nmap",
        "-sV",           # service/version detection
        "-sC",           # default scripts
        "--open",        # only show open ports
        "-T4",           # aggressive timing
        "-p", "21,22,23,25,53,80,110,143,443,445,993,995,3306,3389,5432,5900,6379,8080,8443,8888,9200,27017",
        "-oX", xml_out,
        "-oN", txt_out,
        domain,
    ]

    print_status(f"      CMD: {' '.join(cmd)}", Colors.CYAN)

    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        print_status("      [WARN] nmap timed out", Colors.YELLOW)
    except FileNotFoundError:
        print_status("      [ERR] nmap not found in PATH", Colors.RED)
        return {}

    return parse_nmap_xml(xml_out)


def parse_nmap_xml(xml_file: str) -> dict:
    """Parse nmap XML output into { host: [port_info] }"""
    results = {}
    if not os.path.isfile(xml_file):
        return results

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for host_el in root.findall("host"):
            # Get IP or hostname
            addr_el = host_el.find("address[@addrtype='ipv4']")
            host_name_el = host_el.find(".//hostname[@type='user']")
            host_key = (host_name_el.get("name") if host_name_el is not None
                        else addr_el.get("addr") if addr_el is not None
                        else "unknown")

            ports_info = []
            for port_el in host_el.findall(".//port"):
                state_el = port_el.find("state")
                if state_el is None or state_el.get("state") != "open":
                    continue
                svc_el = port_el.find("service")
                portid  = port_el.get("portid")
                proto   = port_el.get("protocol")
                service = svc_el.get("name", "unknown")     if svc_el is not None else "unknown"
                version = svc_el.get("product", "")         if svc_el is not None else ""
                version += " " + svc_el.get("version", "")  if svc_el is not None else ""
                ports_info.append({
                    "port":    portid,
                    "proto":   proto,
                    "service": service,
                    "version": version.strip(),
                })

            if ports_info:
                results[host_key] = ports_info

    except ET.ParseError as e:
        print_status(f"      [WARN] Could not parse nmap XML: {e}", Colors.YELLOW)

    return results
