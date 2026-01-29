// Molty Status Dashboard - Frontend

const STATES = {
    sleeping: { emoji: '💤', label: 'Sleeping', art: `
    ___
   /o o\\\\
  (  >  )
   \\\\_-_/
    | |
   _| |_` },
    thinking: { emoji: '🤔', label: 'Thinking', art: `
    ___
   /O O\\\\
  (  ?  )
   \\\\_~_/
    | |
   _| |_` },
    coding: { emoji: '⌨️', label: 'Coding', art: `
    ___
   /• •\\\\
  (  <  )
   \\\\_=_/
   ⌨| |⌨
   _| |_` },
    searching: { emoji: '🔍', label: 'Searching Web', art: `
    ___
   /◉ ◉\\\\
  (  o  )
   \\\\_-_/
   🔍| |
   _| |_` },
    pushing: { emoji: '🚀', label: 'Pushing to GitHub', art: `
    ___
   /★ ★\\\\
  (  ^  )
   \\\\_!_/
   🚀| |
   _| |_` }
};

let currentState = 'sleeping';
let sessionStartTime = Date.now();
let logBuffer = [];
const MAX_LOGS = 10;

// Update sprite and state
function updateState(state) {
    if (!STATES[state]) state = 'sleeping';
    
    currentState = state;
    const stateData = STATES[state];
    
    // Update sprite
    const sprite = document.getElementById('sprite');
    sprite.className = `sprite ${state}`;
    
    // Update ASCII art
    document.getElementById('ascii-sprite').textContent = stateData.art;
    
    // Update label
    document.getElementById('state-label').textContent = `${stateData.emoji} ${stateData.label}`;
}

// Add log entry
function addLog(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const entry = { time: timestamp, message, type };
    
    logBuffer.unshift(entry);
    if (logBuffer.length > MAX_LOGS) {
        logBuffer = logBuffer.slice(0, MAX_LOGS);
    }
    
    renderLogs();
}

// Render logs
function renderLogs() {
    const logContainer = document.getElementById('log-entries');
    
    if (logBuffer.length === 0) {
        logContainer.innerHTML = '<div class="log-entry">Waiting for activity...</div>';
        return;
    }
    
    logContainer.innerHTML = logBuffer.map(log => 
        `<div class="log-entry ${log.type}">
            <span style="opacity: 0.6">[${log.time}]</span> ${log.message}
        </div>`
    ).join('');
}

// Update session time
function updateSessionTime() {
    const elapsed = Date.now() - sessionStartTime;
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    document.getElementById('session-time').textContent = 
        `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Fetch status from backend
async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.state) {
            updateState(data.state);
        }
        
        if (data.activity) {
            document.getElementById('current-activity').textContent = data.activity;
        }
        
        if (data.lastAction) {
            document.getElementById('last-action').textContent = data.lastAction;
        }
        
        if (data.projectsShipped !== undefined) {
            document.getElementById('projects-shipped').textContent = data.projectsShipped;
        }
        
        if (data.newLogs && data.newLogs.length > 0) {
            data.newLogs.forEach(log => addLog(log.message, log.type));
        }
        
        // Update connection status
        document.getElementById('status-dot').className = 'status-dot';
        document.getElementById('connection-status').textContent = 'Connected';
        
    } catch (error) {
        console.error('Failed to fetch status:', error);
        document.getElementById('status-dot').className = 'status-dot disconnected';
        document.getElementById('connection-status').textContent = 'Disconnected';
    }
}

// Initialize
function init() {
    // Update time every second
    setInterval(updateSessionTime, 1000);
    
    // Fetch status every 2 seconds
    fetchStatus();
    setInterval(fetchStatus, 2000);
    
    // Initial state
    updateState('sleeping');
    addLog('Dashboard initialized', 'success');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
