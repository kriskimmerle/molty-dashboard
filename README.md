# 🦞 Molty Status Dashboard

A retro pixel-art dashboard that shows what Molty (autonomous research agent) is doing in real-time.

## Features

- 🎮 **Pixel art aesthetic** with retro styling
- 🦞 **Animated sprite** with different states
- 📊 **Real-time status** from Moltbot logs
- 📝 **Activity log** showing recent actions
- ⏱️ **Session timer** tracking active time
- 🚀 **Project counter** showing shipped projects

## States

The Molty sprite changes based on current activity:

- 💤 **Sleeping** - Idle, waiting for tasks
- 🤔 **Thinking** - Analyzing and planning
- ⌨️ **Coding** - Writing code
- 🔍 **Searching Web** - Researching online
- 🚀 **Pushing to GitHub** - Publishing projects

## Installation

No installation needed! Just Python 3.

## Usage

### Start the dashboard

```bash
chmod +x server.py
./server.py
```

Or:

```bash
python3 server.py
```

The dashboard will open on `http://localhost:8789`

### How it works

The server:
1. Reads Moltbot logs from `/tmp/moltbot/moltbot-*.log`
2. Parses activity to detect current state
3. Serves a web dashboard with live updates
4. Updates every 2 seconds

## Screenshots

```
    ___
   /• •\
  (  <  )
   \_=_/
   ⌨| |⌨
   _| |_
   
   ⌨️ Coding
```

## Dashboard Layout

- **Header**: Molty branding
- **Sprite Panel**: Animated character showing current state
- **Info Panel**: Stats (current activity, last action, session time, projects shipped)
- **Activity Log**: Recent 10 actions from logs
- **Footer**: Connection status

## Tech Stack

- **Frontend**: HTML, CSS, vanilla JavaScript
- **Backend**: Python 3 (http.server)
- **Styling**: Press Start 2P pixel font
- **Data Source**: Moltbot logs in `/tmp/moltbot/`

## Customization

### Change the port

Edit `server.py` line:
```python
port = 8789  # Change to your preferred port
```

### Add new states

Edit `dashboard.js` to add new states:
```javascript
STATES.myNewState = {
    emoji: '🎯',
    label: 'My State',
    art: `your ASCII art here`
};
```

Then update `server.py` to detect the new state in logs.

### Modify detection patterns

Edit `parse_log_file()` in `server.py` to change how states are detected from logs.

## Files

- `index.html` - Dashboard UI
- `style.css` - Retro pixel art styling
- `dashboard.js` - Frontend logic and animations
- `server.py` - Backend server and log parser

## Requirements

- Python 3.6+
- A browser
- Moltbot running (to see live activity)

## Tips

- Leave the dashboard open while Molty is working
- Perfect for streaming or presentations
- Use as a desktop widget via browser window
- Can be extended to show on external displays

## Future Ideas

- [ ] Desktop menubar app version (Swift/Electron)
- [ ] Sound effects for state changes
- [ ] Historical charts (activity over time)
- [ ] Multiple sprite styles to choose from
- [ ] Dark/light theme toggle
- [ ] Export activity reports
- [ ] Integration with system notifications
- [ ] Support for multiple agents

## License

MIT
