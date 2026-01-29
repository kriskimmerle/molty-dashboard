#!/usr/bin/env python3
"""
Molty Status Dashboard Server
Serves the dashboard and provides real-time status from Moltbot logs
"""

import json
import os
import re
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, List, Optional


class MoltyStatusHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the dashboard"""
    
    # Track last log position
    last_log_position = 0
    last_log_file = None
    session_start = time.time()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/status':
            self.send_json_response(self.get_status())
        else:
            # Serve static files
            super().do_GET()
    
    def send_json_response(self, data: Dict):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_status(self) -> Dict:
        """Get current Molty status"""
        # Find latest log file
        log_dir = Path('/tmp/moltbot')
        
        if not log_dir.exists():
            return {
                'state': 'sleeping',
                'activity': 'No logs found',
                'lastAction': 'Moltbot not running?',
                'projectsShipped': self.count_shipped_projects(),
                'newLogs': []
            }
        
        # Find most recent log file
        log_files = sorted(log_dir.glob('moltbot-*.log'))
        if not log_files:
            return {
                'state': 'sleeping',
                'activity': 'Idle',
                'lastAction': 'No recent activity',
                'projectsShipped': self.count_shipped_projects(),
                'newLogs': []
            }
        
        latest_log = log_files[-1]
        
        # Detect state from recent log activity
        state, activity, last_action, new_logs = self.parse_log_file(latest_log)
        
        return {
            'state': state,
            'activity': activity,
            'lastAction': last_action,
            'projectsShipped': self.count_shipped_projects(),
            'newLogs': new_logs
        }
    
    def parse_log_file(self, log_file: Path) -> tuple:
        """Parse log file to determine current state"""
        try:
            # Read new log entries
            if self.last_log_file != str(log_file):
                self.last_log_position = 0
                self.last_log_file = str(log_file)
            
            with open(log_file) as f:
                f.seek(self.last_log_position)
                new_content = f.read()
                self.last_log_position = f.tell()
            
            # Parse recent lines
            recent_lines = new_content.strip().split('\n')[-50:] if new_content else []
            
            # Detect state based on log patterns
            state = 'sleeping'
            activity = 'Idle'
            last_action = 'No recent activity'
            new_logs = []
            
            # Check for activity patterns
            for line in reversed(recent_lines):
                if not line.strip():
                    continue
                
                # Extract timestamp and message
                match = re.search(r'\[(.*?)\].*?\s+(.*)', line)
                if match:
                    msg = match.group(2)
                    
                    # Detect state
                    if 'web_search' in line.lower() or 'searching' in line.lower():
                        state = 'searching'
                        activity = 'Searching the web'
                        last_action = msg[:100]
                    elif 'exec' in line.lower() and 'git push' in line.lower():
                        state = 'pushing'
                        activity = 'Pushing to GitHub'
                        last_action = 'Publishing project'
                    elif 'exec' in line.lower() and ('gh repo create' in line.lower() or 'git commit' in line.lower()):
                        state = 'pushing'
                        activity = 'Committing code'
                        last_action = msg[:100]
                    elif 'write' in line.lower() and ('.py' in line.lower() or '.js' in line.lower() or '.html' in line.lower()):
                        state = 'coding'
                        activity = 'Writing code'
                        last_action = msg[:100]
                    elif 'thinking' in line.lower() or 'analyzing' in line.lower():
                        state = 'thinking'
                        activity = 'Thinking'
                        last_action = msg[:100]
                    elif last_action == 'No recent activity':
                        last_action = msg[:100]
                    
                    # Add to new logs
                    if len(new_logs) < 5:
                        log_type = 'info'
                        if 'error' in line.lower():
                            log_type = 'error'
                        elif 'success' in line.lower() or 'complete' in line.lower():
                            log_type = 'success'
                        elif 'warning' in line.lower():
                            log_type = 'warning'
                        
                        new_logs.append({
                            'message': msg[:200],
                            'type': log_type
                        })
            
            # Check if recently active (within last 30 seconds)
            mod_time = os.path.getmtime(log_file)
            age = time.time() - mod_time
            
            if age > 30 and state != 'sleeping':
                state = 'sleeping'
                activity = 'Idle (waiting for tasks)'
            
            return state, activity, last_action, new_logs
            
        except Exception as e:
            print(f"Error parsing log: {e}")
            return 'sleeping', 'Error reading logs', str(e), []
    
    def count_shipped_projects(self) -> int:
        """Count shipped projects from published.md"""
        try:
            published_file = Path.home() / 'clawd' / 'research' / 'published.md'
            if published_file.exists():
                content = published_file.read_text()
                # Count ## headers (each project has one)
                count = len(re.findall(r'^## \w', content, re.MULTILINE))
                return count
        except Exception:
            pass
        return 4  # Default based on current count
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def main():
    """Start the dashboard server"""
    port = 8789
    
    print("🦞 Molty Status Dashboard")
    print("=" * 50)
    print(f"Starting server on http://localhost:{port}")
    print(f"Open in browser: http://localhost:{port}")
    print("=" * 50)
    print("Press Ctrl+C to stop\n")
    
    # Change to dashboard directory
    os.chdir(Path(__file__).parent)
    
    server = HTTPServer(('localhost', port), MoltyStatusHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down dashboard...")
        server.shutdown()


if __name__ == '__main__':
    main()
