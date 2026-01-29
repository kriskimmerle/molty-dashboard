# Molty Dashboard

A real-time status dashboard for an autonomous research agent. Shows what Molty is doing right now, which projects have shipped, and aggregate stats — all in a clean dark UI.

![status](https://img.shields.io/badge/version-2.0-6c5ce7)

## Features

- **Live status orb** — radiating orb changes colour by state (sleeping, thinking, coding, researching, publishing)
- **Project gallery** — every shipped project with name, description, stack, date, and GitHub link (parsed from `research/published.md`)
- **Aggregate stats** — total projects, commits, and lines of code across all repos
- **Activity feed** — recent actions streamed from Moltbot logs
- **Session timer** — how long the current session has been running

## Quick Start

```bash
cd projects/molty-dashboard
python3 server.py
# → open http://localhost:8790
```

Set a custom port:

```bash
PORT=9000 python3 server.py
```

## How It Works

```
browser ──poll──▶ /api/status   ← parses /tmp/moltbot/moltbot-*.log
                  /api/projects ← parses ~/clawd/research/published.md
                  /api/stats    ← runs git rev-list + wc across project repos
```

The backend is a zero-dependency Python `http.server`. The frontend is vanilla HTML/CSS/JS with the Inter font loaded from Google Fonts.

## States

| State | Orb colour | Trigger |
|-------|-----------|---------|
| Sleeping | Grey | Idle / no recent log activity |
| Thinking | Amber | Analyzing, planning |
| Coding | Purple | Writing `.py`, `.js`, `.ts`, `.html`, `.css` files |
| Researching | Blue | `web_search` or `web_fetch` calls |
| Publishing | Green | `git push`, `gh repo create` |

## API

| Endpoint | Returns |
|----------|---------|
| `GET /api/status` | `{ state, activity, lastAction, logs[] }` |
| `GET /api/projects` | `[ { name, date, repo, description, stack, status } ]` |
| `GET /api/stats` | `{ projects, commits, loc }` |

Stats are cached for 30 seconds.

## Tech

- **Backend**: Python 3.6+ stdlib (`http.server`, `json`, `subprocess`)
- **Frontend**: HTML, CSS, vanilla JS
- **Font**: [Inter](https://rsms.me/inter/) via Google Fonts
- **Dependencies**: None

## Requirements

- Python 3.6+
- Moltbot running (for live status; the project gallery works regardless)

## License

MIT
