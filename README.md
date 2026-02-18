<div align="center">

# JERRY v7.0 ULTIMATE — AI System Control Assistant

**A Jarvis-inspired real-time voice AI that controls your ENTIRE PC**

Built with React + TypeScript + Gemini 2.5 Flash Live + Python

**40+ System Controllers | Ultimate Voice Control | Everything Means Everything**

</div>

---

## Features

### Core System Control
- **Real-time Voice Conversation** — Gemini 2.5 Flash Native Audio API with streaming
- **Wake Word Detection** — Say "Jerry" to activate hands-free
- **Volume & Brightness Control** — Up, down, set exact percentage, mute/unmute
- **Power Management** — Lock, sleep, shutdown, restart (with cancel grace period)
- **App Management** — Open, close, focus, and list running applications
- **File Operations** — Create, read, delete, copy, move, search files & folders
- **Process Control** — List, kill processes, find resource hogs
- **WiFi Management** — List, connect, disconnect wireless networks
- **Keyboard & Mouse** — Full automation, macros, hotkeys, typing
- **Shell Commands** — Execute any terminal command

### v7.0 Ultimate Capabilities
- **Alarms, Timers & Reminders** — Set wake-up alarms, countdown timers, task reminders
- **Text-to-Speech** — Make your PC speak aloud
- **Media Control** — Play/pause/skip, YouTube search, Spotify integration
- **Calendar (Outlook)** — View and create calendar events
- **Email (SMTP)** — Send emails via voice
- **Quick Notes** — Take and search notes with tags
- **Window Management** — Snap, move, resize windows
- **Bluetooth Control** — List devices, toggle on/off
- **Display Settings** — Night light, resolution, multi-monitor projection
- **Audio Devices** — Switch audio output, mute microphone
- **Screen Recording** — Game Bar recording, webcam photos
- **Archive Operations** — Create/extract zip files
- **File Downloads** — Download from any URL
- **Git Version Control** — Status, pull, push, commit, clone, branch
- **Code Execution** — Run Python and PowerShell code
- **Calculator & Converter** — Math, unit conversion, currency conversion
- **Translator** — Translate text via Google Translate
- **Windows Services** — Start, stop, restart services
- **Accessibility** — Magnifier, narrator, high contrast
- **Focus Mode** — Do Not Disturb / Focus Assist control
- **Virtual Desktops** — Create, switch, close virtual desktops
- **USB Management** — List devices, safely eject drives
- **VPN Control** — Connect/disconnect VPN connections
- **Mobile Hotspot** — Toggle hotspot on/off
- **Clipboard History** — Access Windows clipboard history
- **Printing** — List printers, set default, print files
- **Power Profiles** — Switch between Balanced/High Performance/Power Saver
- **Environment Variables** — Get, set, list env vars
- **Scheduled Tasks** — Create and manage Windows scheduled tasks
- **Quick Actions** — Action Center, emoji picker, File Explorer, search, dictation

### Infrastructure
- **Workflow Automation** — Morning Mode, Work Mode, Night Mode, Gaming Mode, etc.
- **Real-time System Monitor** — CPU, RAM, disk, battery, network with proactive alerts
- **Command Queuing** — Queues commands when bridge is offline
- **Security Layer** — Auth tokens, command validation, dangerous action blocking
- **Smart API Key Rotation** — Auto-rotates Gemini keys with health tracking
- **Auto-Reconnect** — Exponential backoff reconnection on errors

---

## Prerequisites

- **Node.js** >= 18
- **Python** >= 3.10
- **Windows 10/11** (system control features are Windows-specific)

---

## Setup

### 1. Frontend

```bash
npm install
```

### 2. Python Bridge Dependencies

```bash
pip install websockets psutil pyautogui screen-brightness-control pycaw comtypes pyttsx3 pywin32 wmi pyperclip
```

Or create a `requirements.txt`:
```
websockets
psutil
pyautogui
screen-brightness-control
pycaw
comtypes
pyttsx3
pywin32
wmi
pyperclip
```

### 3. Environment Variables

Create `.env.local` in the project root:

```
GEMINI_API_KEY=key1,key2,key3,key4,key5
```

You can use 1 or more comma-separated Gemini API keys. Multiple keys enable automatic round-robin rotation on rate limits.

**Optional (for Email):**
```
JERRY_SMTP_USER=your-email@gmail.com
JERRY_SMTP_PASS=your-app-password
```

