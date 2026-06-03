"""
reporter.py — Generate HTML and JSON summary reports
"""

import os
import json
from datetime import datetime
from modules.utils import print_status, Colors


def generate(results: dict, out_dir: str):
    """Write JSON summary + HTML report to out_dir."""
    _write_json(results, out_dir)
    _write_html(results, out_dir)
    print_status(f"      Reports: {out_dir}/report.html", Colors.GREEN)
    print_status(f"               {out_dir}/summary.json", Colors.GREEN)


# ── JSON ──────────────────────────────────────────────────────────────────────

def _write_json(results: dict, out_dir: str):
    path = os.path.join(out_dir, "summary.json")
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


# ── HTML ──────────────────────────────────────────────────────────────────────

def _write_html(results: dict, out_dir: str):
    domain    = results.get("domain", "unknown")
    ts        = results.get("timestamp", "")
    subs      = results.get("subdomains", [])
    live      = results.get("live_hosts", [])
    ports     = results.get("open_ports", {})
    dirs      = results.get("directories", [])
    vulns     = results.get("vulns", [])

    # Severity colour map
    sev_color = {
        "critical": "#e74c3c",
        "high":     "#e67e22",
        "medium":   "#f1c40f",
        "low":      "#2ecc71",
        "info":     "#3498db",
    }

    def badge(sev: str) -> str:
        c = sev_color.get(sev.lower(), "#95a5a6")
        return f'<span style="background:{c};color:#fff;padding:2px 8px;border-radius:3px;font-size:0.8em;font-weight:bold">{sev.upper()}</span>'

    # Build sections
    sub_rows = "\n".join(f"<tr><td>{s}</td></tr>" for s in subs) or "<tr><td>None found</td></tr>"
    live_rows = "\n".join(f"<tr><td><a href='{h}' target='_blank'>{h}</a></td></tr>" for h in live) or "<tr><td>None found</td></tr>"

    port_rows = ""
    for host, plist in ports.items():
        for p in plist:
            port_rows += f"<tr><td>{host}</td><td>{p['port']}/{p['proto']}</td><td>{p['service']}</td><td>{p['version']}</td></tr>"
    if not port_rows:
        port_rows = "<tr><td colspan='4'>No open ports found</td></tr>"

    dir_rows = ""
    for d in dirs:
        dir_rows += f"<tr><td><a href='{d['url']}' target='_blank'>{d['url']}</a></td><td>{d['status']}</td><td>{d['length']}</td></tr>"
    if not dir_rows:
        dir_rows = "<tr><td colspan='3'>No paths discovered</td></tr>"

    vuln_rows = ""
    for v in vulns:
        vuln_rows += f"<tr><td>{badge(v['severity'])}</td><td>{v['name']}</td><td><a href='{v['matched']}' target='_blank'>{v['matched']}</a></td><td>{v['template']}</td></tr>"
    if not vuln_rows:
        vuln_rows = "<tr><td colspan='4'>No vulnerabilities found</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>AutoRecon Report — {domain}</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Segoe UI',Arial,sans-serif;background:#0f1117;color:#e0e0e0;padding:20px}}
    h1{{color:#00d2ff;font-size:1.8em;margin-bottom:4px}}
    .subtitle{{color:#888;margin-bottom:24px;font-size:0.9em}}
    .stats{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:28px}}
    .stat-card{{background:#1a1d27;border:1px solid #2a2d3a;border-radius:8px;padding:16px 24px;min-width:130px;text-align:center}}
    .stat-card .num{{font-size:2em;font-weight:bold;color:#00d2ff}}
    .stat-card .lbl{{font-size:0.8em;color:#888;margin-top:4px}}
    h2{{color:#00d2ff;font-size:1.1em;margin:24px 0 10px;border-bottom:1px solid #2a2d3a;padding-bottom:6px}}
    table{{width:100%;border-collapse:collapse;background:#1a1d27;border-radius:6px;overflow:hidden;margin-bottom:8px}}
    th{{background:#12141e;color:#00d2ff;padding:10px 14px;text-align:left;font-size:0.85em}}
    td{{padding:9px 14px;font-size:0.85em;border-bottom:1px solid #22253a;word-break:break-all}}
    tr:last-child td{{border-bottom:none}}
    tr:hover td{{background:#1e2130}}
    a{{color:#00d2ff;text-decoration:none}}
    a:hover{{text-decoration:underline}}
    .footer{{margin-top:32px;color:#555;font-size:0.8em;text-align:center}}
  </style>
</head>
<body>
  <h1>🔍 AutoRecon Report</h1>
  <div class="subtitle">Target: <strong>{domain}</strong> &nbsp;|&nbsp; Scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

  <div class="stats">
    <div class="stat-card"><div class="num">{len(subs)}</div><div class="lbl">Subdomains</div></div>
    <div class="stat-card"><div class="num">{len(live)}</div><div class="lbl">Live Hosts</div></div>
    <div class="stat-card"><div class="num">{sum(len(v) for v in ports.values())}</div><div class="lbl">Open Ports</div></div>
    <div class="stat-card"><div class="num">{len(dirs)}</div><div class="lbl">Directories</div></div>
    <div class="stat-card"><div class="num">{len(vulns)}</div><div class="lbl">Findings</div></div>
  </div>

  <h2>📋 Subdomains ({len(subs)})</h2>
  <table><thead><tr><th>Subdomain</th></tr></thead><tbody>{sub_rows}</tbody></table>

  <h2>🌐 Live Hosts ({len(live)})</h2>
  <table><thead><tr><th>URL</th></tr></thead><tbody>{live_rows}</tbody></table>

  <h2>🔌 Open Ports</h2>
  <table>
    <thead><tr><th>Host</th><th>Port</th><th>Service</th><th>Version</th></tr></thead>
    <tbody>{port_rows}</tbody>
  </table>

  <h2>📁 Discovered Paths ({len(dirs)})</h2>
  <table>
    <thead><tr><th>URL</th><th>Status</th><th>Size</th></tr></thead>
    <tbody>{dir_rows}</tbody>
  </table>

  <h2>⚠️ Vulnerabilities ({len(vulns)})</h2>
  <table>
    <thead><tr><th>Severity</th><th>Name</th><th>Matched At</th><th>Template</th></tr></thead>
    <tbody>{vuln_rows}</tbody>
  </table>

  <div class="footer">Generated by AutoRecon &nbsp;•&nbsp; For authorized security testing only</div>
</body>
</html>"""

    path = os.path.join(out_dir, "report.html")
    with open(path, "w") as f:
        f.write(html)
