#!/usr/bin/env python3
"""
Molty Dashboard v2 — Server
Serves the dashboard and provides real-time status + project data.
"""

import json
import os
import re
import subprocess
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional

CLAWD = Path.home() / "clawd"
PUBLISHED_MD = CLAWD / "research" / "published.md"
PROJECTS_DIR = CLAWD / "projects"


# ── Project parser ─────────────────────────────────────────────────────────

def parse_published() -> List[Dict[str, Any]]:
    """Parse research/published.md into structured project objects."""
    if not PUBLISHED_MD.exists():
        return []

    text = PUBLISHED_MD.read_text()
    # Split on level-2 headings that look like project entries
    raw_sections = re.split(r"(?=^## \w)", text, flags=re.MULTILINE)

    projects: List[Dict[str, Any]] = []
    for sec in raw_sections:
        sec = sec.strip()
        if not sec.startswith("## "):
            continue

        header_match = re.match(r"^## (.+?)(?:\s*\((.+?)\))?\s*$", sec, re.MULTILINE)
        if not header_match:
            continue

        name = header_match.group(1).strip()
        date = header_match.group(2) or ""

        repo = ""
        m = re.search(r"\*\*Repo:\*\*\s*(https?://\S+)", sec)
        if m:
            repo = m.group(1).strip()

        what = ""
        m = re.search(r"\*\*What:\*\*\s*(.+?)(?:\n\n|\n\*\*)", sec, re.DOTALL)
        if m:
            what = m.group(1).strip()

        stack = ""
        m = re.search(r"\*\*Stack:\*\*\s*(.+)", sec)
        if m:
            stack = m.group(1).strip()

        status = ""
        m = re.search(r"\*\*Status:\*\*\s*(.+)", sec)
        if m:
            status = m.group(1).strip()

        projects.append({
            "name": name,
            "date": date,
            "repo": repo,
            "description": what,
            "stack": stack,
            "status": status,
        })

    return projects


def git_stats() -> Dict[str, int]:
    """Aggregate commit count + rough LOC across project repos."""
    total_commits = 0
    total_loc = 0
    if not PROJECTS_DIR.exists():
        return {"commits": 0, "loc": 0}

    for d in PROJECTS_DIR.iterdir():
        if not d.is_dir() or not (d / ".git").exists():
            continue
        try:
            out = subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=str(d), stderr=subprocess.DEVNULL, text=True,
            )
            total_commits += int(out.strip())
        except Exception:
            pass
        # Rough LOC via wc
        try:
            out = subprocess.check_output(
                "git ls-files | xargs wc -l 2>/dev/null | tail -1",
                cwd=str(d), shell=True, stderr=subprocess.DEVNULL, text=True,
            )
            m = re.match(r"\s*(\d+)", out)
            if m:
                total_loc += int(m.group(1))
        except Exception:
            pass
    return {"commits": total_commits, "loc": total_loc}


# ── Handler ────────────────────────────────────────────────────────────────

class DashboardHandler(SimpleHTTPRequestHandler):
    last_log_pos = 0
    last_log_file: Optional[str] = None
    _stats_cache: Optional[Dict] = None
    _stats_ts: float = 0

    def do_GET(self):
        if self.path == "/api/status":
            return self._json(self._build_status())
        if self.path == "/api/projects":
            return self._json(parse_published())
        if self.path == "/api/stats":
            return self._json(self._cached_stats())
        super().do_GET()

    # ── helpers ──

    def _json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cached_stats(self) -> Dict:
        now = time.time()
        if DashboardHandler._stats_cache is None or now - DashboardHandler._stats_ts > 30:
            DashboardHandler._stats_cache = git_stats()
            DashboardHandler._stats_cache["projects"] = len(parse_published())
            DashboardHandler._stats_ts = now
        return DashboardHandler._stats_cache

    # ── status / log parsing ──

    def _build_status(self) -> Dict:
        log_dir = Path("/tmp/moltbot")
        if not log_dir.exists():
            return self._idle("No logs found")

        log_files = sorted(log_dir.glob("moltbot-*.log"))
        if not log_files:
            return self._idle("Idle")

        return self._parse_log(log_files[-1])

    def _idle(self, msg: str) -> Dict:
        return {
            "state": "sleeping",
            "activity": msg,
            "lastAction": "Waiting for tasks",
            "logs": [],
        }

    def _parse_log(self, log_file: Path) -> Dict:
        cls = DashboardHandler
        if cls.last_log_file != str(log_file):
            cls.last_log_pos = 0
            cls.last_log_file = str(log_file)

        try:
            with open(log_file) as f:
                f.seek(cls.last_log_pos)
                chunk = f.read()
                cls.last_log_pos = f.tell()
        except Exception:
            return self._idle("Error reading logs")

        lines = [l for l in chunk.strip().split("\n") if l.strip()][-50:]

        state = "sleeping"
        activity = "Idle"
        last_action = "No recent activity"
        logs: List[Dict] = []

        for line in reversed(lines):
            m = re.search(r"\[(.*?)\].*?\s+(.*)", line)
            if not m:
                continue
            msg = m.group(2)

            low = line.lower()
            if "web_search" in low or "web_fetch" in low:
                state, activity = "searching", "Researching"
            elif "git push" in low or "gh repo create" in low:
                state, activity = "pushing", "Publishing"
            elif "git commit" in low:
                state, activity = "pushing", "Committing"
            elif re.search(r"\.(py|js|ts|html|css|rs|go)\b", low) and ("write" in low or "edit" in low):
                state, activity = "coding", "Writing code"
            elif "thinking" in low or "analyzing" in low:
                state, activity = "thinking", "Thinking"

            if last_action == "No recent activity":
                last_action = msg[:120]

            if len(logs) < 8:
                kind = "info"
                if "error" in low:
                    kind = "error"
                elif "success" in low or "complete" in low or "shipped" in low:
                    kind = "success"
                logs.append({"message": msg[:200], "type": kind})

        # Go idle if log hasn't been touched in 30s
        try:
            age = time.time() - os.path.getmtime(log_file)
            if age > 30:
                state, activity = "sleeping", "Idle"
        except Exception:
            pass

        return {
            "state": state,
            "activity": activity,
            "lastAction": last_action,
            "logs": logs,
        }

    def log_message(self, fmt, *args):
        pass  # silence


# ── main ───────────────────────────────────────────────────────────────────

def main():
    port = int(os.environ.get("PORT", 8790))
    os.chdir(Path(__file__).parent)
    print(f"\n  Molty Dashboard v2")
    print(f"  http://localhost:{port}\n")
    server = HTTPServer(("localhost", port), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