---

## Running

### Start the Python Bridge (Terminal 1)

```bash
python jerry_bridge.py
```

This starts the WebSocket bridge on `ws://localhost:8765` for system control.

### Start the Frontend (Terminal 2)

```bash
npm run dev
```

Opens at `http://localhost:3000`.

---

## Architecture

```
┌───────────────────────┐
│     React Frontend    │
│  (Gemini Live Audio)  │
├───────────────────────┤
│  App.tsx              │ ← Main orchestrator
│  services/gemini.ts   │ ← 17 Tools, system instruction
│  services/security.ts │ ← Auth, validation, logging
│  components/Orb.tsx   │ ← Arc-reactor style orb
│  components/Dashboard │ ← System stats display
│  components/Terminal  │ ← Activity log
└───────────┬───────────┘
            │ WebSocket
┌───────────▼───────────┐
│  jerry_bridge.py v7.0 │
│   (40+ Controllers)   │
├───────────────────────┤
│ AppController         │ SystemController
│ InputController       │ FileController
│ ProcessController     │ SystemMonitor
│ NetworkController     │ NotificationController
│ AlarmController       │ MediaController
│ TTSController         │ EmailController
│ CalendarController    │ WindowManager
│ NotesController       │ BluetoothController
│ DisplayController     │ AudioDeviceController
│ ScreenRecorder        │ ArchiveController
│ DownloadController    │ GitController
│ CodeExecutor          │ Calculator
│ Translator            │ ServicesController
│ AccessibilityCtrl     │ FocusAssist
│ VirtualDesktopCtrl    │ USBController
│ HotspotController     │ VPNController
│ ClipboardHistory      │ PrinterController
│ PowerProfiles         │ EnvironmentController
│ ScheduledTasks        │ QuickActions
└───────────────────────┘
```

---

## Built-in Workflows

| Workflow | Actions |
|---|---|
| **Morning Mode** | Brightness 70%, open Chrome + WhatsApp + Spotify, volume 40% |
| **Work Mode** | Close distractions, open VS Code + Chrome, brightness 60% |
| **Night Mode** | Brightness 20%, volume 20%, close work apps |
| **Gaming Mode** | Close work apps, open Steam, brightness 80%, volume 70% |
| **Presentation Mode** | Close messaging, brightness 90%, minimize all |
| **Lock Down** | Screenshot then lock PC |
| **System Cleanup** | Find resource hogs, clear temp files |

---

## Voice Commands (Examples)

### Basic System Control
- "Jerry, open Chrome and VS Code"
- "Set volume to 50 percent"
- "What's my CPU usage?"
- "Activate work mode"
- "Take a screenshot"
- "Lock the laptop"

### Time Management
- "Set an alarm for 7:30 AM"
- "Timer for 25 minutes"
- "Remind me in 30 minutes to take a break"
- "What alarms are set?"
- "Cancel all alarms"

### Media & Entertainment
- "Play lofi beats on YouTube"
- "Play Bohemian Rhapsody on Spotify"
- "Skip this song"
- "Pause the music"

### Notes & Memory
- "Remember that the WiFi password is guest123"
- "What notes do I have?"
- "Find notes about passwords"
- "Take a note: meeting with John at 3pm"

### Calendar & Email
- "What's on my calendar this week?"
- "Schedule a meeting tomorrow at 2pm"
- "Send an email to john@example.com about the project update"

### v7.0 Extended Commands
- "Turn on night light"
- "Start screen recording"
- "Zip my Documents folder"
- "Download this file: [URL]"
- "Git status"
- "Commit with message 'fix bug'"
- "Calculate 2 to the power of 10"
- "Convert 100 km to miles"
- "Convert 50 dollars to euros"
- "Translate hello to Spanish"
- "List running services"
- "New virtual desktop"
- "Switch to left desktop"
- "Eject USB drive E"
- "Connect to work VPN"
- "Turn on hotspot"
- "Set power to high performance"
- "Open emoji picker"
- "Start dictation"
- "Run Python: print('hello world')"
- "List printers"
- "Print this file"

---

## Security

- Bridge authentication via `AUTH_TOKEN`
- Dangerous commands (format, rm -rf, registry edits) are blocked
- Destructive actions require confirmation
- All activity is logged with timestamps
- Shutdown/restart have 30-second cancel grace period

---

## License

MIT
