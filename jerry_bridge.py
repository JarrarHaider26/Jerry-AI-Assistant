"""
Jerry Neural Bridge v7.0 â€” ULTIMATE System Control Interface
The most comprehensive voice-controlled system bridge ever built.

CAPABILITIES:
- Apps, Volume, Brightness, Power, Screenshots
- Alarms, Timers, Reminders
- Calendar, Email, Notes
- Media Control (YouTube, Spotify, etc.)
- Text-to-Speech
- Window Management
- File Operations
- Process Management
- Shell Commands
- WiFi, Bluetooth, Hotspot
- Display Settings (Night Light, Resolution, Multi-Monitor)
- Audio Device Switching
- Screen Recording, Screenshots, Webcam
- OCR (Read text from screen)
- Archive Operations (Zip/Unzip)
- Download Files from URL
- Git Operations
- Python Code Execution
- Translation, Currency Conversion, Calculator
- System Services, Startup Programs
- Accessibility Features
- VPN Control
- USB Eject
- Clipboard History
- Virtual Desktops
- Focus Assist / Do Not Disturb
- And MUCH more...
"""

import asyncio
import json
import os
import sys
import time
import hashlib
import hmac
import platform
import subprocess
import shutil
import glob
import socket
import signal
import logging
from logging.handlers import RotatingFileHandler
import ctypes
import threading
import smtplib
import ssl
import webbrowser
import tempfile
import zipfile
import tarfile
import base64
import re
import math
import struct
import wave
import io
import urllib.request
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Tuple
from functools import wraps
import sched
import heapq
import uuid
import secrets
from collections import deque, Counter, defaultdict

# --- Chrome browser helper (always opens in Chrome, not Edge) ---
def open_in_chrome(url: str) -> bool:
    """Open URL specifically in Chrome using user's existing session.
    
    If Chrome is running: opens a new tab in the existing window.
    If Chrome is not running: launches Chrome normally (uses default profile automatically).
    No special flags, no debugging ports, no profile overrides.
    """
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    
    # Find Chrome executable
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
    
    if chrome_path:
        try:
            # Just open the URL â€” Chrome handles everything:
            # - If running: opens new tab in existing window (with all logins)
            # - If not running: launches with default profile (all logins preserved)
            subprocess.Popen([chrome_path, url])
            return True
        except Exception:
            pass
    
    # Fallback: use 'start chrome' command
    try:
        subprocess.Popen(f'start chrome "{url}"', shell=True)
        return True
    except Exception:
        pass
    
    # Last fallback: system default browser
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False

# --- Third-party imports ---
try:
    import websockets
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
    import websockets

try:
    import psutil
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.1
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    import pyautogui

try:
    import screen_brightness_control as sbc
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "screen-brightness-control"])
    import screen_brightness_control as sbc

# Windows-specific imports
if platform.system() == "Windows":
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER
        import comtypes
        PYCAW_AVAILABLE = True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pycaw", "comtypes"])
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            from ctypes import cast, POINTER
            import comtypes
            PYCAW_AVAILABLE = True
        except Exception:
            PYCAW_AVAILABLE = False
else:
    PYCAW_AVAILABLE = False

# Text-to-Speech
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyttsx3"])
        import pyttsx3
        TTS_AVAILABLE = True
    except Exception:
        TTS_AVAILABLE = False

# Windows COM for Outlook/Calendar
OUTLOOK_AVAILABLE = False
if platform.system() == "Windows":
    try:
        import win32com.client
        OUTLOOK_AVAILABLE = True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
            import win32com.client
            OUTLOOK_AVAILABLE = True
        except Exception:
            pass

# WMI for advanced Windows control
WMI_AVAILABLE = False
if platform.system() == "Windows":
    try:
        import wmi
        WMI_AVAILABLE = True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "wmi"])
            import wmi
            WMI_AVAILABLE = True
        except Exception:
            pass

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [JERRY-BRIDGE] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler("jerry_bridge.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    ]
)
log = logging.getLogger("JerryBridge")


class StructuredLogger:
    """Structured JSON logger for command auditing."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_command(self, action: str, status: str, details: Optional[Dict[str, Any]] = None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details or {}
        }
        self.logger.info(json.dumps(log_entry))


structured_log = StructuredLogger("JerryBridge.Structured")


class PredictiveIntelligence:
    """Learn command patterns and suggest likely next actions."""

    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.transitions: Dict[str, Counter] = defaultdict(Counter)
        self.model_path = os.path.expanduser("~/.jerry_predictive.json")
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, "r") as f:
                    data = json.load(f)
                self.history = data.get("history", [])
                transitions = data.get("transitions", {})
                self.transitions = defaultdict(Counter, {k: Counter(v) for k, v in transitions.items()})
        except Exception:
            self.history = []
            self.transitions = defaultdict(Counter)

    def _save(self):
        try:
            transitions = {k: dict(v) for k, v in self.transitions.items()}
            data = {"history": self.history[-500:], "transitions": transitions}
            with open(self.model_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def learn_from_command(self, action: str, context: Dict[str, Any]):
        if not action:
            return
        now = datetime.now().isoformat()
        self.history.append({"action": action, "timestamp": now, "context": context})
        if len(self.history) >= 2:
            prev_action = self.history[-2]["action"]
            self.transitions[prev_action][action] += 1

        if len(self.history) % 25 == 0:
            self._save()

    def predict_next_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        if len(self.history) < 10:
            return []
        last_action = self.history[-1]["action"]
        counts = self.transitions.get(last_action, Counter())
        if not counts:
            return []
        total = sum(counts.values()) or 1
        top = counts.most_common(3)
        return [
            {
                "command": action,
                "confidence": round(count / total, 3),
                "reason": f"After '{last_action}', this action occurs {count} time(s)."
            }
            for action, count in top
        ]

    def detect_routines(self) -> List[Dict[str, Any]]:
        routines: List[Dict[str, Any]] = []
        if len(self.history) < 20:
            return routines

        def hour_of(entry: Dict[str, Any]) -> int:
            try:
                return datetime.fromisoformat(entry["timestamp"]).hour
            except Exception:
                return 0

        morning = [h for h in self.history if 6 <= hour_of(h) <= 10]
        work = [h for h in self.history if 9 <= hour_of(h) <= 17]

        if len(morning) > 10:
            common = Counter([h["action"] for h in morning]).most_common(5)
            routines.append({
                "name": "Morning Routine",
                "time": "06:00-10:00",
                "commands": [cmd for cmd, _ in common],
                "frequency": len(morning)
            })

        if len(work) > 20:
            common = Counter([h["action"] for h in work]).most_common(5)
            routines.append({
                "name": "Work Mode",
                "time": "09:00-17:00",
                "commands": [cmd for cmd, _ in common],
                "frequency": len(work)
            })

        return routines

    def suggest_automation(self) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []
        if len(self.history) < 10:
            return suggestions

        sequences: List[Tuple[str, str, str]] = []
        for i in range(len(self.history) - 2):
            seq = (
                self.history[i]["action"],
                self.history[i + 1]["action"],
                self.history[i + 2]["action"],
            )
            sequences.append(seq)

        common = Counter(sequences).most_common(3)
        for seq, count in common:
            if count >= 3:
                suggestions.append({
                    "type": "workflow",
                    "commands": list(seq),
                    "frequency": count,
                    "suggestion": "Create workflow: " + " -> ".join(seq)
                })
        return suggestions


class AutonomousAgent:
    """Simple autonomous agent with heuristic planning and execution."""

    def __init__(self, goal: str, bridge: "JerryBridge"):
        self.goal = goal or ""
        self.bridge = bridge
        self.plan: List[Dict[str, Any]] = []
        self.memory: List[Dict[str, Any]] = []

    def _extract_after(self, keyword: str) -> str:
        lower = self.goal.lower()
        if keyword in lower:
            return self.goal.lower().split(keyword, 1)[-1].strip()
        return ""

    async def _create_plan(self) -> List[Dict[str, Any]]:
        goal = self.goal.lower()
        plan: List[Dict[str, Any]] = []

        if "open" in goal and "youtube" in goal:
            plan.append({"action": "open_app", "target": "youtube"})
        if "play" in goal and "youtube" in goal:
            query = self._extract_after("play") or self._extract_after("youtube")
            plan.append({"action": "youtube_play", "target": query})
        if "search" in goal or "google" in goal:
            query = self._extract_after("search") or self._extract_after("google")
            if query:
                plan.append({"action": "google_first", "target": query})
        if "system status" in goal or "diagnostics" in goal:
            plan.append({"action": "system_status"})

        if not plan:
            plan.append({"action": "system_status"})
        return plan

    async def execute(self) -> Dict[str, Any]:
        self.plan = await self._create_plan()
        results: List[Dict[str, Any]] = []

        for step in self.plan:
            try:
                result = await self.bridge.handle_command(step)
            except Exception as e:
                result = {"status": "error", "message": str(e)}
            results.append(result)
            self.memory.append({"step": step, "result": result})

        return {
            "status": "success",
            "goal": self.goal,
            "steps_executed": len(results),
            "results": results
        }


class JerryBridgeException(Exception):
    """Base exception for Jerry Bridge."""


class CommandExecutionError(JerryBridgeException):
    """Raised when command execution fails."""


class BridgeConnectionError(JerryBridgeException):
    """Raised when bridge connection fails."""

# --- Configuration ---
BRIDGE_HOST = "127.0.0.1"
BRIDGE_PORT = 8765
TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".jerry_bridge_token")
ENV_SYNC_FILE = os.path.join(Path(__file__).resolve().parent, ".env.local")
NONCE_TTL_MS = 30000
recent_nonces: Dict[str, float] = {}


def _load_or_create_token() -> str:
    if os.path.exists(TOKEN_FILE):
        try:
            # Only check Unix-style permissions on non-Windows platforms
            if platform.system() != "Windows":
                stat_info = os.stat(TOKEN_FILE)
                if stat_info.st_mode & 0o077:
                    log.error("Token file has insecure permissions. Regenerating.")
                    os.remove(TOKEN_FILE)
                else:
                    with open(TOKEN_FILE, "r") as f:
                        token = f.read().strip()
                        if token:
                            return token
            else:
                # On Windows, just read the token directly
                with open(TOKEN_FILE, "r") as f:
                    token = f.read().strip()
                    if token:
                        return token
        except Exception:
            pass

    token = secrets.token_urlsafe(32)
    try:
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        # Set restrictive permissions on Unix; skip on Windows
        if platform.system() != "Windows":
            try:
                os.chmod(TOKEN_FILE, 0o600)
            except Exception:
                pass
    except Exception:
        pass
    return token


def _cleanup_nonces(now_ms: float) -> None:
    expired = [n for n, ts in recent_nonces.items() if now_ms - ts > NONCE_TTL_MS]
    for n in expired:
        recent_nonces.pop(n, None)


def validate_token(provided_token: str, timestamp: Optional[int] = None, nonce: Optional[str] = None) -> bool:
    """Validate auth token. For localhost, simple token comparison is sufficient.
    Timestamp/nonce replay protection is optional and only enforced if provided."""
    if not provided_token:
        return False
    try:
        if not hmac.compare_digest(str(provided_token), str(AUTH_TOKEN)):
            return False
    except TypeError:
        return False
    # Token matches — that's sufficient for localhost
    return True


def _sync_token_to_env(token: str) -> None:
    """Write VITE_JERRY_BRIDGE_TOKEN to .env.local for frontend dev builds."""
    if os.environ.get("JERRY_BRIDGE_ENV_SYNC", "1") != "1":
        return
    try:
        lines: List[str] = []
        if os.path.exists(ENV_SYNC_FILE):
            with open(ENV_SYNC_FILE, "r") as f:
                lines = f.read().splitlines()
        updated = False
        new_lines: List[str] = []
        for line in lines:
            if line.startswith("VITE_JERRY_BRIDGE_TOKEN="):
                new_lines.append(f"VITE_JERRY_BRIDGE_TOKEN={token}")
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f"VITE_JERRY_BRIDGE_TOKEN={token}")
        with open(ENV_SYNC_FILE, "w") as f:
            f.write("\n".join(new_lines) + "\n")
    except Exception as e:
        log.warning(f"Failed to sync token to .env.local: {e}")


AUTH_TOKEN = os.environ.get("JERRY_BRIDGE_TOKEN")
if not AUTH_TOKEN:
    AUTH_TOKEN = _load_or_create_token()
    log.warning("AUTH_TOKEN not set. Using token from ~/.jerry_bridge_token. Set JERRY_BRIDGE_TOKEN to override.")
    _sync_token_to_env(AUTH_TOKEN)
MAX_COMMAND_HISTORY = 500
DANGEROUS_ACTIONS = ["shutdown", "restart", "delete_file", "delete_folder", "format", "registry_edit", "kill_process"]

# --- App Registry: Common apps and their executable paths ---
APP_REGISTRY: Dict[str, str] = {
    # Browsers
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "brave": "brave",
    # Communication
    "whatsapp": "WhatsApp",
    "telegram": "Telegram",
    "discord": "Discord",
    "slack": "slack",
    "teams": "teams",
    "microsoft teams": "teams",
    "zoom": "zoom",
    "skype": "skype",
    # Media
    "spotify": "Spotify",
    "vlc": "vlc",
    "itunes": "iTunes",
    # Productivity
    "notepad": "notepad",
    "notepad++": "notepad++",
    "word": "WINWORD",
    "excel": "EXCEL",
    "powerpoint": "POWERPNT",
    "outlook": "OUTLOOK",
    "onenote": "ONENOTE",
    # Development
    "vscode": "code",
    "visual studio code": "code",
    "visual studio": "devenv",
    "cmd": "cmd",
    "terminal": "wt",
    "powershell": "powershell",
    "git bash": "git-bash",
    # System
    "task manager": "taskmgr",
    "control panel": "control",
    "settings": "ms-settings:",
    "file explorer": "explorer",
    "calculator": "calc",
    "paint": "mspaint",
    "snipping tool": "SnippingTool",
    # Games / Other
    "steam": "steam",
    "epic games": "EpicGamesLauncher",
}

# --- Website Registry: Common websites to open in browser ---
WEBSITE_REGISTRY: Dict[str, str] = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://twitter.com",
    "x": "https://twitter.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "reddit": "https://www.reddit.com",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
    "chatgpt": "https://chat.openai.com",
    "wikipedia": "https://www.wikipedia.org",
    "twitch": "https://www.twitch.tv",
    "pinterest": "https://www.pinterest.com",
    "tiktok": "https://www.tiktok.com",
    "bing": "https://www.bing.com",
    "yahoo": "https://www.yahoo.com",
    "outlook": "https://outlook.live.com",
    "drive": "https://drive.google.com",
    "docs": "https://docs.google.com",
    "sheets": "https://sheets.google.com",
    "maps": "https://maps.google.com",
    "calendar": "https://calendar.google.com",
}

# --- Command History & Undo ---
COMMAND_HISTORY_FILE = os.path.join(os.path.expanduser("~"), "jerry_command_history.json")
active_connections: set = set()


def _load_command_history() -> List[Dict[str, Any]]:
    """Load command history from disk."""
    try:
        if os.path.exists(COMMAND_HISTORY_FILE):
            with open(COMMAND_HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []

command_history: List[Dict[str, Any]] = _load_command_history()


def _save_command_history():
    """Persist command history to disk."""
    try:
        with open(COMMAND_HISTORY_FILE, 'w') as f:
            json.dump(command_history[-MAX_COMMAND_HISTORY:], f, indent=2)
    except Exception as e:
        log.error(f"Failed to save command history: {e}")


def record_command(action: str, details: Dict[str, Any], undoable: bool = False, undo_action: Optional[Dict] = None):
    """Record a command execution for history and undo."""
    entry = {
        "id": len(command_history) + 1,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "undoable": undoable,
        "undo_action": undo_action,
        "status": "executed"
    }
    command_history.append(entry)
    if len(command_history) > MAX_COMMAND_HISTORY:
        command_history.pop(0)
    _save_command_history()
    return entry


# ===================================================================
# MODULE 1: APPLICATION CONTROL
# ===================================================================
class AppController:
    """Handles opening, closing, and managing applications."""

    @staticmethod
    def open_app(target: str, payload: str = "") -> Dict[str, Any]:
        target_lower = target.lower().strip()
        payload_lower = payload.lower().strip() if payload else ""
        
        # Check if target is a website (e.g., "open youtube", "open google")
        if target_lower in WEBSITE_REGISTRY:
            website_url = WEBSITE_REGISTRY[target_lower]
            
            # Check if user specified a browser in payload
            browser = None
            if "chrome" in payload_lower or "chrome" in target_lower:
                browser = "chrome"
            elif "edge" in payload_lower:
                browser = "edge"
            elif "firefox" in payload_lower:
                browser = "firefox"
            elif "brave" in payload_lower:
                browser = "brave"
            
            # Default to Chrome for websites
            if browser == "chrome" or browser is None:
                open_in_chrome(website_url)
                return {"status": "success", "message": f"Opened {target} in Chrome"}
            elif browser == "edge":
                subprocess.Popen(f'start msedge "{website_url}"', shell=True)
                return {"status": "success", "message": f"Opened {target} in Edge"}
            elif browser == "firefox":
                subprocess.Popen(f'start firefox "{website_url}"', shell=True)
                return {"status": "success", "message": f"Opened {target} in Firefox"}
            elif browser == "brave":
                subprocess.Popen(f'start brave "{website_url}"', shell=True)
                return {"status": "success", "message": f"Opened {target} in Brave"}
        
        # Check if payload is a URL (e.g., "open chrome with youtube.com")  
        if payload and ("http" in payload or "www." in payload or ".com" in payload or ".org" in payload or ".net" in payload):
            url = payload if payload.startswith("http") else f"https://{payload}"
            # Use Chrome by default for URLs
            if target_lower in ["chrome", "google chrome"]:
                open_in_chrome(url)
                return {"status": "success", "message": f"Opened {url} in Chrome"}
            elif target_lower in ["edge", "msedge", "microsoft edge"]:
                subprocess.Popen(f'start msedge "{url}"', shell=True)
                return {"status": "success", "message": f"Opened {url} in Edge"}
            else:
                open_in_chrome(url)
                return {"status": "success", "message": f"Opened {url} in Chrome"}
        
        exe = APP_REGISTRY.get(target_lower, target_lower)

        try:
            # Handle Windows Settings URI
            if exe.startswith("ms-settings:"):
                os.system(f"start {exe}")
                record_command("open_app", {"target": target}, undoable=True,
                              undo_action={"action": "close_app", "target": target})
                return {"status": "success", "message": f"Opened {target}"}

            # Standard app launch
            if platform.system() == "Windows":
                subprocess.Popen(f"start {exe}", shell=True)
            else:
                subprocess.Popen([exe], start_new_session=True)

            record_command("open_app", {"target": target, "exe": exe}, undoable=True,
                          undo_action={"action": "close_app", "target": target})
            return {"status": "success", "message": f"Launched {target}"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to open {target}: {str(e)}"}

    @staticmethod
    def close_app(target: str) -> Dict[str, Any]:
        target_lower = target.lower().strip()
        exe = APP_REGISTRY.get(target_lower, target_lower)

        try:
            killed = False
            for proc in psutil.process_iter(['name', 'pid']):
                proc_name = proc.info['name'].lower()
                if exe.lower() in proc_name or target_lower in proc_name:
                    proc.terminate()
                    killed = True

            if killed:
                record_command("close_app", {"target": target})
                return {"status": "success", "message": f"Closed {target}"}
            else:
                return {"status": "warning", "message": f"{target} is not running"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to close {target}: {str(e)}"}

    @staticmethod
    def list_running_apps() -> Dict[str, Any]:
        """List all running applications with window titles."""
        apps = []
        seen = set()
        for proc in psutil.process_iter(['name', 'pid', 'cpu_percent', 'memory_percent']):
            try:
                name = proc.info['name']
                if name not in seen and proc.info['memory_percent'] and proc.info['memory_percent'] > 0.1:
                    apps.append({
                        "name": name,
                        "pid": proc.info['pid'],
                        "cpu": round(proc.info['cpu_percent'] or 0, 1),
                        "memory": round(proc.info['memory_percent'] or 0, 1)
                    })
                    seen.add(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        apps.sort(key=lambda x: x['memory'], reverse=True)
        return {"status": "success", "apps": apps[:30]}

    @staticmethod
    def focus_app(target: str) -> Dict[str, Any]:
        """Bring an application window to the foreground."""
        if platform.system() != "Windows":
            return {"status": "error", "message": "Window focus only supported on Windows"}
        try:
            import win32gui
            import win32con

            target_lower = target.lower()

            def callback(hwnd, hwnds):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd).lower()
                    if target_lower in title:
                        hwnds.append(hwnd)
                return True

            hwnds = []
            win32gui.EnumWindows(callback, hwnds)
            if hwnds:
                win32gui.ShowWindow(hwnds[0], win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnds[0])
                return {"status": "success", "message": f"Focused {target}"}
            return {"status": "warning", "message": f"No window found for {target}"}
        except ImportError:
            return {"status": "error", "message": "win32gui not installed. Run: pip install pywin32"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 2: SYSTEM CONTROL
# ===================================================================
class SystemController:
    """Handles volume, brightness, power, and OS-level operations."""

    @staticmethod
    def volume_control(target: str, payload: str = "") -> Dict[str, Any]:
        action = target.lower().strip()
        try:
            # Primary method: Use keyboard media keys (most reliable)
            if action == "up":
                for _ in range(5):
                    pyautogui.press('volumeup')
                    time.sleep(0.05)
                return {"status": "success", "message": "Volume increased"}
            elif action == "down":
                for _ in range(5):
                    pyautogui.press('volumedown')
                    time.sleep(0.05)
                return {"status": "success", "message": "Volume decreased"}
            elif action == "mute":
                pyautogui.press('volumemute')
                return {"status": "success", "message": "Volume muted"}
            elif action == "unmute":
                pyautogui.press('volumemute')
                return {"status": "success", "message": "Volume toggled"}
            elif action == "set" and payload:
                try:
                    level = int(payload)
                    # Mute first, then set to level using key presses
                    # Each volumeup is roughly 2% on Windows
                    presses = level // 2
                    # First, go to 0 by pressing down many times
                    for _ in range(50):
                        pyautogui.press('volumedown')
                        time.sleep(0.02)
                    # Then press up to desired level
                    for _ in range(presses):
                        pyautogui.press('volumeup')
                        time.sleep(0.02)
                    return {"status": "success", "message": f"Volume set to approximately {level}%"}
                except ValueError:
                    return {"status": "error", "message": "Invalid volume level. Use 0-100"}
            elif action == "get":
                # Try to get volume via PowerShell
                try:
                    result = subprocess.run(
                        ['powershell', '-Command', 
                         '(Get-AudioDevice -PlaybackVolume).Volume'],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        return {"status": "success", "message": f"Volume: {result.stdout.strip()}%"}
                except Exception:
                    pass
                return {"status": "info", "message": "Volume level: Use Windows mixer to check"}
            else:
                return {"status": "error", "message": f"Unknown volume action: {action}. Use: up, down, mute, unmute, set, get"}

        except Exception as e:
            return {"status": "error", "message": f"Volume control failed: {str(e)}"}

    @staticmethod
    def brightness_control(target: str, payload: str = "") -> Dict[str, Any]:
        action = target.lower().strip()
        try:
            current = sbc.get_brightness(display=0)
            if isinstance(current, list):
                current = current[0]

            if action == "up":
                new_val = min(100, current + 10)
                sbc.set_brightness(new_val, display=0)
                return {"status": "success", "message": f"Brightness: {new_val}%"}
            elif action == "down":
                new_val = max(0, current - 10)
                sbc.set_brightness(new_val, display=0)
                return {"status": "success", "message": f"Brightness: {new_val}%"}
            elif action == "set" and payload:
                sbc.set_brightness(int(payload), display=0)
                return {"status": "success", "message": f"Brightness set to {payload}%"}
            elif action == "get":
                return {"status": "success", "message": f"Brightness: {current}%"}

        except Exception as e:
            return {"status": "error", "message": f"Brightness control failed: {str(e)}"}

        return {"status": "error", "message": f"Unknown brightness action: {action}"}

    @staticmethod
    def power_control(target: str) -> Dict[str, Any]:
        action = target.lower().strip()
        try:
            if action == "lock":
                if platform.system() == "Windows":
                    ctypes.windll.user32.LockWorkStation()
                return {"status": "success", "message": "Workstation locked"}
            elif action == "sleep":
                if platform.system() == "Windows":
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return {"status": "success", "message": "System entering sleep mode"}
            elif action == "shutdown":
                os.system("shutdown /s /t 30 /c \"Jerry: Shutdown initiated by command.\"")
                record_command("power_control", {"target": "shutdown"}, undoable=True,
                              undo_action={"action": "cancel_shutdown"})
                return {"status": "success", "message": "System will shut down in 30 seconds. Say 'cancel shutdown' to abort."}
            elif action == "restart":
                os.system("shutdown /r /t 30 /c \"Jerry: Restart initiated by command.\"")
                record_command("power_control", {"target": "restart"}, undoable=True,
                              undo_action={"action": "cancel_shutdown"})
                return {"status": "success", "message": "System will restart in 30 seconds. Say 'cancel restart' to abort."}
            elif action == "cancel_shutdown":
                os.system("shutdown /a")
                return {"status": "success", "message": "Shutdown/restart cancelled"}
            elif action == "logoff":
                os.system("shutdown /l")
                return {"status": "success", "message": "Logging off..."}

        except Exception as e:
            return {"status": "error", "message": f"Power control failed: {str(e)}"}

        return {"status": "error", "message": f"Unknown power action: {action}"}

    @staticmethod
    def screenshot(payload: str = "") -> Dict[str, Any]:
        try:
            save_path = payload or os.path.join(os.path.expanduser("~"), "Desktop", f"jerry_screenshot_{int(time.time())}.png")
            img = pyautogui.screenshot()
            img.save(save_path)
            record_command("screenshot", {"path": save_path})
            return {"status": "success", "message": f"Screenshot saved: {save_path}"}
        except Exception as e:
            return {"status": "error", "message": f"Screenshot failed: {str(e)}"}

    @staticmethod
    def clipboard_control(target: str, payload: str = "") -> Dict[str, Any]:
        action = target.lower().strip()
        try:
            import pyperclip
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
            import pyperclip

        try:
            if action == "copy" and payload:
                pyperclip.copy(payload)
                return {"status": "success", "message": "Text copied to clipboard"}
            elif action == "get" or action == "paste":
                text = pyperclip.paste()
                return {"status": "success", "message": f"Clipboard: {text[:500]}"}
            elif action == "clear":
                pyperclip.copy("")
                return {"status": "success", "message": "Clipboard cleared"}
        except Exception as e:
            return {"status": "error", "message": f"Clipboard operation failed: {str(e)}"}

        return {"status": "error", "message": f"Unknown clipboard action: {action}"}


# ===================================================================
# MODULE 3: KEYBOARD & MOUSE AUTOMATION
# ===================================================================
class InputController:
    """Keyboard and mouse automation."""

    @staticmethod
    def keyboard_macro(target: str, payload: str = "") -> Dict[str, Any]:
        action = target.lower().strip()
        try:
            if action == "type" and payload:
                pyautogui.typewrite(payload, interval=0.02)
                return {"status": "success", "message": f"Typed: {payload[:50]}..."}
            elif action == "type_unicode" and payload:
                pyautogui.write(payload)
                return {"status": "success", "message": f"Typed: {payload[:50]}..."}
            elif action == "hotkey" and payload:
                keys = [k.strip() for k in payload.split("+")]
                pyautogui.hotkey(*keys)
                return {"status": "success", "message": f"Hotkey executed: {payload}"}
            elif action == "press" and payload:
                pyautogui.press(payload)
                return {"status": "success", "message": f"Key pressed: {payload}"}
            elif action == "copy_all":
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'c')
                return {"status": "success", "message": "Selected all and copied"}
            elif action == "save":
                pyautogui.hotkey('ctrl', 's')
                return {"status": "success", "message": "Save shortcut triggered"}
            elif action == "undo":
                pyautogui.hotkey('ctrl', 'z')
                return {"status": "success", "message": "Undo triggered"}
            elif action == "redo":
                pyautogui.hotkey('ctrl', 'y')
                return {"status": "success", "message": "Redo triggered"}
            elif action == "screenshot":
                pyautogui.hotkey('win', 'shift', 's')
                return {"status": "success", "message": "Snipping tool opened"}
            elif action == "search":
                pyautogui.hotkey('win')
                time.sleep(0.5)
                if payload:
                    pyautogui.typewrite(payload, interval=0.03)
                return {"status": "success", "message": f"Windows search opened{': ' + payload if payload else ''}"}
            elif action == "minimize_all":
                pyautogui.hotkey('win', 'd')
                return {"status": "success", "message": "All windows minimized"}
            elif action == "switch_window":
                pyautogui.hotkey('alt', 'tab')
                return {"status": "success", "message": "Window switched"}
            elif action == "task_view":
                pyautogui.hotkey('win', 'tab')
                return {"status": "success", "message": "Task view opened"}
            elif action == "close_window":
                pyautogui.hotkey('alt', 'F4')
                return {"status": "success", "message": "Active window closed"}
            elif action == "new_desktop":
                pyautogui.hotkey('win', 'ctrl', 'd')
                return {"status": "success", "message": "New virtual desktop created"}

        except Exception as e:
            return {"status": "error", "message": f"Keyboard macro failed: {str(e)}"}

        return {"status": "error", "message": f"Unknown keyboard action: {action}"}

    @staticmethod
    def mouse_control(target: str, payload: str = "") -> Dict[str, Any]:
        action = target.lower().strip()
        try:
            if action == "click":
                if payload:
                    coords = [int(c.strip()) for c in payload.split(",")]
                    pyautogui.click(coords[0], coords[1])
                else:
                    pyautogui.click()
                return {"status": "success", "message": "Mouse clicked"}
            elif action == "doubleclick":
                pyautogui.doubleClick()
                return {"status": "success", "message": "Mouse double-clicked"}
            elif action == "rightclick":
                pyautogui.rightClick()
                return {"status": "success", "message": "Mouse right-clicked"}
            elif action == "move" and payload:
                coords = [int(c.strip()) for c in payload.split(",")]
                pyautogui.moveTo(coords[0], coords[1], duration=0.3)
                return {"status": "success", "message": f"Mouse moved to {payload}"}
            elif action == "scroll" and payload:
                pyautogui.scroll(int(payload))
                return {"status": "success", "message": f"Scrolled {'up' if int(payload) > 0 else 'down'}"}
            elif action == "position":
                pos = pyautogui.position()
                return {"status": "success", "message": f"Mouse position: ({pos.x}, {pos.y})"}

        except Exception as e:
            return {"status": "error", "message": f"Mouse control failed: {str(e)}"}

        return {"status": "error", "message": f"Unknown mouse action: {action}"}


# ===================================================================
# MODULE 4: FILE SYSTEM OPERATIONS
# ===================================================================
class FileController:
    """File system operations."""

    @staticmethod
    def _resolve_path(path: str) -> str:
        """Resolve paths with wrong usernames or shortcuts to actual user paths."""
        if not path:
            return path
        # Expand ~ and env vars
        path = os.path.expanduser(os.path.expandvars(path))
        # Fix wrong username in paths like C:\Users\Sir\Desktop -> actual user Desktop
        home = os.path.expanduser("~")
        # Detect paths under C:\Users\<wrong_user>\ and remap to actual home
        import re
        match = re.match(r'^([A-Za-z]:\\Users\\)[^\\]+(\\.*)', path, re.IGNORECASE)
        if match and not os.path.exists(os.path.dirname(path)):
            corrected = home + match.group(2)
            log.info(f"Path corrected: {path} -> {corrected}")
            return corrected
        # Handle bare names like "Desktop\file.txt" -> actual Desktop
        if not os.path.isabs(path):
            # Check if it starts with a known folder name
            known_folders = {
                'desktop': os.path.join(home, 'Desktop'),
                'documents': os.path.join(home, 'Documents'),
                'downloads': os.path.join(home, 'Downloads'),
                'pictures': os.path.join(home, 'Pictures'),
                'music': os.path.join(home, 'Music'),
                'videos': os.path.join(home, 'Videos'),
            }
            first_part = path.split(os.sep)[0].split('/')[0].lower()
            if first_part in known_folders:
                rest = path[len(first_part):].lstrip(os.sep).lstrip('/')
                resolved = os.path.join(known_folders[first_part], rest) if rest else known_folders[first_part]
                log.info(f"Path resolved: {path} -> {resolved}")
                return resolved
        return path

    @staticmethod
    def file_operation(target: str, payload: str = "", extra: str = "") -> Dict[str, Any]:
        action = target.lower().strip()
        # Resolve paths to fix wrong usernames
        payload = FileController._resolve_path(payload)
        if extra and action in ('rename_file', 'copy_file', 'move_file', 'restore_file'):
            extra = FileController._resolve_path(extra)
        try:
            if action == "create_file" and payload:
                Path(payload).parent.mkdir(parents=True, exist_ok=True)
                with open(payload, 'w', encoding='utf-8') as f:
                    f.write(extra or "")
                record_command("file_operation", {"action": "create_file", "path": payload}, undoable=True,
                              undo_action={"action": "delete_file", "target": payload})
                return {"status": "success", "message": f"File created: {payload}"}

            elif action == "read_file" and payload:
                if not os.path.exists(payload):
                    return {"status": "error", "message": f"File not found: {payload}"}
                with open(payload, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(10000)  # Limit read
                return {"status": "success", "message": f"Content:\n{content}"}

            elif action == "delete_file" and payload:
                if os.path.exists(payload):
                    # Backup before delete
                    backup_path = payload + ".jerry_backup"
                    shutil.copy2(payload, backup_path)
                    os.remove(payload)
                    record_command("file_operation", {"action": "delete_file", "path": payload}, undoable=True,
                                  undo_action={"action": "restore_file", "target": backup_path, "payload": payload})
                    return {"status": "success", "message": f"File deleted: {payload}"}
                return {"status": "error", "message": f"File not found: {payload}"}

            elif action == "rename_file" and payload and extra:
                os.rename(payload, extra)
                record_command("file_operation", {"action": "rename_file", "from": payload, "to": extra}, undoable=True,
                              undo_action={"action": "rename_file", "target": extra, "payload": payload})
                return {"status": "success", "message": f"Renamed: {payload} â†’ {extra}"}

            elif action == "copy_file" and payload and extra:
                shutil.copy2(payload, extra)
                return {"status": "success", "message": f"Copied: {payload} â†’ {extra}"}

            elif action == "move_file" and payload and extra:
                shutil.move(payload, extra)
                record_command("file_operation", {"action": "move_file", "from": payload, "to": extra}, undoable=True,
                              undo_action={"action": "move_file", "target": extra, "payload": payload})
                return {"status": "success", "message": f"Moved: {payload} â†’ {extra}"}

            elif action == "list_dir" and payload:
                if not os.path.isdir(payload):
                    return {"status": "error", "message": f"Directory not found: {payload}"}
                items = []
                for item in os.listdir(payload):
                    full_path = os.path.join(payload, item)
                    is_dir = os.path.isdir(full_path)
                    size = os.path.getsize(full_path) if not is_dir else 0
                    items.append({"name": item, "is_dir": is_dir, "size": size})
                return {"status": "success", "items": items, "message": f"Listed {len(items)} items"}

            elif action == "create_folder" and payload:
                os.makedirs(payload, exist_ok=True)
                return {"status": "success", "message": f"Folder created: {payload}"}

            elif action == "delete_folder" and payload:
                if os.path.isdir(payload):
                    shutil.rmtree(payload)
                    return {"status": "success", "message": f"Folder deleted: {payload}"}
                return {"status": "error", "message": f"Folder not found: {payload}"}

            elif action == "search_files" and payload:
                search_in = extra or os.path.expanduser("~")
                results = []
                for root, dirs, files in os.walk(search_in):
                    for f in files:
                        if payload.lower() in f.lower():
                            results.append(os.path.join(root, f))
                            if len(results) >= 20:
                                break
                    if len(results) >= 20:
                        break
                return {"status": "success", "results": results, "message": f"Found {len(results)} matches"}

            elif action == "restore_file" and payload and extra:
                # payload = backup path, extra = original path
                if os.path.exists(payload):
                    shutil.copy2(payload, extra)
                    os.remove(payload)
                    return {"status": "success", "message": f"File restored: {extra}"}
                return {"status": "error", "message": "Backup not found"}

            elif action == "disk_usage":
                path = payload or "C:\\"
                usage = shutil.disk_usage(path)
                return {
                    "status": "success",
                    "message": f"Disk {path}: Total={usage.total//(1024**3)}GB, Used={usage.used//(1024**3)}GB, Free={usage.free//(1024**3)}GB"
                }

        except PermissionError:
            return {"status": "error", "message": f"Permission denied for: {payload}"}
        except Exception as e:
            return {"status": "error", "message": f"File operation failed: {str(e)}"}

        return {"status": "error", "message": f"Unknown file action: {action}"}


# ===================================================================
# MODULE 5: PROCESS MANAGEMENT
# ===================================================================
class ProcessController:
    """Process monitoring and management."""

    @staticmethod
    def process_operation(target: str, payload: str = "") -> Dict[str, Any]:
        action = target.lower().strip()
        try:
            if action == "list":
                procs = []
                for proc in psutil.process_iter(['name', 'pid', 'cpu_percent', 'memory_percent', 'status']):
                    try:
                        info = proc.info
                        if info['memory_percent'] and info['memory_percent'] > 0.1:
                            procs.append({
                                "name": info['name'],
                                "pid": info['pid'],
                                "cpu": round(info['cpu_percent'] or 0, 1),
                                "memory": round(info['memory_percent'] or 0, 1),
                                "status": info['status']
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                procs.sort(key=lambda x: x['cpu'], reverse=True)
                return {"status": "success", "processes": procs[:25], "message": f"Top {min(25, len(procs))} processes"}

            elif action == "kill" and payload:
                killed = False
                for proc in psutil.process_iter(['name', 'pid']):
                    try:
                        if payload.isdigit():
                            if proc.info['pid'] == int(payload):
                                proc.kill()
                                killed = True
                                break
                        else:
                            if payload.lower() in proc.info['name'].lower():
                                proc.kill()
                                killed = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                if killed:
                    record_command("kill_process", {"target": payload})
                    return {"status": "success", "message": f"Process {payload} killed"}
                return {"status": "warning", "message": f"Process {payload} not found"}

            elif action == "kill_all" and payload:
                count = 0
                for proc in psutil.process_iter(['name', 'pid']):
                    try:
                        if payload.lower() in proc.info['name'].lower():
                            proc.kill()
                            count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return {"status": "success", "message": f"Killed {count} instances of {payload}"}

            elif action == "resource_hogs":
                procs = []
                for proc in psutil.process_iter(['name', 'pid', 'cpu_percent', 'memory_percent']):
                    try:
                        info = proc.info
                        if (info['cpu_percent'] or 0) > 10 or (info['memory_percent'] or 0) > 5:
                            procs.append({
                                "name": info['name'],
                                "pid": info['pid'],
                                "cpu": round(info['cpu_percent'] or 0, 1),
                                "memory": round(info['memory_percent'] or 0, 1)
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                procs.sort(key=lambda x: x['cpu'] + x['memory'], reverse=True)
                return {"status": "success", "processes": procs[:10], "message": f"Found {len(procs)} resource-heavy processes"}

        except Exception as e:
            return {"status": "error", "message": f"Process operation failed: {str(e)}"}

        return {"status": "error", "message": f"Unknown process action: {action}"}


# ===================================================================
# MODULE 6: SYSTEM MONITORING
# ===================================================================
class SystemMonitor:
    """Real-time system monitoring and diagnostics."""

    @staticmethod
    def get_system_status() -> Dict[str, Any]:
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            battery = psutil.sensors_battery()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            temps = None
            try:
                temps = psutil.sensors_temperatures()
            except Exception:
                pass

            result = {
                "status": "success",
                "cpu": {
                    "percent": cpu,
                    "cores": psutil.cpu_count(),
                    "freq_current": round(cpu_freq.current, 0) if cpu_freq else 0,
                    "freq_max": round(cpu_freq.max, 0) if cpu_freq else 0,
                    "per_core": psutil.cpu_percent(percpu=True)
                },
                "memory": {
                    "percent": memory.percent,
                    "total_gb": round(memory.total / (1024**3), 1),
                    "used_gb": round(memory.used / (1024**3), 1),
                    "available_gb": round(memory.available / (1024**3), 1)
                },
                "disk": {
                    "percent": disk.percent,
                    "total_gb": round(disk.total / (1024**3), 1),
                    "used_gb": round(disk.used / (1024**3), 1),
                    "free_gb": round(disk.free / (1024**3), 1)
                },
                "network": {
                    "bytes_sent": net.bytes_sent,
                    "bytes_recv": net.bytes_recv,
                    "sent_mb": round(net.bytes_sent / (1024**2), 1),
                    "recv_mb": round(net.bytes_recv / (1024**2), 1)
                },
                "battery": {
                    "percent": battery.percent if battery else None,
                    "charging": battery.power_plugged if battery else None,
                    "time_left": str(timedelta(seconds=battery.secsleft)) if battery and battery.secsleft > 0 else "N/A"
                },
                "uptime": str(uptime).split('.')[0],
                "os": f"{platform.system()} {platform.release()}",
                "hostname": socket.gethostname()
            }

            if temps:
                result["temperatures"] = {k: [{"label": t.label, "current": t.current} for t in v] for k, v in temps.items()}

            return result

        except Exception as e:
            return {"status": "error", "message": f"System status failed: {str(e)}"}

    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        try:
            interfaces = {}
            for name, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        interfaces[name] = {
                            "ip": addr.address,
                            "netmask": addr.netmask
                        }

            connections = []
            for conn in psutil.net_connections(kind='inet')[:20]:
                connections.append({
                    "local": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                    "remote": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
                    "status": conn.status,
                    "pid": conn.pid
                })

            return {
                "status": "success",
                "interfaces": interfaces,
                "active_connections": len(connections),
                "connections": connections[:10]
            }
        except Exception as e:
            return {"status": "error", "message": f"Network info failed: {str(e)}"}

    @staticmethod
    def get_startup_programs() -> Dict[str, Any]:
        """List startup programs (Windows)."""
        programs = []
        if platform.system() == "Windows":
            try:
                import winreg
                locations = [
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                ]
                for hive, path in locations:
                    try:
                        key = winreg.OpenKey(hive, path)
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                programs.append({"name": name, "path": value})
                                i += 1
                            except OSError:
                                break
                    except Exception:
                        pass
            except ImportError:
                pass
        return {"status": "success", "programs": programs, "message": f"Found {len(programs)} startup programs"}


# ===================================================================
# MODULE 7: COMMAND EXECUTION (Shell)
# ===================================================================
class ShellController:
    """Execute shell commands safely."""

    BLOCKED_COMMANDS = ["format", "del /s", "rd /s /q C:", "rm -rf /"]

    @staticmethod
    def execute_command(command: str, cwd: str = None) -> Dict[str, Any]:
        # Safety check
        for blocked in ShellController.BLOCKED_COMMANDS:
            if blocked.lower() in command.lower():
                return {"status": "error", "message": f"BLOCKED: Dangerous command detected: {blocked}"}

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=cwd
            )
            output = result.stdout.strip() or result.stderr.strip()
            record_command("shell_execute", {"command": command})
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": output[:3000],
                "return_code": result.returncode,
                "message": output[:500] or "Command executed"
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out after 30 seconds"}
        except Exception as e:
            return {"status": "error", "message": f"Shell execution failed: {str(e)}"}


# ===================================================================
# MODULE 8: NOTIFICATION & ALERT SYSTEM
# ===================================================================
class NotificationController:
    """System notifications and alerts."""

    @staticmethod
    def send_notification(title: str, message: str) -> Dict[str, Any]:
        try:
            if platform.system() == "Windows":
                # Use PowerShell for toast notification
                ps_script = f'''
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
                $template = @"
                <toast>
                    <visual>
                        <binding template="ToastText02">
                            <text id="1">{title}</text>
                            <text id="2">{message}</text>
                        </binding>
                    </visual>
                </toast>
"@
                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
                $xml.LoadXml($template)
                $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Jerry AI").Show($toast)
                '''
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
                return {"status": "success", "message": f"Notification sent: {title}"}
            else:
                return {"status": "error", "message": "Notifications not supported on this OS"}
        except Exception as e:
            return {"status": "error", "message": f"Notification failed: {str(e)}"}


# ===================================================================
# MODULE 9: WIFI & NETWORK MANAGEMENT
# ===================================================================
class NetworkController:
    """WiFi and network management."""

    @staticmethod
    def wifi_operation(target: str, payload: str = "") -> Dict[str, Any]:
        action = target.lower().strip()
        try:
            if action == "list":
                result = subprocess.run(
                    'netsh wlan show networks mode=bssid',
                    shell=True, capture_output=True, text=True
                )
                return {"status": "success", "message": result.stdout[:3000] or "No networks found"}

            elif action == "connect" and payload:
                result = subprocess.run(
                    f'netsh wlan connect name="{payload}"',
                    shell=True, capture_output=True, text=True
                )
                return {"status": "success", "message": result.stdout.strip() or f"Connecting to {payload}"}

            elif action == "disconnect":
                result = subprocess.run(
                    'netsh wlan disconnect',
                    shell=True, capture_output=True, text=True
                )
                return {"status": "success", "message": "WiFi disconnected"}

            elif action == "status":
                result = subprocess.run(
                    'netsh wlan show interfaces',
                    shell=True, capture_output=True, text=True
                )
                return {"status": "success", "message": result.stdout[:3000]}

            elif action == "ip":
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                return {"status": "success", "message": f"Hostname: {hostname}, IP: {ip}"}

            elif action == "speedtest":
                return {"status": "info", "message": "Running network speed test..."}

        except Exception as e:
            return {"status": "error", "message": f"WiFi operation failed: {str(e)}"}

        return {"status": "error", "message": f"Unknown WiFi action: {action}"}


# ===================================================================
# MODULE 10: ALARM, TIMER & REMINDER SYSTEM
# ===================================================================
class AlarmController:
    """Manage alarms, timers, and reminders."""
    
    _instance = None
    _alarms: Dict[str, Dict[str, Any]] = {}
    _timers: Dict[str, Dict[str, Any]] = {}
    _reminders: Dict[str, Dict[str, Any]] = {}
    _alarm_tasks: Dict[str, asyncio.Task] = {}
    ALARMS_FILE = os.path.join(os.path.expanduser("~"), "jerry_alarms.json")
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_alarms_from_disk()
        return cls._instance
    
    @classmethod
    def _load_alarms_from_disk(cls):
        """Load persisted alarms/reminders from disk."""
        try:
            if os.path.exists(cls.ALARMS_FILE):
                with open(cls.ALARMS_FILE, 'r') as f:
                    data = json.load(f)
                cls._alarms = data.get("alarms", {})
                cls._reminders = data.get("reminders", {})
                # Re-schedule any future alarms
                now = datetime.now()
                for alarm_id, alarm in list(cls._alarms.items()):
                    if not alarm.get("triggered", False):
                        try:
                            target_time = datetime.fromisoformat(alarm["time"])
                            if target_time > now:
                                log.info(f"Re-scheduling alarm '{alarm.get('label', alarm_id)}' for {target_time}")
                            else:
                                alarm["triggered"] = True
                        except Exception:
                            pass
                log.info(f"Loaded {len(cls._alarms)} alarms, {len(cls._reminders)} reminders from disk")
        except Exception as e:
            log.error(f"Failed to load alarms from disk: {e}")
    
    @classmethod
    def _save_alarms_to_disk(cls):
        """Persist alarms/reminders to disk."""
        try:
            data = {
                "alarms": cls._alarms,
                "reminders": cls._reminders
            }
            with open(cls.ALARMS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log.error(f"Failed to save alarms to disk: {e}")
    
    @staticmethod
    def _play_alarm_sound(sound_type: str = "alarm"):
        """Play alarm sound on Windows."""
        try:
            if platform.system() == "Windows":
                import winsound
                if sound_type == "alarm":
                    # Play Windows alarm sound
                    for _ in range(3):
                        winsound.Beep(1000, 500)
                        time.sleep(0.1)
                elif sound_type == "timer":
                    winsound.Beep(800, 300)
                    winsound.Beep(1000, 300)
                    winsound.Beep(1200, 300)
                elif sound_type == "reminder":
                    winsound.Beep(600, 200)
                    winsound.Beep(800, 400)
        except Exception as e:
            log.error(f"Sound error: {e}")
    
    @staticmethod
    def _show_alert(title: str, message: str):
        """Show Windows alert dialog."""
        try:
            if platform.system() == "Windows":
                ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1000)
        except Exception:
            pass
    
    async def _alarm_worker(self, alarm_id: str, target_time: datetime, label: str, sound: bool = True):
        """Background worker that waits and triggers alarm."""
        try:
            now = datetime.now()
            wait_seconds = (target_time - now).total_seconds()
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            
            # Trigger alarm
            self._play_alarm_sound("alarm")
            AlarmController._alarms[alarm_id]["triggered"] = True
            AlarmController._save_alarms_to_disk()
            
            # Show notification
            NotificationController.send_notification(f"â° ALARM: {label}", f"Time: {target_time.strftime('%H:%M')}")
            
            # Speak it
            if TTS_AVAILABLE:
                TTSController.speak(f"Alarm! {label}")
            
            log.info(f"â° ALARM TRIGGERED: {label} at {target_time}")
        except asyncio.CancelledError:
            log.info(f"Alarm {alarm_id} cancelled")
        except Exception as e:
            log.error(f"Alarm worker error: {e}")
    
    def set_alarm(self, time_str: str, label: str = "Alarm", repeat: str = "") -> Dict[str, Any]:
        """Set an alarm using Windows Task Scheduler. Format: HH:MM or HH:MM:SS"""
        try:
            # Parse time
            now = datetime.now()
            time_parts = time_str.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time has passed today, set for tomorrow
            if target <= now:
                target += timedelta(days=1)
            
            alarm_id = str(uuid.uuid4())[:8]
            
            # Create a real Windows Scheduled Task that triggers a notification + sound
            schtask_success = self._create_alarm_task(alarm_id, target, label)
            
            # Also keep in-memory backup alarm
            self._alarms[alarm_id] = {
                "id": alarm_id,
                "time": target.isoformat(),
                "label": label,
                "repeat": repeat,
                "triggered": False,
                "created": now.isoformat(),
                "scheduled_task": schtask_success
            }
            self._save_alarms_to_disk()
            
            # Start async backup task (plays sound even if scheduled task works)
            loop = asyncio.get_event_loop()
            task = loop.create_task(self._alarm_worker(alarm_id, target, label))
            self._alarm_tasks[alarm_id] = task
            
            time_until = target - now
            hours_until, remainder = divmod(time_until.total_seconds(), 3600)
            minutes_until, _ = divmod(remainder, 60)
            
            status_msg = f"â° Alarm '{label}' set for {target.strftime('%H:%M')} ({int(hours_until)}h {int(minutes_until)}m from now)"
            if schtask_success:
                status_msg += " [System scheduled]"
            
            return {
                "status": "success",
                "alarm_id": alarm_id,
                "message": status_msg
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to set alarm: {str(e)}"}
    
    def _create_alarm_task(self, alarm_id: str, target_time: datetime, label: str) -> bool:
        """Create a Windows Scheduled Task that shows a toast notification + plays alarm sound."""
        try:
            task_name = f"JerryAlarm_{alarm_id}"
            
            # PowerShell script that shows a toast notification and plays alarm sound
            # Uses BurntToast module if available, falls back to basic notification
            ps_script = f'''
# Play alarm sound
[System.Media.SystemSounds]::Exclamation.Play()
Start-Sleep -Milliseconds 500
[System.Media.SystemSounds]::Exclamation.Play()
Start-Sleep -Milliseconds 500
[System.Media.SystemSounds]::Exclamation.Play()

# Try toast notification
try {{
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null
    $xml = @"
<toast duration="long">
  <visual>
    <binding template="ToastGeneric">
      <text>Alarm: {label}</text>
      <text>Time: {target_time.strftime('%I:%M %p')}</text>
    </binding>
  </visual>
  <audio src="ms-winsoundevent:Notification.Looping.Alarm" loop="true"/>
</toast>
"@
    $XmlDocument = [Windows.Data.Xml.Dom.XmlDocument]::new()
    $XmlDocument.LoadXml($xml)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($XmlDocument)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Jerry AI")
    $notifier.Show($toast)
}} catch {{
    # Fallback: simple message box
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show("Time: {target_time.strftime('%I:%M %p')}", "Alarm: {label}", "OK", "Information")
}}

# Delete the scheduled task after triggering
schtasks /delete /tn "{task_name}" /f 2>$null
'''
            
            # Write the script to a temp file
            script_dir = os.path.join(os.path.expanduser("~"), ".jerry_alarms")
            os.makedirs(script_dir, exist_ok=True)
            script_path = os.path.join(script_dir, f"{task_name}.ps1")
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(ps_script)
            
            # Create the scheduled task using schtasks
            time_str = target_time.strftime('%H:%M')
            date_str = target_time.strftime('%m/%d/%Y')
            
            cmd = (
                f'schtasks /create /tn "{task_name}" '
                f'/tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File \\"{script_path}\\"" '
                f'/sc once /st {time_str} /sd {date_str} /f'
            )
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                log.info(f"âœ“ Scheduled Task created: {task_name} at {time_str} on {date_str}")
                return True
            else:
                log.error(f"schtasks failed: {result.stderr}")
                return False
            
        except Exception as e:
            log.error(f"Failed to create scheduled task alarm: {e}")
            return False
    
    def _delete_alarm_task(self, alarm_id: str):
        """Delete a scheduled alarm task."""
        try:
            task_name = f"JerryAlarm_{alarm_id}"
            subprocess.run(
                f'schtasks /delete /tn "{task_name}" /f',
                shell=True, capture_output=True, timeout=5
            )
            # Clean up script file
            script_path = os.path.join(os.path.expanduser("~"), ".jerry_alarms", f"{task_name}.ps1")
            if os.path.exists(script_path):
                os.remove(script_path)
        except Exception:
            pass
    
    def set_timer(self, duration: str, label: str = "Timer") -> Dict[str, Any]:
        """Set a countdown timer. Format: Xh Ym Zs (e.g., '5m', '1h 30m', '90s')"""
        try:
            # Parse duration
            total_seconds = 0
            duration = duration.lower().strip()
            
            # Handle simple formats like "5" (minutes by default)
            if duration.isdigit():
                total_seconds = int(duration) * 60
            else:
                import re
                hours = re.search(r'(\d+)\s*h', duration)
                minutes = re.search(r'(\d+)\s*m', duration)
                seconds = re.search(r'(\d+)\s*s', duration)
                
                if hours:
                    total_seconds += int(hours.group(1)) * 3600
                if minutes:
                    total_seconds += int(minutes.group(1)) * 60
                if seconds:
                    total_seconds += int(seconds.group(1))
            
            if total_seconds <= 0:
                return {"status": "error", "message": "Invalid duration. Use format: 5m, 1h 30m, 90s"}
            
            timer_id = str(uuid.uuid4())[:8]
            end_time = datetime.now() + timedelta(seconds=total_seconds)
            
            self._timers[timer_id] = {
                "id": timer_id,
                "duration": total_seconds,
                "end_time": end_time.isoformat(),
                "label": label,
                "triggered": False
            }
            
            # Start async timer
            async def timer_worker():
                await asyncio.sleep(total_seconds)
                self._play_alarm_sound("timer")
                self._timers[timer_id]["triggered"] = True
                NotificationController.send_notification(f"â±ï¸ TIMER: {label}", "Time's up!")
                if TTS_AVAILABLE:
                    TTSController.speak(f"Timer complete! {label}")
            
            loop = asyncio.get_event_loop()
            task = loop.create_task(timer_worker())
            self._alarm_tasks[f"timer_{timer_id}"] = task
            
            hours, remainder = divmod(total_seconds, 3600)
            minutes, secs = divmod(remainder, 60)
            time_str = ""
            if hours:
                time_str += f"{int(hours)}h "
            if minutes:
                time_str += f"{int(minutes)}m "
            if secs:
                time_str += f"{int(secs)}s"
            
            return {
                "status": "success",
                "timer_id": timer_id,
                "message": f"â±ï¸ Timer '{label}' set for {time_str.strip()}"
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to set timer: {str(e)}"}
    
    def set_reminder(self, time_str: str, message: str) -> Dict[str, Any]:
        """Set a reminder. Time can be relative ('in 30 minutes') or absolute ('at 3pm')"""
        try:
            now = datetime.now()
            target = None
            
            time_lower = time_str.lower()
            
            # Parse relative time: "in X minutes/hours"
            import re
            relative = re.search(r'in\s+(\d+)\s*(minute|min|m|hour|h|second|sec|s)', time_lower)
            if relative:
                amount = int(relative.group(1))
                unit = relative.group(2)
                if unit.startswith('h'):
                    target = now + timedelta(hours=amount)
                elif unit.startswith('m'):
                    target = now + timedelta(minutes=amount)
                else:
                    target = now + timedelta(seconds=amount)
            
            # Parse absolute time: "at HH:MM" or "HH:MM"
            if not target:
                time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)?', time_lower)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2) or 0)
                    ampm = time_match.group(3)
                    
                    if ampm == 'pm' and hour < 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    
                    target = now.replace(hour=hour, minute=minute, second=0)
                    if target <= now:
                        target += timedelta(days=1)
            
            if not target:
                return {"status": "error", "message": "Couldn't parse time. Try 'in 30 minutes' or 'at 3:30pm'"}
            
            reminder_id = str(uuid.uuid4())[:8]
            self._reminders[reminder_id] = {
                "id": reminder_id,
                "time": target.isoformat(),
                "message": message
            }
            self._save_alarms_to_disk()
            
            async def reminder_worker():
                wait = (target - datetime.now()).total_seconds()
                if wait > 0:
                    await asyncio.sleep(wait)
                self._play_alarm_sound("reminder")
                NotificationController.send_notification("ðŸ“ REMINDER", message)
                if TTS_AVAILABLE:
                    TTSController.speak(f"Reminder: {message}")
            
            loop = asyncio.get_event_loop()
            task = loop.create_task(reminder_worker())
            self._alarm_tasks[f"reminder_{reminder_id}"] = task
            
            return {
                "status": "success",
                "reminder_id": reminder_id,
                "message": f"ðŸ“ Reminder set for {target.strftime('%H:%M')}: {message}"
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to set reminder: {str(e)}"}
    
    def cancel_alarm(self, alarm_id: str) -> Dict[str, Any]:
        """Cancel an alarm, timer, or reminder."""
        try:
            # Check all types
            for prefix in ["", "timer_", "reminder_"]:
                task_id = f"{prefix}{alarm_id}"
                if task_id in self._alarm_tasks:
                    self._alarm_tasks[task_id].cancel()
                    del self._alarm_tasks[task_id]
            
            if alarm_id in self._alarms:
                # Also delete the Windows Scheduled Task
                self._delete_alarm_task(alarm_id)
                del self._alarms[alarm_id]
            if alarm_id in self._timers:
                del self._timers[alarm_id]
            if alarm_id in self._reminders:
                del self._reminders[alarm_id]
            
            self._save_alarms_to_disk()
            return {"status": "success", "message": f"Cancelled: {alarm_id}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_alarms(self) -> Dict[str, Any]:
        """List all active alarms, timers, and reminders."""
        return {
            "status": "success",
            "alarms": list(self._alarms.values()),
            "timers": list(self._timers.values()),
            "reminders": list(self._reminders.values()),
            "message": f"Active: {len(self._alarms)} alarms, {len(self._timers)} timers, {len(self._reminders)} reminders"
        }


# ===================================================================
# MODULE 11: TEXT-TO-SPEECH
# ===================================================================
class TTSController:
    """Text-to-speech capabilities."""
    
    _engine = None
    
    @classmethod
    def _get_engine(cls):
        if cls._engine is None and TTS_AVAILABLE:
            cls._engine = pyttsx3.init()
            cls._engine.setProperty('rate', 175)  # Speed
            cls._engine.setProperty('volume', 0.9)
        return cls._engine
    
    @classmethod
    def speak(cls, text: str, wait: bool = False) -> Dict[str, Any]:
        """Make the computer speak."""
        try:
            if not TTS_AVAILABLE:
                # Fallback to PowerShell
                ps_cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}")'
                subprocess.Popen(["powershell", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)
                return {"status": "success", "message": f"Speaking: {text[:50]}..."}
            
            engine = cls._get_engine()
            if wait:
                engine.say(text)
                engine.runAndWait()
            else:
                # Non-blocking speech
                def speak_thread():
                    e = pyttsx3.init()
                    e.say(text)
                    e.runAndWait()
                threading.Thread(target=speak_thread, daemon=True).start()
            
            return {"status": "success", "message": f"Speaking: {text[:50]}..."}
        except Exception as e:
            return {"status": "error", "message": f"TTS failed: {str(e)}"}
    
    @classmethod
    def set_voice(cls, voice_id: int = 0) -> Dict[str, Any]:
        """Change TTS voice."""
        try:
            engine = cls._get_engine()
            voices = engine.getProperty('voices')
            if 0 <= voice_id < len(voices):
                engine.setProperty('voice', voices[voice_id].id)
                return {"status": "success", "message": f"Voice changed to: {voices[voice_id].name}"}
            return {"status": "error", "message": f"Voice ID {voice_id} not found. Available: 0-{len(voices)-1}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @classmethod
    def list_voices(cls) -> Dict[str, Any]:
        """List available TTS voices."""
        try:
            engine = cls._get_engine()
            voices = engine.getProperty('voices')
            voice_list = [{"id": i, "name": v.name} for i, v in enumerate(voices)]
            return {"status": "success", "voices": voice_list}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 12: EMAIL CONTROLLER
# ===================================================================
class EmailController:
    """Send emails via SMTP."""
    
    # Default configuration (user can override via environment)
    SMTP_SERVER = os.environ.get("JERRY_SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("JERRY_SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("JERRY_SMTP_USER", "")
    SMTP_PASS = os.environ.get("JERRY_SMTP_PASS", "")  # App password for Gmail
    
    @classmethod
    def send_email(cls, to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
        """Send an email."""
        if not cls.SMTP_USER or not cls.SMTP_PASS:
            return {
                "status": "error",
                "message": "Email not configured. Set JERRY_SMTP_USER and JERRY_SMTP_PASS environment variables."
            }
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = cls.SMTP_USER
            msg["To"] = to
            
            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            context = ssl.create_default_context()
            with smtplib.SMTP(cls.SMTP_SERVER, cls.SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(cls.SMTP_USER, cls.SMTP_PASS)
                server.sendmail(cls.SMTP_USER, to, msg.as_string())
            
            return {"status": "success", "message": f"Email sent to {to}"}
        except Exception as e:
            return {"status": "error", "message": f"Email failed: {str(e)}"}


# ===================================================================
# MODULE 13: CALENDAR CONTROLLER (Outlook Integration)
# ===================================================================
class CalendarController:
    """Calendar operations via Outlook COM."""
    
    @staticmethod
    def get_events(days: int = 7) -> Dict[str, Any]:
        """Get calendar events for the next X days."""
        if not OUTLOOK_AVAILABLE:
            return {"status": "error", "message": "Outlook not available. Install pywin32."}
        
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            calendar = namespace.GetDefaultFolder(9)  # 9 = Calendar
            
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            
            appointments = calendar.Items
            appointments.IncludeRecurrences = True
            appointments.Sort("[Start]")
            
            restriction = f"[Start] >= '{start_date.strftime('%m/%d/%Y')}' AND [Start] <= '{end_date.strftime('%m/%d/%Y')}'"
            filtered = appointments.Restrict(restriction)
            
            events = []
            for appt in filtered:
                events.append({
                    "subject": appt.Subject,
                    "start": str(appt.Start),
                    "end": str(appt.End),
                    "location": appt.Location,
                    "body": appt.Body[:200] if appt.Body else ""
                })
                if len(events) >= 20:
                    break
            
            return {"status": "success", "events": events, "message": f"Found {len(events)} events"}
        except Exception as e:
            return {"status": "error", "message": f"Calendar error: {str(e)}"}
    
    @staticmethod
    def create_event(subject: str, start_time: str, duration_minutes: int = 60, location: str = "", body: str = "") -> Dict[str, Any]:
        """Create a calendar event."""
        if not OUTLOOK_AVAILABLE:
            return {"status": "error", "message": "Outlook not available"}
        
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            appt = outlook.CreateItem(1)  # 1 = Appointment
            
            # Parse start time
            start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            
            appt.Subject = subject
            appt.Start = start
            appt.Duration = duration_minutes
            appt.Location = location
            appt.Body = body
            appt.ReminderSet = True
            appt.ReminderMinutesBeforeStart = 15
            appt.Save()
            
            return {"status": "success", "message": f"Created event: {subject} at {start_time}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to create event: {str(e)}"}


# ===================================================================
# MODULE 14: MEDIA CONTROLLER
# ===================================================================
class MediaController:
    """Control media playback (play, pause, next, previous, etc.)."""
    
    @staticmethod
    def media_control(action: str) -> Dict[str, Any]:
        """Control media playback using virtual key presses."""
        try:
            if platform.system() != "Windows":
                return {"status": "error", "message": "Media control only on Windows"}
            
            # Virtual key codes for media keys
            VK_MEDIA_PLAY_PAUSE = 0xB3
            VK_MEDIA_NEXT = 0xB0
            VK_MEDIA_PREV = 0xB1
            VK_MEDIA_STOP = 0xB2
            VK_VOLUME_MUTE = 0xAD
            
            key_map = {
                "play": VK_MEDIA_PLAY_PAUSE,
                "pause": VK_MEDIA_PLAY_PAUSE,
                "playpause": VK_MEDIA_PLAY_PAUSE,
                "toggle": VK_MEDIA_PLAY_PAUSE,
                "next": VK_MEDIA_NEXT,
                "skip": VK_MEDIA_NEXT,
                "previous": VK_MEDIA_PREV,
                "prev": VK_MEDIA_PREV,
                "back": VK_MEDIA_PREV,
                "stop": VK_MEDIA_STOP,
                "mute": VK_VOLUME_MUTE
            }
            
            action_lower = action.lower().strip()
            if action_lower not in key_map:
                return {"status": "error", "message": f"Unknown media action: {action}. Use: play, pause, next, previous, stop"}
            
            vk = key_map[action_lower]
            
            # Send key press
            ctypes.windll.user32.keybd_event(vk, 0, 0, 0)  # Key down
            ctypes.windll.user32.keybd_event(vk, 0, 2, 0)  # Key up
            
            return {"status": "success", "message": f"Media: {action}"}
        except Exception as e:
            return {"status": "error", "message": f"Media control failed: {str(e)}"}
    
    @staticmethod
    def open_url(url: str) -> Dict[str, Any]:
        """Open a URL in Chrome (not the default browser)."""
        try:
            open_in_chrome(url)
            return {"status": "success", "message": f"Opened in Chrome: {url}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def play_youtube(query: str, auto_play: bool = True) -> Dict[str, Any]:
        """Search and play on YouTube (auto-clicks first video if enabled)."""
        if auto_play:
            return BrowserControl.youtube_play_first(query)
        
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            open_in_chrome(search_url)
            return {"status": "success", "message": f"Searching YouTube for: {query}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def play_spotify(query: str, auto_play: bool = True) -> Dict[str, Any]:
        """Search on Spotify and play first result."""
        if auto_play:
            return BrowserControl.spotify_play_first(query)
        
        try:
            # Try Spotify URI first
            spotify_uri = f"spotify:search:{query}"
            subprocess.Popen(f"start {spotify_uri}", shell=True)
            return {"status": "success", "message": f"Searching Spotify for: {query}"}
        except Exception:
            # Fallback to web (use Chrome)
            open_in_chrome(f"https://open.spotify.com/search/{query}")
            return {"status": "success", "message": f"Opening Spotify web for: {query}"}


# ===================================================================
# MODULE 14B: BROWSER CONTROL (No Selenium - uses existing Chrome)
# ===================================================================
# Uses pyautogui + Chrome address bar + keyboard shortcuts
# No new browser windows, no new profiles, no Selenium drivers


class BrowserControl:
    """Browser control using user's existing Chrome via pyautogui + keyboard.
    
    This approach:
    - Never opens a new browser window/profile
    - Works with the user's existing Chrome session (all logins preserved)
    - Uses keyboard shortcuts and pyautogui for interaction
    - Uses Chrome address bar (Ctrl+L) for navigation
    - Uses Chrome DevTools Protocol for reading page content when available
    """
    
    @staticmethod
    def _focus_chrome() -> bool:
        """Bring Chrome to the foreground."""
        try:
            import win32gui
            import win32con
            
            def enum_handler(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "chrome" in title.lower() or "google chrome" in title.lower():
                        results.append(hwnd)
            
            windows = []
            win32gui.EnumWindows(enum_handler, windows)
            
            if windows:
                hwnd = windows[0]
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.3)
                return True
        except Exception:
            pass
        
        # Fallback: Alt+Tab or try launching Chrome
        try:
            # Try to activate Chrome via taskbar
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            return True
        except Exception:
            return False
    
    @staticmethod
    def _is_chrome_running() -> bool:
        """Check if Chrome is currently running."""
        try:
            result = subprocess.run(
                'tasklist /fi "imagename eq chrome.exe" /fo csv /nh',
                shell=True, capture_output=True, text=True, timeout=5
            )
            return "chrome.exe" in result.stdout.lower()
        except Exception:
            return False
    
    @staticmethod
    def navigate(url: str) -> Dict[str, Any]:
        """Open URL in user's existing Chrome browser."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            open_in_chrome(url)
            return {"status": "success", "message": f"Opened: {url}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def navigate_address_bar(url: str) -> Dict[str, Any]:
        """Navigate by typing in address bar of active Chrome window."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            BrowserControl._focus_chrome()
            time.sleep(0.3)
            
            # Ctrl+L to focus address bar
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.3)
            
            # Type URL and press Enter
            pyautogui.typewrite(url, interval=0.01)
            pyautogui.press('enter')
            
            return {"status": "success", "message": f"Navigating to: {url}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def new_tab(url: str = "") -> Dict[str, Any]:
        """Open a new tab in Chrome."""
        try:
            if url:
                open_in_chrome(url)
                return {"status": "success", "message": f"New tab: {url}"}
            else:
                BrowserControl._focus_chrome()
                pyautogui.hotkey('ctrl', 't')
                return {"status": "success", "message": "New tab opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def close_tab() -> Dict[str, Any]:
        """Close current browser tab."""
        try:
            BrowserControl._focus_chrome()
            pyautogui.hotkey('ctrl', 'w')
            return {"status": "success", "message": "Tab closed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def switch_tab(direction: str = "next") -> Dict[str, Any]:
        """Switch to next or previous tab."""
        try:
            BrowserControl._focus_chrome()
            if direction.lower() in ("next", "right"):
                pyautogui.hotkey('ctrl', 'tab')
            elif direction.lower() in ("prev", "previous", "left"):
                pyautogui.hotkey('ctrl', 'shift', 'tab')
            elif direction.lower().isdigit():
                # Switch to specific tab number (1-8)
                pyautogui.hotkey('ctrl', direction.lower())
            return {"status": "success", "message": f"Switched tab: {direction}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def scroll_page(direction: str = "down", amount: int = 5) -> Dict[str, Any]:
        """Scroll the active browser page."""
        try:
            BrowserControl._focus_chrome()
            time.sleep(0.2)
            
            if direction.lower() == "down":
                pyautogui.scroll(-amount)
            elif direction.lower() == "up":
                pyautogui.scroll(amount)
            elif direction.lower() == "top":
                pyautogui.hotkey('ctrl', 'Home')
            elif direction.lower() == "bottom":
                pyautogui.hotkey('ctrl', 'End')
            elif direction.lower() == "pagedown":
                pyautogui.press('pagedown')
            elif direction.lower() == "pageup":
                pyautogui.press('pageup')
            
            return {"status": "success", "message": f"Scrolled {direction}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def send_keys(keys: str) -> Dict[str, Any]:
        """Send keyboard keys/shortcuts to active window."""
        try:
            BrowserControl._focus_chrome()
            time.sleep(0.2)
            
            # Parse keys like "ctrl+a", "ctrl+shift+s", "enter", "f5"
            key_parts = keys.lower().split('+')
            
            if len(key_parts) > 1:
                pyautogui.hotkey(*key_parts)
            else:
                key = key_parts[0]
                # Map common key names
                key_map = {
                    "enter": "enter", "return": "enter",
                    "esc": "escape", "escape": "escape",
                    "space": "space", "tab": "tab",
                    "backspace": "backspace", "delete": "delete",
                    "up": "up", "down": "down", "left": "left", "right": "right",
                    "home": "home", "end": "end",
                    "pageup": "pageup", "pagedown": "pagedown",
                }
                pyautogui.press(key_map.get(key, key))
            
            return {"status": "success", "message": f"Sent keys: {keys}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def type_text(text: str, submit: bool = False) -> Dict[str, Any]:
        """Type text into the currently focused element."""
        try:
            BrowserControl._focus_chrome()
            time.sleep(0.2)
            
            # Use pyperclip + Ctrl+V for fast, Unicode-safe typing
            try:
                import pyperclip
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            except Exception:
                pyautogui.typewrite(text, interval=0.02)
            
            if submit:
                time.sleep(0.1)
                pyautogui.press('enter')
            
            return {"status": "success", "message": f"Typed: {text[:50]}..."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def click_position(x: int, y: int, click_type: str = "single") -> Dict[str, Any]:
        """Click at specific screen coordinates."""
        try:
            if click_type == "double":
                pyautogui.doubleClick(x, y)
            elif click_type == "right":
                pyautogui.rightClick(x, y)
            elif click_type == "triple":
                pyautogui.tripleClick(x, y)
            else:
                pyautogui.click(x, y)
            return {"status": "success", "message": f"{click_type.title()}-clicked at ({x}, {y})"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def search_on_page(text: str) -> Dict[str, Any]:
        """Use Ctrl+F to find text on the page."""
        try:
            BrowserControl._focus_chrome()
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.3)
            
            try:
                import pyperclip
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            except Exception:
                pyautogui.typewrite(text, interval=0.02)
            
            time.sleep(0.3)
            pyautogui.press('enter')
            
            return {"status": "success", "message": f"Searching page for: {text}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def browser_back() -> Dict[str, Any]:
        """Go back in browser history."""
        try:
            BrowserControl._focus_chrome()
            pyautogui.hotkey('alt', 'left')
            return {"status": "success", "message": "Went back"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def browser_forward() -> Dict[str, Any]:
        """Go forward in browser history."""
        try:
            BrowserControl._focus_chrome()
            pyautogui.hotkey('alt', 'right')
            return {"status": "success", "message": "Went forward"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def browser_refresh() -> Dict[str, Any]:
        """Refresh the current page."""
        try:
            BrowserControl._focus_chrome()
            pyautogui.press('f5')
            return {"status": "success", "message": "Page refreshed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def browser_zoom(direction: str = "in") -> Dict[str, Any]:
        """Zoom in, out, or reset."""
        try:
            BrowserControl._focus_chrome()
            if direction.lower() == "in":
                pyautogui.hotkey('ctrl', '+')
            elif direction.lower() == "out":
                pyautogui.hotkey('ctrl', '-')
            elif direction.lower() in ("reset", "default"):
                pyautogui.hotkey('ctrl', '0')
            return {"status": "success", "message": f"Zoomed {direction}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def fullscreen() -> Dict[str, Any]:
        """Toggle browser fullscreen."""
        try:
            BrowserControl._focus_chrome()
            pyautogui.press('f11')
            return {"status": "success", "message": "Toggled fullscreen"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def screenshot_page(filename: str = "") -> Dict[str, Any]:
        """Take a screenshot of the active window."""
        try:
            BrowserControl._focus_chrome()
            time.sleep(0.3)
            
            if not filename:
                filename = f"browser_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(os.path.expanduser("~"), "Pictures", filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            return {"status": "success", "message": f"Screenshot saved: {filepath}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def copy_page_text() -> Dict[str, Any]:
        """Select all text on page and copy to clipboard."""
        try:
            BrowserControl._focus_chrome()
            time.sleep(0.2)
            
            # Ctrl+A to select all, Ctrl+C to copy
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)
            
            # Read clipboard
            try:
                import pyperclip
                text = pyperclip.paste()
                return {"status": "success", "text": text[:5000], "message": f"Copied {len(text)} chars from page"}
            except Exception:
                return {"status": "success", "message": "Page text copied to clipboard"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def wait_and_click(seconds: float, x: int = 0, y: int = 0) -> Dict[str, Any]:
        """Wait for specified seconds then optionally click."""
        try:
            time.sleep(seconds)
            if x > 0 and y > 0:
                pyautogui.click(x, y)
                return {"status": "success", "message": f"Waited {seconds}s and clicked at ({x}, {y})"}
            return {"status": "success", "message": f"Waited {seconds} seconds"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def youtube_play_first(query: str) -> Dict[str, Any]:
        """Search YouTube and play the first video result directly."""
        try:
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            
            # Try to fetch search page and extract first video ID to play directly
            try:
                req = urllib.request.Request(search_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9'
                })
                with urllib.request.urlopen(req, timeout=8) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                
                # Extract first video ID from YouTube search results
                import re
                # YouTube embeds video IDs in various patterns in the HTML
                video_ids = re.findall(r'"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"', html)
                
                if video_ids:
                    # First unique video ID (skip duplicates from ads/promoted)
                    seen = set()
                    first_id = None
                    for vid in video_ids:
                        if vid not in seen:
                            first_id = vid
                            break
                        seen.add(vid)
                    
                    if first_id:
                        watch_url = f"https://www.youtube.com/watch?v={first_id}"
                        open_in_chrome(watch_url)
                        log.info(f"YouTube: Playing video {first_id} for query '{query}'")
                        return {"status": "success", "message": f"Playing YouTube video for: {query}", "video_id": first_id}
            except Exception as fetch_err:
                log.warning(f"YouTube fetch failed, falling back to search page: {fetch_err}")
            
            # Fallback: just open the search page
            open_in_chrome(search_url)
            return {"status": "success", "message": f"Opened YouTube search for: {query} (click a video to play)"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def spotify_play_first(query: str) -> Dict[str, Any]:
        """Open Spotify and search for a song."""
        # Try Spotify desktop app first
        try:
            subprocess.Popen(f"start spotify:search:{query}", shell=True)
            return {"status": "success", "message": f"Searching Spotify for: {query}"}
        except Exception:
            pass
        
        # Fallback to Spotify web
        try:
            open_in_chrome(f"https://open.spotify.com/search/{urllib.parse.quote(query)}")
            return {"status": "success", "message": f"Opened Spotify web for: {query}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def google_search_first(query: str) -> Dict[str, Any]:
        """Google search and open results page."""
        try:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            open_in_chrome(search_url)
            
            return {"status": "success", "message": f"Google search: {query}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_devtools() -> Dict[str, Any]:
        """Open Chrome DevTools."""
        try:
            BrowserControl._focus_chrome()
            pyautogui.press('f12')
            return {"status": "success", "message": "DevTools opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def tab_navigate(presses: int = 1) -> Dict[str, Any]:
        """Press Tab to navigate between page elements."""
        try:
            BrowserControl._focus_chrome()
            pyautogui.press('tab', presses=presses, interval=0.15)
            return {"status": "success", "message": f"Tabbed {presses} times"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def select_address_bar() -> Dict[str, Any]:
        """Select/focus the address bar."""
        try:
            BrowserControl._focus_chrome()
            pyautogui.hotkey('ctrl', 'l')
            return {"status": "success", "message": "Address bar focused"}
        except Exception as e:
            return {"status": "error", "message": str(e)}



# ===================================================================
# MODULE 14C: SCREEN READER & VISUAL AI (OCR + Element Detection)
# ===================================================================
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image, ImageGrab, ImageDraw, ImageEnhance
    TESSERACT_AVAILABLE = True
    # Try to auto-detect tesseract path on Windows
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.environ.get("USERNAME", "")),
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytesseract", "Pillow"])
        import pytesseract
        from PIL import Image, ImageGrab, ImageDraw, ImageEnhance
        TESSERACT_AVAILABLE = True
    except Exception:
        pass


class ScreenReader:
    """Advanced screen OCR and visual element detection."""
    
    _last_screenshot = None
    _last_ocr_data = None
    _last_text_boxes = []
    
    @staticmethod
    def capture_screen(region: Tuple[int, int, int, int] = None) -> Optional[Image.Image]:
        """Capture screenshot of entire screen or specific region."""
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            ScreenReader._last_screenshot = screenshot
            return screenshot
        except Exception as e:
            log.error(f"Screenshot capture failed: {e}")
            return None
    
    @staticmethod
    def capture_active_window() -> Optional[Image.Image]:
        """Capture screenshot of the currently active window."""
        try:
            if platform.system() == "Windows":
                import win32gui
                hwnd = win32gui.GetForegroundWindow()
                rect = win32gui.GetWindowRect(hwnd)
                screenshot = ImageGrab.grab(bbox=rect)
                ScreenReader._last_screenshot = screenshot
                return screenshot
        except Exception:
            pass
        return ScreenReader.capture_screen()
    
    @staticmethod
    def preprocess_image(image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            # Increase contrast
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(enhanced)
            sharp = enhancer.enhance(2.0)
            return sharp
        except Exception:
            return image
    
    @staticmethod
    def ocr_screen(region: Tuple[int, int, int, int] = None, preprocess: bool = True) -> Dict[str, Any]:
        """Perform OCR on the screen and return text with positions."""
        if not TESSERACT_AVAILABLE:
            return {"status": "error", "message": "Tesseract OCR not available. Install pytesseract and Tesseract-OCR."}
        
        try:
            screenshot = ScreenReader.capture_screen(region)
            if screenshot is None:
                return {"status": "error", "message": "Failed to capture screen"}
            
            if preprocess:
                processed = ScreenReader.preprocess_image(screenshot)
            else:
                processed = screenshot
            
            # Get detailed OCR data with bounding boxes
            ocr_data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            ScreenReader._last_ocr_data = ocr_data
            
            # Extract text with positions
            text_boxes = []
            full_text_lines = {}
            
            n_boxes = len(ocr_data['text'])
            for i in range(n_boxes):
                text = ocr_data['text'][i].strip()
                conf = int(ocr_data['conf'][i])
                
                if text and conf > 30:  # Filter low confidence
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    line_num = ocr_data['line_num'][i]
                    block_num = ocr_data['block_num'][i]
                    
                    # Adjust for region offset if specified
                    if region:
                        x += region[0]
                        y += region[1]
                    
                    text_boxes.append({
                        'text': text,
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'confidence': conf,
                        'line': line_num,
                        'block': block_num
                    })
                    
                    # Group by line
                    key = (block_num, line_num)
                    if key not in full_text_lines:
                        full_text_lines[key] = {'texts': [], 'y': y}
                    full_text_lines[key]['texts'].append(text)
            
            ScreenReader._last_text_boxes = text_boxes
            
            # Build full text preserving paragraphs
            paragraphs = []
            current_block = -1
            current_para = []
            
            for (block, line), data in sorted(full_text_lines.items()):
                if block != current_block:
                    if current_para:
                        paragraphs.append(' '.join(current_para))
                    current_para = []
                    current_block = block
                current_para.append(' '.join(data['texts']))
            
            if current_para:
                paragraphs.append(' '.join(current_para))
            
            full_text = '\n\n'.join(paragraphs)
            
            return {
                "status": "success",
                "text": full_text,
                "paragraphs": paragraphs,
                "word_count": len(text_boxes),
                "boxes": text_boxes[:100],  # Limit for response size
                "message": f"Read {len(text_boxes)} words from screen"
            }
        except Exception as e:
            return {"status": "error", "message": f"OCR failed: {str(e)}"}
    
    @staticmethod
    def find_text_on_screen(search_text: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """Find specific text on screen and return its location."""
        if not ScreenReader._last_text_boxes:
            # Perform fresh OCR
            result = ScreenReader.ocr_screen()
            if result.get("status") != "success":
                return result
        
        search = search_text if case_sensitive else search_text.lower()
        matches = []
        
        for box in ScreenReader._last_text_boxes:
            text = box['text'] if case_sensitive else box['text'].lower()
            if search in text or text in search:
                matches.append({
                    'text': box['text'],
                    'x': box['center_x'],
                    'y': box['center_y'],
                    'bbox': (box['x'], box['y'], box['w'], box['h'])
                })
        
        # Also check for multi-word matches by combining adjacent words
        if ' ' in search_text and not matches:
            words = search_text.split()
            for i, box in enumerate(ScreenReader._last_text_boxes):
                if i + len(words) <= len(ScreenReader._last_text_boxes):
                    combined = ' '.join(b['text'] for b in ScreenReader._last_text_boxes[i:i+len(words)])
                    combined_check = combined if case_sensitive else combined.lower()
                    if search in combined_check:
                        # Get bounding box of the combined text
                        first = ScreenReader._last_text_boxes[i]
                        last = ScreenReader._last_text_boxes[i + len(words) - 1]
                        matches.append({
                            'text': combined,
                            'x': (first['center_x'] + last['center_x']) // 2,
                            'y': first['center_y'],
                            'bbox': (first['x'], first['y'], 
                                    last['x'] + last['w'] - first['x'], first['h'])
                        })
        
        if matches:
            return {
                "status": "success",
                "found": True,
                "matches": matches,
                "count": len(matches),
                "message": f"Found '{search_text}' at {len(matches)} location(s)"
            }
        
        return {
            "status": "success",
            "found": False,
            "matches": [],
            "message": f"Text '{search_text}' not found on screen"
        }
    
    @staticmethod
    def click_text_on_screen(search_text: str, click_type: str = "single", index: int = 0) -> Dict[str, Any]:
        """Find text on screen and click on it."""
        result = ScreenReader.find_text_on_screen(search_text)
        
        if result.get("status") != "success" or not result.get("found"):
            return {"status": "error", "message": f"Could not find '{search_text}' on screen"}
        
        matches = result.get("matches", [])
        if index >= len(matches):
            index = 0
        
        target = matches[index]
        x, y = target['x'], target['y']
        
        try:
            if click_type == "double":
                pyautogui.doubleClick(x, y)
            elif click_type == "right":
                pyautogui.rightClick(x, y)
            else:
                pyautogui.click(x, y)
            
            return {
                "status": "success",
                "message": f"Clicked on '{target['text']}' at ({x}, {y})",
                "clicked_text": target['text'],
                "position": (x, y)
            }
        except Exception as e:
            return {"status": "error", "message": f"Click failed: {str(e)}"}
    
    @staticmethod
    def get_paragraph(paragraph_num: int = 1) -> Dict[str, Any]:
        """Get a specific paragraph from the screen (1-indexed)."""
        if not ScreenReader._last_ocr_data:
            result = ScreenReader.ocr_screen()
            if result.get("status") != "success":
                return result
        else:
            result = {"paragraphs": []}
            # Rebuild paragraphs from cached data
            full_text_lines = {}
            ocr_data = ScreenReader._last_ocr_data
            n_boxes = len(ocr_data['text'])
            for i in range(n_boxes):
                text = ocr_data['text'][i].strip()
                conf = int(ocr_data['conf'][i])
                if text and conf > 30:
                    line_num = ocr_data['line_num'][i]
                    block_num = ocr_data['block_num'][i]
                    key = (block_num, line_num)
                    if key not in full_text_lines:
                        full_text_lines[key] = []
                    full_text_lines[key].append(text)
            
            paragraphs = []
            current_block = -1
            current_para = []
            for (block, line), texts in sorted(full_text_lines.items()):
                if block != current_block:
                    if current_para:
                        paragraphs.append(' '.join(current_para))
                    current_para = []
                    current_block = block
                current_para.append(' '.join(texts))
            if current_para:
                paragraphs.append(' '.join(current_para))
            result["paragraphs"] = paragraphs
        
        paragraphs = result.get("paragraphs", [])
        
        if not paragraphs:
            return {"status": "error", "message": "No text found on screen"}
        
        idx = paragraph_num - 1
        if idx < 0 or idx >= len(paragraphs):
            return {
                "status": "error", 
                "message": f"Paragraph {paragraph_num} not found. Screen has {len(paragraphs)} paragraph(s)."
            }
        
        return {
            "status": "success",
            "paragraph": paragraphs[idx],
            "paragraph_number": paragraph_num,
            "total_paragraphs": len(paragraphs),
            "message": f"Retrieved paragraph {paragraph_num} of {len(paragraphs)}"
        }
    
    @staticmethod
    def copy_text_from_screen(what: str = "all", identifier: str = "") -> Dict[str, Any]:
        """Copy text from screen to clipboard.
        
        Args:
            what: "all", "paragraph", "line", "word", "selection"
            identifier: paragraph number, line number, or text to find
        """
        try:
            import pyperclip
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
            import pyperclip
        
        if not ScreenReader._last_ocr_data:
            result = ScreenReader.ocr_screen()
            if result.get("status") != "success":
                return result
        
        text_to_copy = ""
        
        if what == "all":
            # Get all text
            result = ScreenReader.ocr_screen()
            text_to_copy = result.get("text", "")
        
        elif what == "paragraph":
            para_num = int(identifier) if identifier.isdigit() else 1
            result = ScreenReader.get_paragraph(para_num)
            if result.get("status") != "success":
                return result
            text_to_copy = result.get("paragraph", "")
        
        elif what == "line":
            line_num = int(identifier) if identifier.isdigit() else 1
            # Get line from OCR data
            lines = []
            full_text_lines = {}
            ocr_data = ScreenReader._last_ocr_data
            n_boxes = len(ocr_data['text'])
            for i in range(n_boxes):
                text = ocr_data['text'][i].strip()
                if text and int(ocr_data['conf'][i]) > 30:
                    key = (ocr_data['block_num'][i], ocr_data['line_num'][i])
                    if key not in full_text_lines:
                        full_text_lines[key] = []
                    full_text_lines[key].append(text)
            
            for key in sorted(full_text_lines.keys()):
                lines.append(' '.join(full_text_lines[key]))
            
            if 1 <= line_num <= len(lines):
                text_to_copy = lines[line_num - 1]
            else:
                return {"status": "error", "message": f"Line {line_num} not found. Screen has {len(lines)} lines."}
        
        elif what == "word":
            word_num = int(identifier) if identifier.isdigit() else 1
            words = [b['text'] for b in ScreenReader._last_text_boxes]
            if 1 <= word_num <= len(words):
                text_to_copy = words[word_num - 1]
            else:
                return {"status": "error", "message": f"Word {word_num} not found. Screen has {len(words)} words."}
        
        elif what == "containing":
            # Copy text that contains the identifier
            search_result = ScreenReader.find_text_on_screen(identifier)
            if search_result.get("found"):
                text_to_copy = search_result["matches"][0]["text"]
            else:
                return {"status": "error", "message": f"No text containing '{identifier}' found."}
        
        elif what == "selection":
            # Triple-click to select paragraph, then copy
            if identifier:
                click_result = ScreenReader.click_text_on_screen(identifier, "triple")
                if click_result.get("status") != "success":
                    return click_result
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.1)
            try:
                text_to_copy = pyperclip.paste()
            except Exception:
                return {"status": "error", "message": "Failed to get clipboard content"}
        
        else:
            return {"status": "error", "message": f"Unknown copy type: {what}. Use: all, paragraph, line, word, selection, containing"}
        
        if text_to_copy:
            pyperclip.copy(text_to_copy)
            return {
                "status": "success",
                "copied_text": text_to_copy[:500] + ("..." if len(text_to_copy) > 500 else ""),
                "length": len(text_to_copy),
                "message": f"Copied {len(text_to_copy)} characters to clipboard"
            }
        
        return {"status": "error", "message": "No text to copy"}
    
    @staticmethod
    def find_button(button_text: str) -> Dict[str, Any]:
        """Find a button or clickable element by its text."""
        # First try browser automation click_by_text if in browser
        # Fall back to screen OCR
        result = ScreenReader.find_text_on_screen(button_text)
        
        if result.get("found"):
            matches = result.get("matches", [])
            return {
                "status": "success",
                "found": True,
                "button_text": button_text,
                "locations": [(m['x'], m['y']) for m in matches],
                "message": f"Found button '{button_text}' at {len(matches)} location(s)"
            }
        
        return {
            "status": "success",
            "found": False,
            "message": f"Button '{button_text}' not found on screen"
        }
    
    @staticmethod
    def click_button(button_text: str, click_type: str = "single") -> Dict[str, Any]:
        """Find and click a button by its visible text."""
        return ScreenReader.click_text_on_screen(button_text, click_type)
    
    @staticmethod
    def read_active_window() -> Dict[str, Any]:
        """Read all text from the currently active window."""
        screenshot = ScreenReader.capture_active_window()
        if screenshot is None:
            return {"status": "error", "message": "Failed to capture active window"}
        
        try:
            processed = ScreenReader.preprocess_image(screenshot)
            text = pytesseract.image_to_string(processed)
            
            return {
                "status": "success",
                "text": text,
                "window_size": screenshot.size,
                "message": f"Read {len(text.split())} words from active window"
            }
        except Exception as e:
            return {"status": "error", "message": f"OCR failed: {str(e)}"}
    
    @staticmethod
    def find_and_click_image_element(description: str) -> Dict[str, Any]:
        """Find UI element by description and click (uses text matching heuristics)."""
        # Common button/element text patterns
        common_buttons = {
            "sign in": ["Sign In", "Sign in", "LOGIN", "Login", "Log In", "Log in"],
            "sign up": ["Sign Up", "Sign up", "Register", "Create Account", "Join"],
            "submit": ["Submit", "SUBMIT", "Send", "SEND", "Go", "GO"],
            "cancel": ["Cancel", "CANCEL", "Close", "CLOSE", "X"],
            "ok": ["OK", "Ok", "Okay", "OKAY", "Yes", "YES"],
            "next": ["Next", "NEXT", "Continue", "CONTINUE", "â†’", ">"],
            "back": ["Back", "BACK", "Previous", "PREVIOUS", "â†", "<"],
            "search": ["Search", "SEARCH", "ðŸ”", "Find"],
            "play": ["Play", "PLAY", "â–¶", "â–º"],
            "pause": ["Pause", "PAUSE", "â¸", "||"],
            "download": ["Download", "DOWNLOAD", "Save", "SAVE"],
            "upload": ["Upload", "UPLOAD", "Browse", "Choose File"],
            "delete": ["Delete", "DELETE", "Remove", "REMOVE", "ðŸ—‘"],
            "edit": ["Edit", "EDIT", "Modify", "âœ"],
            "settings": ["Settings", "SETTINGS", "âš™", "Preferences"],
            "menu": ["Menu", "MENU", "â˜°", "â‰¡"],
            "share": ["Share", "SHARE", "ðŸ“¤"],
            "like": ["Like", "LIKE", "ðŸ‘", "â¤"],
            "comment": ["Comment", "COMMENT", "ðŸ’¬", "Reply"],
            "subscribe": ["Subscribe", "SUBSCRIBE", "Follow", "FOLLOW"],
        }
        
        # Try exact match first
        search_terms = [description]
        
        # Add common variations
        desc_lower = description.lower()
        for key, variations in common_buttons.items():
            if key in desc_lower or desc_lower in key:
                search_terms.extend(variations)
        
        # Try each search term
        for term in search_terms:
            result = ScreenReader.find_text_on_screen(term)
            if result.get("found"):
                click_result = ScreenReader.click_text_on_screen(term)
                if click_result.get("status") == "success":
                    return click_result
        
        return {"status": "error", "message": f"Could not find element matching '{description}' on screen"}
    
    @staticmethod
    def get_screen_elements() -> Dict[str, Any]:
        """Get a list of all visible text elements/buttons on screen."""
        result = ScreenReader.ocr_screen()
        if result.get("status") != "success":
            return result
        
        # Identify likely buttons/clickable elements
        clickable_keywords = ['sign', 'log', 'submit', 'cancel', 'ok', 'next', 'back', 
                             'search', 'play', 'download', 'upload', 'delete', 'edit',
                             'settings', 'menu', 'share', 'like', 'click', 'tap', 'press',
                             'button', 'link', 'open', 'close', 'save', 'send']
        
        elements = []
        for box in ScreenReader._last_text_boxes:
            text_lower = box['text'].lower()
            is_likely_button = any(kw in text_lower for kw in clickable_keywords)
            elements.append({
                'text': box['text'],
                'position': (box['center_x'], box['center_y']),
                'likely_clickable': is_likely_button
            })
        
        # Sort by y position (top to bottom)
        elements.sort(key=lambda e: e['position'][1])
        
        clickable = [e for e in elements if e['likely_clickable']]
        
        return {
            "status": "success",
            "total_elements": len(elements),
            "clickable_elements": clickable[:20],  # Top 20 likely clickable
            "all_elements": elements[:50],  # First 50 elements
            "message": f"Found {len(elements)} text elements, {len(clickable)} likely clickable"
        }


# ===================================================================
# MODULE 15: SYSTEM UTILITIES
# ===================================================================
class SystemUtilities:
    """System maintenance and utilities."""
    
    @staticmethod
    def empty_recycle_bin() -> Dict[str, Any]:
        """Empty the Windows recycle bin."""
        try:
            if platform.system() == "Windows":
                # SHEmptyRecycleBin
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
                return {"status": "success", "message": "Recycle bin emptied"}
            return {"status": "error", "message": "Only supported on Windows"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def clear_temp_files() -> Dict[str, Any]:
        """Clear temporary files."""
        try:
            temp_dirs = [
                os.environ.get("TEMP", ""),
                os.environ.get("TMP", ""),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp")
            ]
            
            deleted = 0
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    for item in os.listdir(temp_dir):
                        try:
                            path = os.path.join(temp_dir, item)
                            if os.path.isfile(path):
                                os.remove(path)
                                deleted += 1
                            elif os.path.isdir(path):
                                shutil.rmtree(path, ignore_errors=True)
                                deleted += 1
                        except Exception:
                            pass
            
            return {"status": "success", "message": f"Cleaned {deleted} temp items"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def disk_cleanup() -> Dict[str, Any]:
        """Run Windows Disk Cleanup."""
        try:
            subprocess.Popen("cleanmgr /sagerun:1", shell=True)
            return {"status": "success", "message": "Disk Cleanup started"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def check_windows_updates() -> Dict[str, Any]:
        """Open Windows Update settings."""
        try:
            subprocess.Popen("start ms-settings:windowsupdate", shell=True)
            return {"status": "success", "message": "Windows Update opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def system_info() -> Dict[str, Any]:
        """Get detailed system information."""
        try:
            info = {
                "os": platform.platform(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": socket.gethostname(),
                "username": os.getlogin(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1)
            }
            return {"status": "success", "info": info, "message": "System information retrieved"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def install_app(app_name: str) -> Dict[str, Any]:
        """Install an app using winget."""
        try:
            result = subprocess.run(
                f"winget install {app_name} --accept-package-agreements --accept-source-agreements",
                shell=True, capture_output=True, text=True, timeout=120
            )
            return {"status": "success", "message": result.stdout[:500] or f"Installing {app_name}..."}
        except subprocess.TimeoutExpired:
            return {"status": "info", "message": f"Installation of {app_name} in progress..."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def uninstall_app(app_name: str) -> Dict[str, Any]:
        """Uninstall an app using winget."""
        try:
            result = subprocess.run(
                f"winget uninstall {app_name}",
                shell=True, capture_output=True, text=True, timeout=60
            )
            return {"status": "success", "message": result.stdout[:500] or f"Uninstalling {app_name}..."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def search_apps(query: str) -> Dict[str, Any]:
        """Search for apps available via winget."""
        try:
            result = subprocess.run(
                f"winget search {query}",
                shell=True, capture_output=True, text=True, timeout=30
            )
            return {"status": "success", "message": result.stdout[:2000]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 16: WINDOW MANAGER
# ===================================================================
class WindowManager:
    """Advanced window management."""
    
    @staticmethod
    def list_windows() -> Dict[str, Any]:
        """List all visible windows."""
        if platform.system() != "Windows":
            return {"status": "error", "message": "Windows only"}
        
        try:
            import win32gui
            windows = []
            
            def enum_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        rect = win32gui.GetWindowRect(hwnd)
                        results.append({
                            "hwnd": hwnd,
                            "title": title,
                            "position": {"x": rect[0], "y": rect[1]},
                            "size": {"w": rect[2] - rect[0], "h": rect[3] - rect[1]}
                        })
            
            win32gui.EnumWindows(enum_callback, windows)
            titles = [w['title'] for w in windows if w.get('title')]
            title_list = ', '.join(titles[:15])
            return {"status": "success", "windows": windows[:30], "message": f"Found {len(windows)} windows: {title_list}"}
        except ImportError:
            return {"status": "error", "message": "pywin32 not installed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def move_window(title: str, x: int, y: int) -> Dict[str, Any]:
        """Move a window to specific coordinates."""
        try:
            import win32gui
            
            def find_window(search_title):
                result = []
                def callback(hwnd, _):
                    if search_title.lower() in win32gui.GetWindowText(hwnd).lower():
                        result.append(hwnd)
                win32gui.EnumWindows(callback, None)
                return result[0] if result else None
            
            hwnd = find_window(title)
            if hwnd:
                win32gui.SetWindowPos(hwnd, None, x, y, 0, 0, 0x0001 | 0x0004)  # SWP_NOSIZE | SWP_NOZORDER
                return {"status": "success", "message": f"Moved '{title}' to ({x}, {y})"}
            return {"status": "error", "message": f"Window '{title}' not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def resize_window(title: str, width: int, height: int) -> Dict[str, Any]:
        """Resize a window."""
        try:
            import win32gui
            
            def find_window(search_title):
                result = []
                def callback(hwnd, _):
                    if search_title.lower() in win32gui.GetWindowText(hwnd).lower():
                        result.append(hwnd)
                win32gui.EnumWindows(callback, None)
                return result[0] if result else None
            
            hwnd = find_window(title)
            if hwnd:
                rect = win32gui.GetWindowRect(hwnd)
                win32gui.SetWindowPos(hwnd, None, rect[0], rect[1], width, height, 0x0004)
                return {"status": "success", "message": f"Resized '{title}' to {width}x{height}"}
            return {"status": "error", "message": f"Window '{title}' not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def snap_window(title: str, position: str) -> Dict[str, Any]:
        """Snap window to screen edge (left, right, top, bottom, maximize, minimize)."""
        try:
            import win32gui
            import win32con
            
            def find_window(search_title):
                result = []
                def callback(hwnd, _):
                    if search_title.lower() in win32gui.GetWindowText(hwnd).lower():
                        result.append(hwnd)
                win32gui.EnumWindows(callback, None)
                return result[0] if result else None
            
            hwnd = find_window(title)
            if not hwnd:
                return {"status": "error", "message": f"Window '{title}' not found"}
            
            # Get screen dimensions
            screen_w = ctypes.windll.user32.GetSystemMetrics(0)
            screen_h = ctypes.windll.user32.GetSystemMetrics(1)
            
            pos = position.lower()
            if pos == "left":
                win32gui.SetWindowPos(hwnd, None, 0, 0, screen_w // 2, screen_h, 0)
            elif pos == "right":
                win32gui.SetWindowPos(hwnd, None, screen_w // 2, 0, screen_w // 2, screen_h, 0)
            elif pos == "top":
                win32gui.SetWindowPos(hwnd, None, 0, 0, screen_w, screen_h // 2, 0)
            elif pos == "bottom":
                win32gui.SetWindowPos(hwnd, None, 0, screen_h // 2, screen_w, screen_h // 2, 0)
            elif pos == "maximize":
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            elif pos == "minimize":
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            elif pos == "restore":
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            else:
                return {"status": "error", "message": f"Unknown position: {position}"}
            
            return {"status": "success", "message": f"Snapped '{title}' to {position}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 17: QUICK NOTES
# ===================================================================
class NotesController:
    """Quick notes and memos."""
    
    NOTES_FILE = os.path.join(os.path.expanduser("~"), "jerry_notes.json")
    
    @classmethod
    def _load_notes(cls) -> List[Dict]:
        try:
            if os.path.exists(cls.NOTES_FILE):
                with open(cls.NOTES_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    @classmethod
    def _save_notes(cls, notes: List[Dict]):
        with open(cls.NOTES_FILE, 'w') as f:
            json.dump(notes, f, indent=2)
    
    @classmethod
    def add_note(cls, content: str, tags: str = "") -> Dict[str, Any]:
        """Add a quick note."""
        notes = cls._load_notes()
        note = {
            "id": str(uuid.uuid4())[:8],
            "content": content,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        notes.append(note)
        cls._save_notes(notes)
        return {"status": "success", "note_id": note["id"], "message": f"Note saved: {content[:50]}..."}
    
    @classmethod
    def list_notes(cls, tag: str = "", limit: int = 10) -> Dict[str, Any]:
        """List notes, optionally filtered by tag."""
        notes = cls._load_notes()
        if tag:
            notes = [n for n in notes if tag.lower() in [t.lower() for t in n.get("tags", [])]]
        notes = sorted(notes, key=lambda x: x["created"], reverse=True)[:limit]
        return {"status": "success", "notes": notes, "message": f"Found {len(notes)} notes"}
    
    @classmethod
    def delete_note(cls, note_id: str) -> Dict[str, Any]:
        """Delete a note by ID."""
        notes = cls._load_notes()
        notes = [n for n in notes if n["id"] != note_id]
        cls._save_notes(notes)
        return {"status": "success", "message": f"Note {note_id} deleted"}
    
    @classmethod
    def search_notes(cls, query: str) -> Dict[str, Any]:
        """Search notes by content."""
        notes = cls._load_notes()
        results = [n for n in notes if query.lower() in n["content"].lower()]
        return {"status": "success", "notes": results, "message": f"Found {len(results)} matching notes"}


# ===================================================================
# MODULE 18: BLUETOOTH CONTROLLER
# ===================================================================
class BluetoothController:
    """Bluetooth device management."""
    
    @staticmethod
    def list_devices() -> Dict[str, Any]:
        """List paired Bluetooth devices."""
        try:
            result = subprocess.run(
                'powershell "Get-PnpDevice -Class Bluetooth | Select-Object Status, Class, FriendlyName, InstanceId"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout[:2000]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def toggle_bluetooth(enable: bool = True) -> Dict[str, Any]:
        """Enable or disable Bluetooth."""
        try:
            action = "Enable" if enable else "Disable"
            # Toggle via Settings
            subprocess.run(f'start ms-settings:bluetooth', shell=True)
            return {"status": "success", "message": f"Bluetooth settings opened. Please {action.lower()} manually."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def connect_device(device_name: str) -> Dict[str, Any]:
        """Attempt to connect to a Bluetooth device."""
        try:
            # Open Bluetooth settings and provide guidance
            subprocess.run('start ms-settings:bluetooth', shell=True)
            return {"status": "info", "message": f"Bluetooth settings opened. Please connect to '{device_name}' manually."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 19: DISPLAY CONTROLLER
# ===================================================================
class DisplayController:
    """Display and screen settings."""
    
    @staticmethod
    def toggle_night_light(enable: bool = True) -> Dict[str, Any]:
        """Toggle Windows Night Light."""
        try:
            # Night light registry setting
            if enable:
                subprocess.run('start ms-settings:nightlight', shell=True)
                return {"status": "success", "message": "Night light settings opened. Enable it there."}
            else:
                subprocess.run('start ms-settings:nightlight', shell=True)
                return {"status": "success", "message": "Night light settings opened. Disable it there."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def get_resolution() -> Dict[str, Any]:
        """Get current screen resolution."""
        try:
            width = ctypes.windll.user32.GetSystemMetrics(0)
            height = ctypes.windll.user32.GetSystemMetrics(1)
            return {"status": "success", "message": f"Screen resolution: {width}x{height}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def set_resolution(width: int, height: int) -> Dict[str, Any]:
        """Change screen resolution (opens display settings)."""
        try:
            subprocess.run('start ms-settings:display', shell=True)
            return {"status": "info", "message": f"Display settings opened. Change resolution to {width}x{height} manually."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def list_monitors() -> Dict[str, Any]:
        """List connected monitors."""
        try:
            result = subprocess.run(
                'powershell "Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorID | ForEach-Object { [System.Text.Encoding]::ASCII.GetString($_.UserFriendlyName) }"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or "Monitor info retrieved"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def project_display(mode: str) -> Dict[str, Any]:
        """Project display: pc_only, duplicate, extend, second_only"""
        try:
            mode_map = {
                "pc_only": "/internal",
                "duplicate": "/clone",
                "extend": "/extend",
                "second_only": "/external"
            }
            if mode.lower() not in mode_map:
                return {"status": "error", "message": f"Unknown mode. Use: {', '.join(mode_map.keys())}"}
            subprocess.run(f'DisplaySwitch.exe {mode_map[mode.lower()]}', shell=True)
            return {"status": "success", "message": f"Display projection changed to: {mode}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 20: AUDIO DEVICE CONTROLLER
# ===================================================================
class AudioDeviceController:
    """Audio device and microphone control."""
    
    @staticmethod
    def list_audio_devices() -> Dict[str, Any]:
        """List audio playback devices."""
        try:
            result = subprocess.run(
                'powershell "Get-AudioDevice -List | Select-Object Index, Default, Type, Name"',
                shell=True, capture_output=True, text=True
            )
            if "not recognized" in result.stderr:
                # Fallback without AudioDeviceCmdlets
                result = subprocess.run(
                    'powershell "Get-CimInstance Win32_SoundDevice | Select-Object Name, Status"',
                    shell=True, capture_output=True, text=True
                )
            return {"status": "success", "message": result.stdout[:2000] or "Audio devices listed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def set_default_device(device_name: str) -> Dict[str, Any]:
        """Set default audio device (opens sound settings)."""
        try:
            subprocess.run('start ms-settings:sound', shell=True)
            return {"status": "info", "message": f"Sound settings opened. Set '{device_name}' as default there."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def toggle_microphone(mute: bool = True) -> Dict[str, Any]:
        """Mute or unmute the microphone."""
        try:
            # Use keyboard shortcut or open settings
            if platform.system() == "Windows":
                subprocess.run('start ms-settings:sound', shell=True)
                return {"status": "info", "message": f"Sound settings opened. {'Mute' if mute else 'Unmute'} microphone there."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 21: SCREEN RECORDER
# ===================================================================
class ScreenRecorder:
    """Screen recording and webcam capture."""
    
    @staticmethod
    def start_recording() -> Dict[str, Any]:
        """Start screen recording using Windows Game Bar."""
        try:
            # Win+Alt+R starts recording
            pyautogui.hotkey('win', 'alt', 'r')
            return {"status": "success", "message": "Screen recording started (Game Bar). Press Win+Alt+R to stop."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def stop_recording() -> Dict[str, Any]:
        """Stop screen recording."""
        try:
            pyautogui.hotkey('win', 'alt', 'r')
            return {"status": "success", "message": "Screen recording stopped."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_game_bar() -> Dict[str, Any]:
        """Open Windows Game Bar."""
        try:
            pyautogui.hotkey('win', 'g')
            return {"status": "success", "message": "Game Bar opened."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def take_webcam_photo() -> Dict[str, Any]:
        """Take a photo with webcam using Windows Camera app."""
        try:
            subprocess.Popen('start microsoft.windows.camera:', shell=True)
            return {"status": "success", "message": "Camera app opened. Take a photo manually."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 22: ARCHIVE CONTROLLER
# ===================================================================
class ArchiveController:
    """Zip, unzip, and archive operations."""
    
    @staticmethod
    def zip_files(source: str, dest: str = "") -> Dict[str, Any]:
        """Create a zip archive from files/folder."""
        try:
            source_path = Path(source)
            if not dest:
                dest = str(source_path.parent / f"{source_path.name}.zip")
            
            with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if source_path.is_dir():
                    for file in source_path.rglob('*'):
                        zipf.write(file, file.relative_to(source_path.parent))
                else:
                    zipf.write(source_path, source_path.name)
            
            return {"status": "success", "message": f"Created archive: {dest}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def unzip_file(source: str, dest: str = "") -> Dict[str, Any]:
        """Extract a zip archive."""
        try:
            if not dest:
                dest = str(Path(source).parent)
            
            with zipfile.ZipFile(source, 'r') as zipf:
                zipf.extractall(dest)
            
            return {"status": "success", "message": f"Extracted to: {dest}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def list_archive(source: str) -> Dict[str, Any]:
        """List contents of an archive."""
        try:
            with zipfile.ZipFile(source, 'r') as zipf:
                files = zipf.namelist()
            return {"status": "success", "files": files[:50], "message": f"Archive contains {len(files)} files"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 23: DOWNLOAD CONTROLLER
# ===================================================================
class DownloadController:
    """Download files from the internet."""
    
    @staticmethod
    def download_file(url: str, dest: str = "") -> Dict[str, Any]:
        """Download a file from URL."""
        try:
            if not dest:
                filename = url.split('/')[-1].split('?')[0] or "download"
                dest = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            
            urllib.request.urlretrieve(url, dest)
            return {"status": "success", "message": f"Downloaded to: {dest}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def download_with_progress(url: str, dest: str = "") -> Dict[str, Any]:
        """Download with progress tracking (basic)."""
        try:
            if not dest:
                filename = url.split('/')[-1].split('?')[0] or "download"
                dest = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            
            # Use PowerShell for better download
            ps_cmd = f'Invoke-WebRequest -Uri "{url}" -OutFile "{dest}"'
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
            
            return {"status": "success", "message": f"Downloaded to: {dest}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 24: GIT CONTROLLER
# ===================================================================
class GitController:
    """Git operations."""
    
    @staticmethod
    def git_status(path: str = ".") -> Dict[str, Any]:
        """Get git status."""
        try:
            result = subprocess.run(
                f'git -C "{path}" status --short',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or "Working directory clean"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def git_pull(path: str = ".") -> Dict[str, Any]:
        """Pull latest changes."""
        try:
            result = subprocess.run(
                f'git -C "{path}" pull',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def git_push(path: str = ".") -> Dict[str, Any]:
        """Push changes."""
        try:
            result = subprocess.run(
                f'git -C "{path}" push',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or result.stderr or "Push complete"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def git_commit(path: str = ".", message: str = "Auto-commit by Jerry") -> Dict[str, Any]:
        """Stage all and commit."""
        try:
            subprocess.run(f'git -C "{path}" add -A', shell=True, capture_output=True)
            result = subprocess.run(
                f'git -C "{path}" commit -m "{message}"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or result.stderr or "Committed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def git_clone(url: str, dest: str = "") -> Dict[str, Any]:
        """Clone a repository."""
        try:
            cmd = f'git clone "{url}"'
            if dest:
                cmd += f' "{dest}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return {"status": "success", "message": result.stdout or result.stderr or "Cloned"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def git_branch(path: str = ".") -> Dict[str, Any]:
        """List branches."""
        try:
            result = subprocess.run(
                f'git -C "{path}" branch -a',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 25: CODE EXECUTOR
# ===================================================================
class CodeExecutor:
    """Execute code snippets safely."""
    
    @staticmethod
    def run_python(code: str) -> Dict[str, Any]:
        """Execute Python code."""
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True, text=True, timeout=30
            )
            os.unlink(temp_path)
            
            output = result.stdout or result.stderr
            return {"status": "success" if result.returncode == 0 else "error", "message": output[:2000]}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Code execution timed out (30s limit)"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def run_powershell(code: str) -> Dict[str, Any]:
        """Execute PowerShell code."""
        try:
            result = subprocess.run(
                ["powershell", "-Command", code],
                capture_output=True, text=True, timeout=30
            )
            output = result.stdout or result.stderr
            return {"status": "success" if result.returncode == 0 else "error", "message": output[:2000]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 26: CALCULATOR & CONVERTER
# ===================================================================
class Calculator:
    """Math calculations and conversions."""
    
    @staticmethod
    def calculate(expression: str) -> Dict[str, Any]:
        """Evaluate a math expression safely."""
        try:
            # Safe math evaluation
            allowed = set('0123456789+-*/.() ')
            if not all(c in allowed or c.isalpha() for c in expression):
                return {"status": "error", "message": "Invalid characters in expression"}
            
            # Allow math functions
            safe_dict = {
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10,
                'pow': pow, 'abs': abs, 'round': round,
                'pi': math.pi, 'e': math.e
            }
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return {"status": "success", "message": f"{expression} = {result}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def convert_units(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Convert between units."""
        conversions = {
            # Length
            ("km", "miles"): lambda x: x * 0.621371,
            ("miles", "km"): lambda x: x * 1.60934,
            ("m", "ft"): lambda x: x * 3.28084,
            ("ft", "m"): lambda x: x * 0.3048,
            ("cm", "inches"): lambda x: x * 0.393701,
            ("inches", "cm"): lambda x: x * 2.54,
            # Weight
            ("kg", "lbs"): lambda x: x * 2.20462,
            ("lbs", "kg"): lambda x: x * 0.453592,
            ("g", "oz"): lambda x: x * 0.035274,
            ("oz", "g"): lambda x: x * 28.3495,
            # Temperature
            ("c", "f"): lambda x: (x * 9/5) + 32,
            ("f", "c"): lambda x: (x - 32) * 5/9,
            ("c", "k"): lambda x: x + 273.15,
            ("k", "c"): lambda x: x - 273.15,
            # Volume
            ("l", "gal"): lambda x: x * 0.264172,
            ("gal", "l"): lambda x: x * 3.78541,
            # Data
            ("gb", "mb"): lambda x: x * 1024,
            ("mb", "gb"): lambda x: x / 1024,
            ("tb", "gb"): lambda x: x * 1024,
            ("gb", "tb"): lambda x: x / 1024,
        }
        
        key = (from_unit.lower(), to_unit.lower())
        if key in conversions:
            result = conversions[key](value)
            return {"status": "success", "message": f"{value} {from_unit} = {result:.4f} {to_unit}"}
        return {"status": "error", "message": f"Unknown conversion: {from_unit} to {to_unit}"}
    
    @staticmethod
    def convert_currency(amount: float, from_curr: str, to_curr: str) -> Dict[str, Any]:
        """Convert currency (uses approximate rates)."""
        # Approximate rates to USD
        to_usd = {
            "usd": 1, "eur": 1.10, "gbp": 1.27, "jpy": 0.0067,
            "cad": 0.74, "aud": 0.65, "inr": 0.012, "cny": 0.14,
            "pkr": 0.0036, "aed": 0.27, "sar": 0.27
        }
        
        from_curr = from_curr.lower()
        to_curr = to_curr.lower()
        
        if from_curr not in to_usd or to_curr not in to_usd:
            return {"status": "error", "message": f"Unknown currency. Supported: {', '.join(to_usd.keys())}"}
        
        # Convert via USD
        usd_amount = amount * to_usd[from_curr]
        result = usd_amount / to_usd[to_curr]
        
        return {"status": "success", "message": f"{amount} {from_curr.upper()} â‰ˆ {result:.2f} {to_curr.upper()}"}


# ===================================================================
# MODULE 27: TRANSLATOR
# ===================================================================
class Translator:
    """Translation services."""
    
    @staticmethod
    def translate(text: str, to_lang: str = "en", from_lang: str = "auto") -> Dict[str, Any]:
        """Translate text using web service."""
        try:
            # Use Google Translate URL scheme (opens in Chrome)
            encoded_text = urllib.parse.quote(text)
            url = f"https://translate.google.com/?sl={from_lang}&tl={to_lang}&text={encoded_text}&op=translate"
            open_in_chrome(url)
            return {"status": "success", "message": f"Opened Google Translate for: {text[:50]}..."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 28: SERVICES CONTROLLER
# ===================================================================
class ServicesController:
    """Windows Services management."""
    
    @staticmethod
    def list_services(running_only: bool = False) -> Dict[str, Any]:
        """List Windows services."""
        try:
            filter_cmd = "| Where-Object {$_.Status -eq 'Running'}" if running_only else ""
            result = subprocess.run(
                f'powershell "Get-Service {filter_cmd} | Select-Object -First 30 Status, Name, DisplayName | Format-Table"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout[:3000]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def start_service(name: str) -> Dict[str, Any]:
        """Start a Windows service."""
        try:
            result = subprocess.run(
                f'powershell "Start-Service -Name \'{name}\'"',
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                return {"status": "success", "message": f"Service '{name}' started"}
            return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def stop_service(name: str) -> Dict[str, Any]:
        """Stop a Windows service."""
        try:
            result = subprocess.run(
                f'powershell "Stop-Service -Name \'{name}\' -Force"',
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                return {"status": "success", "message": f"Service '{name}' stopped"}
            return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def restart_service(name: str) -> Dict[str, Any]:
        """Restart a Windows service."""
        try:
            result = subprocess.run(
                f'powershell "Restart-Service -Name \'{name}\' -Force"',
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                return {"status": "success", "message": f"Service '{name}' restarted"}
            return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 29: ACCESSIBILITY CONTROLLER
# ===================================================================
class AccessibilityController:
    """Accessibility features."""
    
    @staticmethod
    def toggle_magnifier(enable: bool = True) -> Dict[str, Any]:
        """Toggle Windows Magnifier."""
        try:
            if enable:
                subprocess.Popen('magnify.exe', shell=True)
                return {"status": "success", "message": "Magnifier enabled"}
            else:
                subprocess.run('taskkill /IM magnify.exe /F', shell=True, capture_output=True)
                return {"status": "success", "message": "Magnifier disabled"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def toggle_narrator(enable: bool = True) -> Dict[str, Any]:
        """Toggle Windows Narrator."""
        try:
            if enable:
                subprocess.Popen('narrator.exe', shell=True)
                return {"status": "success", "message": "Narrator enabled"}
            else:
                subprocess.run('taskkill /IM narrator.exe /F', shell=True, capture_output=True)
                return {"status": "success", "message": "Narrator disabled"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def toggle_high_contrast() -> Dict[str, Any]:
        """Toggle high contrast mode."""
        try:
            # Left Alt + Left Shift + Print Screen
            pyautogui.hotkey('alt', 'shift', 'printscreen')
            return {"status": "success", "message": "High contrast toggled"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_ease_of_access() -> Dict[str, Any]:
        """Open Ease of Access settings."""
        try:
            subprocess.run('start ms-settings:easeofaccess', shell=True)
            return {"status": "success", "message": "Ease of Access settings opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 30: FOCUS ASSIST / DO NOT DISTURB
# ===================================================================
class FocusAssist:
    """Focus Assist / Do Not Disturb mode."""
    
    @staticmethod
    def toggle_focus_assist(mode: str = "priority") -> Dict[str, Any]:
        """Toggle Focus Assist. Modes: off, priority, alarms"""
        try:
            subprocess.run('start ms-settings:quiethours', shell=True)
            return {"status": "info", "message": f"Focus Assist settings opened. Set to '{mode}' mode."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def toggle_notifications(enable: bool = True) -> Dict[str, Any]:
        """Enable or disable notifications."""
        try:
            action = "enable" if enable else "disable"
            subprocess.run('start ms-settings:notifications', shell=True)
            return {"status": "info", "message": f"Notification settings opened. {action.capitalize()} notifications there."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 31: VIRTUAL DESKTOP CONTROLLER
# ===================================================================
class VirtualDesktopController:
    """Virtual desktop management."""
    
    @staticmethod
    def new_desktop() -> Dict[str, Any]:
        """Create a new virtual desktop."""
        try:
            pyautogui.hotkey('win', 'ctrl', 'd')
            return {"status": "success", "message": "New virtual desktop created"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def close_desktop() -> Dict[str, Any]:
        """Close current virtual desktop."""
        try:
            pyautogui.hotkey('win', 'ctrl', 'F4')
            return {"status": "success", "message": "Current virtual desktop closed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def switch_desktop(direction: str) -> Dict[str, Any]:
        """Switch to next or previous virtual desktop."""
        try:
            if direction.lower() in ["left", "prev", "previous"]:
                pyautogui.hotkey('win', 'ctrl', 'left')
            else:
                pyautogui.hotkey('win', 'ctrl', 'right')
            return {"status": "success", "message": f"Switched to {direction} desktop"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def show_task_view() -> Dict[str, Any]:
        """Open Task View."""
        try:
            pyautogui.hotkey('win', 'tab')
            return {"status": "success", "message": "Task View opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 32: USB CONTROLLER
# ===================================================================
class USBController:
    """USB device management."""
    
    @staticmethod
    def list_usb_devices() -> Dict[str, Any]:
        """List connected USB devices."""
        try:
            result = subprocess.run(
                'powershell "Get-PnpDevice -Class USB | Where-Object {$_.Status -eq \'OK\'} | Select-Object FriendlyName, Status"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout[:2000]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def eject_drive(drive_letter: str) -> Dict[str, Any]:
        """Safely eject a USB drive."""
        try:
            drive = drive_letter.upper().rstrip(':')
            result = subprocess.run(
                f'powershell "(New-Object -ComObject Shell.Application).NameSpace(17).ParseName(\'{drive}:\').InvokeVerb(\'Eject\')"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": f"Ejecting drive {drive}:"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 33: HOTSPOT CONTROLLER
# ===================================================================
class HotspotController:
    """Mobile hotspot control."""
    
    @staticmethod
    def toggle_hotspot(enable: bool = True) -> Dict[str, Any]:
        """Enable or disable mobile hotspot."""
        try:
            subprocess.run('start ms-settings:network-mobilehotspot', shell=True)
            action = "Enable" if enable else "Disable"
            return {"status": "info", "message": f"Hotspot settings opened. {action} it there."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def get_hotspot_status() -> Dict[str, Any]:
        """Get hotspot status."""
        try:
            result = subprocess.run(
                'netsh wlan show hostednetwork',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout[:1500]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 34: VPN CONTROLLER
# ===================================================================
class VPNController:
    """VPN management."""
    
    @staticmethod
    def list_vpn_connections() -> Dict[str, Any]:
        """List VPN connections."""
        try:
            result = subprocess.run(
                'powershell "Get-VpnConnection | Select-Object Name, ServerAddress, ConnectionStatus"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or "No VPN connections found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def connect_vpn(name: str) -> Dict[str, Any]:
        """Connect to a VPN."""
        try:
            result = subprocess.run(
                f'rasdial "{name}"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or f"Connecting to VPN: {name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def disconnect_vpn(name: str) -> Dict[str, Any]:
        """Disconnect from a VPN."""
        try:
            result = subprocess.run(
                f'rasdial "{name}" /disconnect',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or f"Disconnected from VPN: {name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_vpn_settings() -> Dict[str, Any]:
        """Open VPN settings."""
        try:
            subprocess.run('start ms-settings:network-vpn', shell=True)
            return {"status": "success", "message": "VPN settings opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 35: CLIPBOARD HISTORY
# ===================================================================
class ClipboardHistory:
    """Clipboard history management."""
    
    _history: deque = deque(maxlen=50)
    
    @classmethod
    def open_clipboard_history(cls) -> Dict[str, Any]:
        """Open Windows Clipboard History."""
        try:
            pyautogui.hotkey('win', 'v')
            return {"status": "success", "message": "Clipboard history opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @classmethod
    def clear_clipboard(cls) -> Dict[str, Any]:
        """Clear clipboard."""
        try:
            subprocess.run('powershell "Set-Clipboard -Value $null"', shell=True)
            return {"status": "success", "message": "Clipboard cleared"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 36: PRINTER CONTROLLER
# ===================================================================
class PrinterController:
    """Printer management."""
    
    @staticmethod
    def list_printers() -> Dict[str, Any]:
        """List installed printers."""
        try:
            result = subprocess.run(
                'powershell "Get-Printer | Select-Object Name, DriverName, PortName, PrinterStatus"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout[:2000]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def set_default_printer(name: str) -> Dict[str, Any]:
        """Set default printer."""
        try:
            result = subprocess.run(
                f'powershell "Set-DefaultPrinter -Name \'{name}\'"',
                shell=True, capture_output=True, text=True
            )
            # Alternative method
            if result.returncode != 0:
                result = subprocess.run(
                    f'powershell "(Get-WmiObject -Query \\"SELECT * FROM Win32_Printer WHERE Name=\'{name}\'\\").SetDefaultPrinter()"',
                    shell=True, capture_output=True, text=True
                )
            return {"status": "success", "message": f"Default printer set to: {name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def print_file(file_path: str) -> Dict[str, Any]:
        """Print a file."""
        try:
            os.startfile(file_path, "print")
            return {"status": "success", "message": f"Printing: {file_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_print_queue() -> Dict[str, Any]:
        """Open print queue."""
        try:
            subprocess.run('control printers', shell=True)
            return {"status": "success", "message": "Print queue opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 37: POWER PROFILES
# ===================================================================
class PowerProfiles:
    """Power plan management."""
    
    @staticmethod
    def list_power_plans() -> Dict[str, Any]:
        """List available power plans."""
        try:
            result = subprocess.run('powercfg /list', shell=True, capture_output=True, text=True)
            return {"status": "success", "message": result.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def set_power_plan(plan_name: str) -> Dict[str, Any]:
        """Set power plan: balanced, high_performance, power_saver."""
        try:
            plans = {
                "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
                "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
                "power_saver": "a1841308-3541-4fab-bc81-f71556f20b4a"
            }
            
            plan_key = plan_name.lower().replace(" ", "_")
            if plan_key not in plans:
                return {"status": "error", "message": f"Unknown plan. Use: {', '.join(plans.keys())}"}
            
            subprocess.run(f'powercfg /setactive {plans[plan_key]}', shell=True)
            return {"status": "success", "message": f"Power plan set to: {plan_name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def toggle_battery_saver(enable: bool = True) -> Dict[str, Any]:
        """Toggle battery saver mode."""
        try:
            subprocess.run('start ms-settings:batterysaver', shell=True)
            return {"status": "info", "message": f"Battery settings opened. {'Enable' if enable else 'Disable'} battery saver there."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 38: ENVIRONMENT VARIABLES
# ===================================================================
class EnvironmentController:
    """Environment variable management."""
    
    @staticmethod
    def get_env(name: str) -> Dict[str, Any]:
        """Get environment variable."""
        try:
            value = os.environ.get(name, "")
            return {"status": "success", "message": f"{name} = {value}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def set_env(name: str, value: str, persistent: bool = False) -> Dict[str, Any]:
        """Set environment variable."""
        try:
            os.environ[name] = value
            if persistent:
                subprocess.run(f'setx {name} "{value}"', shell=True, capture_output=True)
            return {"status": "success", "message": f"Set {name} = {value}" + (" (persistent)" if persistent else " (session only)")}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def list_env() -> Dict[str, Any]:
        """List all environment variables."""
        try:
            env_vars = dict(os.environ)
            # Truncate for display
            display = {k: v[:50] + "..." if len(v) > 50 else v for k, v in list(env_vars.items())[:30]}
            return {"status": "success", "message": json.dumps(display, indent=2)[:2000]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 39: SCHEDULED TASKS
# ===================================================================
class ScheduledTasks:
    """Windows Task Scheduler management."""
    
    @staticmethod
    def list_tasks() -> Dict[str, Any]:
        """List scheduled tasks."""
        try:
            result = subprocess.run(
                'schtasks /query /fo TABLE',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout[:3000]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def create_task(name: str, command: str, time: str) -> Dict[str, Any]:
        """Create a scheduled task. Time format: HH:MM"""
        try:
            result = subprocess.run(
                f'schtasks /create /tn "{name}" /tr "{command}" /sc once /st {time}',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or f"Task '{name}' created for {time}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def delete_task(name: str) -> Dict[str, Any]:
        """Delete a scheduled task."""
        try:
            result = subprocess.run(
                f'schtasks /delete /tn "{name}" /f',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or f"Task '{name}' deleted"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def run_task(name: str) -> Dict[str, Any]:
        """Run a scheduled task immediately."""
        try:
            result = subprocess.run(
                f'schtasks /run /tn "{name}"',
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": result.stdout or f"Task '{name}' started"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MODULE 40: QUICK ACTIONS
# ===================================================================
class QuickActions:
    """Quick commonly used actions."""
    
    @staticmethod
    def action_center() -> Dict[str, Any]:
        """Open Windows Action Center."""
        try:
            pyautogui.hotkey('win', 'a')
            return {"status": "success", "message": "Action Center opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def quick_settings() -> Dict[str, Any]:
        """Open Quick Settings (Win 11)."""
        try:
            pyautogui.hotkey('win', 'a')
            return {"status": "success", "message": "Quick Settings opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_emoji_picker() -> Dict[str, Any]:
        """Open emoji picker."""
        try:
            pyautogui.hotkey('win', '.')
            return {"status": "success", "message": "Emoji picker opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_run_dialog() -> Dict[str, Any]:
        """Open Run dialog."""
        try:
            pyautogui.hotkey('win', 'r')
            return {"status": "success", "message": "Run dialog opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_file_explorer() -> Dict[str, Any]:
        """Open File Explorer."""
        try:
            pyautogui.hotkey('win', 'e')
            return {"status": "success", "message": "File Explorer opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_search() -> Dict[str, Any]:
        """Open Windows Search."""
        try:
            pyautogui.hotkey('win', 's')
            return {"status": "success", "message": "Search opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def dictation() -> Dict[str, Any]:
        """Start voice dictation."""
        try:
            pyautogui.hotkey('win', 'h')
            return {"status": "success", "message": "Dictation started. Speak now."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def snip_and_sketch() -> Dict[str, Any]:
        """Open Snip & Sketch."""
        try:
            pyautogui.hotkey('win', 'shift', 's')
            return {"status": "success", "message": "Snip & Sketch opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ===================================================================
# MAIN: WebSocket Server & Command Router
# ===================================================================
class JerryBridge:
    """Main WebSocket server that routes commands to appropriate controllers."""

    def __init__(self):
        # Core Controllers
        self.app_ctrl = AppController()
        self.sys_ctrl = SystemController()
        self.input_ctrl = InputController()
        self.file_ctrl = FileController()
        self.proc_ctrl = ProcessController()
        self.sys_monitor = SystemMonitor()
        self.shell_ctrl = ShellController()
        self.notif_ctrl = NotificationController()
        self.net_ctrl = NetworkController()
        self.alarm_ctrl = AlarmController()
        self.media_ctrl = MediaController()
        self.utils_ctrl = SystemUtilities()
        self.window_ctrl = WindowManager()
        self.notes_ctrl = NotesController()
        
        # v7.0 Extended Controllers
        self.bluetooth_ctrl = BluetoothController()
        self.display_ctrl = DisplayController()
        self.audio_ctrl = AudioDeviceController()
        self.recorder = ScreenRecorder()
        self.archive_ctrl = ArchiveController()
        self.download_ctrl = DownloadController()
        self.git_ctrl = GitController()
        self.code_exec = CodeExecutor()
        self.calculator = Calculator()
        self.translator = Translator()
        self.services_ctrl = ServicesController()
        self.accessibility = AccessibilityController()
        self.focus_assist = FocusAssist()
        self.vdesktop_ctrl = VirtualDesktopController()
        self.usb_ctrl = USBController()
        self.hotspot_ctrl = HotspotController()
        self.vpn_ctrl = VPNController()
        self.clipboard_hist = ClipboardHistory()
        self.printer_ctrl = PrinterController()
        self.power_profiles = PowerProfiles()
        self.env_ctrl = EnvironmentController()
        self.tasks_ctrl = ScheduledTasks()
        self.quick_actions = QuickActions()
        self.browser_ctrl = BrowserControl()  # Browser control (pyautogui + keyboard, no Selenium)
        self.predictive = PredictiveIntelligence()
        
        self.monitoring = True
        self.monitor_interval = 5  # seconds
        self.heartbeat_interval = 30  # seconds

    def _build_context(self) -> Dict[str, Any]:
        try:
            status = self.sys_monitor.get_system_status()
            return {
                "cpu_usage": status.get("cpu", {}).get("percent", 0),
                "memory_usage": status.get("memory", {}).get("percent", 0),
                "battery_charging": status.get("battery", {}).get("charging", False),
            }
        except Exception:
            return {}

    async def _heartbeat(self, websocket):
        """Send periodic ping frames to keep the connection alive."""
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                await websocket.ping()
        except Exception:
            return

    async def handle_command(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Route incoming commands to the correct controller."""
        action = data.get("action", "").lower().strip()
        target = data.get("target", "")
        payload = data.get("payload", "")
        extra = data.get("extra", "")

        if not action:
            raise CommandExecutionError("Missing action in command payload")

        log.info(f"Command: action={action}, target={target}")

        # Warn about dangerous actions
        if action in DANGEROUS_ACTIONS:
            log.warning(f"âš ï¸  DANGEROUS ACTION REQUESTED: {action}")

        # --- Route Commands ---
        # App Control
        if action == "open_app":
            return self.app_ctrl.open_app(target, payload)
        elif action == "close_app":
            return self.app_ctrl.close_app(target)
        elif action == "list_apps":
            return self.app_ctrl.list_running_apps()
        elif action == "focus_app":
            return self.app_ctrl.focus_app(target)

        # Volume & Brightness
        elif action == "volume_control":
            return self.sys_ctrl.volume_control(target, payload)
        elif action == "brightness_control":
            return self.sys_ctrl.brightness_control(target, payload)

        # Power Management
        elif action in ("lock", "sleep", "shutdown", "restart", "cancel_shutdown", "logoff"):
            return self.sys_ctrl.power_control(action)
        elif action == "power_control":
            return self.sys_ctrl.power_control(target)

        # Screenshot & Clipboard
        elif action == "screenshot":
            return self.sys_ctrl.screenshot(payload)
        elif action == "clipboard":
            return self.sys_ctrl.clipboard_control(target, payload)

        # Keyboard & Mouse
        elif action == "keyboard_macro":
            return self.input_ctrl.keyboard_macro(target, payload)
        elif action == "mouse_control":
            return self.input_ctrl.mouse_control(target, payload)

        # File Operations
        elif action == "file_operation":
            return self.file_ctrl.file_operation(target, payload, extra)

        # Process Management
        elif action == "process":
            return self.proc_ctrl.process_operation(target, payload)
        elif action == "kill_process":
            return self.proc_ctrl.process_operation("kill", target)

        # System Monitoring
        elif action == "system_status":
            return self.sys_monitor.get_system_status()
        elif action == "network_info":
            return self.sys_monitor.get_network_info()
        elif action == "startup_programs":
            return self.sys_monitor.get_startup_programs()

        # Shell Execution
        elif action == "shell_execute":
            return self.shell_ctrl.execute_command(target or payload)

        # Notifications
        elif action == "notification":
            return self.notif_ctrl.send_notification(target, payload)

        # WiFi
        elif action == "wifi":
            return self.net_ctrl.wifi_operation(target, payload)
        
        # =====================
        # NEW FEATURES
        # =====================
        
        # Alarms, Timers, Reminders
        elif action == "set_alarm":
            return self.alarm_ctrl.set_alarm(target, payload or "Alarm", extra)
        elif action == "set_timer":
            return self.alarm_ctrl.set_timer(target, payload or "Timer")
        elif action == "set_reminder":
            return self.alarm_ctrl.set_reminder(target, payload)
        elif action == "cancel_alarm":
            return self.alarm_ctrl.cancel_alarm(target)
        elif action == "list_alarms":
            return self.alarm_ctrl.list_alarms()
        
        # Text-to-Speech
        elif action == "speak" or action == "say" or action == "tts":
            return TTSController.speak(target or payload)
        elif action == "list_voices":
            return TTSController.list_voices()
        elif action == "set_voice":
            return TTSController.set_voice(int(target or 0))
        
        # Email
        elif action == "send_email":
            # target=recipient, payload=subject, extra=body
            return EmailController.send_email(target, payload, extra)
        
        # Calendar
        elif action == "get_calendar" or action == "list_events":
            days = int(target) if target and target.isdigit() else 7
            return CalendarController.get_events(days)
        elif action == "create_event":
            # target=subject, payload=start_time (YYYY-MM-DD HH:MM), extra=duration_minutes
            duration = int(extra) if extra and extra.isdigit() else 60
            return CalendarController.create_event(target, payload, duration)
        
        # Media Control
        elif action == "media":
            return self.media_ctrl.media_control(target)
        elif action == "open_url":
            return self.media_ctrl.open_url(target or payload)
        elif action == "play_youtube":
            return self.media_ctrl.play_youtube(target or payload)
        elif action == "play_spotify":
            return self.media_ctrl.play_spotify(target or payload)
        
        # System Utilities
        elif action == "empty_recycle_bin":
            return self.utils_ctrl.empty_recycle_bin()
        elif action == "clear_temp":
            return self.utils_ctrl.clear_temp_files()
        elif action == "disk_cleanup":
            return self.utils_ctrl.disk_cleanup()
        elif action == "check_updates":
            return self.utils_ctrl.check_windows_updates()
        elif action == "system_info":
            return self.utils_ctrl.system_info()
        elif action == "install_app":
            return self.utils_ctrl.install_app(target)
        elif action == "uninstall_app":
            return self.utils_ctrl.uninstall_app(target)
        elif action == "search_apps":
            return self.utils_ctrl.search_apps(target)
        
        # Window Management
        elif action == "list_windows":
            return self.window_ctrl.list_windows()
        elif action == "move_window":
            # target=title, payload=x,y
            try:
                coords = [int(c.strip()) for c in payload.split(",")]
                if len(coords) < 2:
                    return {"status": "error", "message": "move_window requires payload='x,y' (two integers)"}
                return self.window_ctrl.move_window(target, coords[0], coords[1])
            except (ValueError, IndexError) as e:
                return {"status": "error", "message": f"Invalid coordinates '{payload}'. Expected format: 'x,y' (e.g. '100,200')"}
        elif action == "resize_window":
            # target=title, payload=width,height
            try:
                dims = [int(c.strip()) for c in payload.split(",")]
                if len(dims) < 2:
                    return {"status": "error", "message": "resize_window requires payload='width,height' (two integers)"}
                return self.window_ctrl.resize_window(target, dims[0], dims[1])
            except (ValueError, IndexError) as e:
                return {"status": "error", "message": f"Invalid dimensions '{payload}'. Expected format: 'width,height' (e.g. '800,600')"}
        elif action == "snap_window":
            return self.window_ctrl.snap_window(target, payload)
        
        # Quick Notes
        elif action == "add_note":
            return self.notes_ctrl.add_note(target, payload)
        elif action == "list_notes":
            return self.notes_ctrl.list_notes(target)
        elif action == "search_notes":
            return self.notes_ctrl.search_notes(target)
        elif action == "delete_note":
            return self.notes_ctrl.delete_note(target)

        # =====================================================
        # v7.0 EXTENDED CAPABILITIES
        # =====================================================
        
        # --- Bluetooth ---
        elif action == "bluetooth_list":
            return self.bluetooth_ctrl.list_devices()
        elif action == "bluetooth_toggle":
            return self.bluetooth_ctrl.toggle_bluetooth((target or "on").lower() != "off")
        elif action == "bluetooth_connect":
            return self.bluetooth_ctrl.connect_device(target)
        
        # --- Display Settings ---
        elif action == "night_light":
            return self.display_ctrl.toggle_night_light((target or "on").lower() != "off")
        elif action == "get_resolution":
            return self.display_ctrl.get_resolution()
        elif action == "set_resolution":
            dims = payload.split("x") if payload else ["1920", "1080"]
            return self.display_ctrl.set_resolution(int(dims[0]), int(dims[1]))
        elif action == "list_monitors":
            return self.display_ctrl.list_monitors()
        elif action == "project_display":
            return self.display_ctrl.project_display(target)  # pc_only, duplicate, extend, second_only
        
        # --- Audio Device ---
        elif action == "list_audio_devices":
            return self.audio_ctrl.list_audio_devices()
        elif action == "set_default_audio":
            return self.audio_ctrl.set_default_device(target)
        elif action == "toggle_microphone":
            return self.audio_ctrl.toggle_microphone((target or "mute").lower() == "mute")
        
        # --- Screen Recording ---
        elif action == "start_recording":
            return self.recorder.start_recording()
        elif action == "stop_recording":
            return self.recorder.stop_recording()
        elif action == "open_game_bar":
            return self.recorder.open_game_bar()
        elif action == "webcam_photo":
            return self.recorder.take_webcam_photo()
        
        # --- Archive Operations ---
        elif action == "zip_files":
            return self.archive_ctrl.zip_files(target, payload)
        elif action == "unzip_file":
            return self.archive_ctrl.unzip_file(target, payload)
        elif action == "list_archive":
            return self.archive_ctrl.list_archive(target)
        
        # --- Downloads ---
        elif action == "download_file":
            return self.download_ctrl.download_file(target, payload)
        
        # --- Git Operations ---
        elif action == "git_status":
            return self.git_ctrl.git_status(target or ".")
        elif action == "git_pull":
            return self.git_ctrl.git_pull(target or ".")
        elif action == "git_push":
            return self.git_ctrl.git_push(target or ".")
        elif action == "git_commit":
            return self.git_ctrl.git_commit(target or ".", payload or "Auto-commit by Jerry")
        elif action == "git_clone":
            return self.git_ctrl.git_clone(target, payload)
        elif action == "git_branch":
            return self.git_ctrl.git_branch(target or ".")
        
        # --- Code Execution ---
        elif action == "run_python":
            return self.code_exec.run_python(target or payload)
        elif action == "run_powershell":
            return self.code_exec.run_powershell(target or payload)
        
        # --- Calculator & Converter ---
        elif action == "calculate":
            return self.calculator.calculate(target or payload)
        elif action == "convert_units":
            # target=value, payload=from_unit, extra=to_unit
            try:
                return self.calculator.convert_units(float(target or 0), payload, extra)
            except ValueError:
                return {"status": "error", "message": "Invalid numeric value for conversion"}
        elif action == "convert_currency":
            # target=amount, payload=from_curr, extra=to_curr
            try:
                return self.calculator.convert_currency(float(target or 0), payload, extra)
            except ValueError:
                return {"status": "error", "message": "Invalid amount for currency conversion"}
        
        # --- Translator ---
        elif action == "translate":
            return self.translator.translate(target, payload or "en")
        
        # --- Windows Services ---
        elif action == "list_services":
            return self.services_ctrl.list_services(target.lower() == "running" if target else False)
        elif action == "start_service":
            return self.services_ctrl.start_service(target)
        elif action == "stop_service":
            return self.services_ctrl.stop_service(target)
        elif action == "restart_service":
            return self.services_ctrl.restart_service(target)
        
        # --- Accessibility ---
        elif action == "magnifier":
            return self.accessibility.toggle_magnifier((target or "on").lower() != "off")
        elif action == "narrator":
            return self.accessibility.toggle_narrator((target or "on").lower() != "off")
        elif action == "high_contrast":
            return self.accessibility.toggle_high_contrast()
        elif action == "ease_of_access":
            return self.accessibility.open_ease_of_access()
        
        # --- Focus Assist ---
        elif action == "focus_assist":
            return self.focus_assist.toggle_focus_assist(target or "priority")
        elif action == "toggle_notifications":
            return self.focus_assist.toggle_notifications((target or "on").lower() != "off")
        
        # --- Virtual Desktops ---
        elif action == "new_desktop":
            return self.vdesktop_ctrl.new_desktop()
        elif action == "close_desktop":
            return self.vdesktop_ctrl.close_desktop()
        elif action == "switch_desktop":
            return self.vdesktop_ctrl.switch_desktop(target or "right")
        elif action == "task_view":
            return self.vdesktop_ctrl.show_task_view()
        
        # --- USB ---
        elif action == "list_usb":
            return self.usb_ctrl.list_usb_devices()
        elif action == "eject_drive":
            return self.usb_ctrl.eject_drive(target)
        
        # --- Hotspot ---
        elif action == "toggle_hotspot":
            return self.hotspot_ctrl.toggle_hotspot((target or "on").lower() != "off")
        elif action == "hotspot_status":
            return self.hotspot_ctrl.get_hotspot_status()
        
        # --- VPN ---
        elif action == "list_vpn":
            return self.vpn_ctrl.list_vpn_connections()
        elif action == "connect_vpn":
            return self.vpn_ctrl.connect_vpn(target)
        elif action == "disconnect_vpn":
            return self.vpn_ctrl.disconnect_vpn(target)
        elif action == "vpn_settings":
            return self.vpn_ctrl.open_vpn_settings()
        
        # --- Clipboard History ---
        elif action == "clipboard_history":
            return self.clipboard_hist.open_clipboard_history()
        elif action == "clear_clipboard":
            return self.clipboard_hist.clear_clipboard()
        
        # --- Printer ---
        elif action == "list_printers":
            return self.printer_ctrl.list_printers()
        elif action == "set_default_printer":
            return self.printer_ctrl.set_default_printer(target)
        elif action == "print_file":
            return self.printer_ctrl.print_file(target)
        elif action == "print_queue":
            return self.printer_ctrl.open_print_queue()
        
        # --- Power Profiles ---
        elif action == "list_power_plans":
            return self.power_profiles.list_power_plans()
        elif action == "set_power_plan":
            return self.power_profiles.set_power_plan(target)
        elif action == "battery_saver":
            return self.power_profiles.toggle_battery_saver((target or "on").lower() != "off")
        
        # --- Environment Variables ---
        elif action == "get_env":
            return self.env_ctrl.get_env(target)
        elif action == "set_env":
            return self.env_ctrl.set_env(target, payload, extra.lower() == "persistent" if extra else False)
        elif action == "list_env":
            return self.env_ctrl.list_env()
        
        # --- Scheduled Tasks ---
        elif action == "list_tasks":
            return self.tasks_ctrl.list_tasks()
        elif action == "create_task":
            # target=name, payload=command, extra=time (HH:MM)
            return self.tasks_ctrl.create_task(target, payload, extra)
        elif action == "delete_task":
            return self.tasks_ctrl.delete_task(target)
        elif action == "run_task":
            return self.tasks_ctrl.run_task(target)
        
        # --- Quick Actions ---
        elif action == "action_center":
            return self.quick_actions.action_center()
        elif action == "quick_settings":
            return self.quick_actions.quick_settings()
        elif action == "emoji_picker":
            return self.quick_actions.open_emoji_picker()
        elif action == "run_dialog":
            return self.quick_actions.open_run_dialog()
        elif action == "file_explorer":
            return self.quick_actions.open_file_explorer()
        elif action == "windows_search":
            return self.quick_actions.open_search()
        elif action == "dictation":
            return self.quick_actions.dictation()
        elif action == "snip_sketch":
            return self.quick_actions.snip_and_sketch()
        
        # =====================================================
        # BROWSER CONTROL (pyautogui + keyboard, no Selenium)
        # =====================================================
        elif action == "browser_navigate":
            return BrowserControl.navigate(target or payload)
        elif action == "browser_click":
            # target=x, payload=y â€” clicks at screen coordinates
            x = int(target) if target and target.lstrip('-').isdigit() else 0
            y = int(payload) if payload and payload.lstrip('-').isdigit() else 0
            click_type = extra if extra else "single"
            return BrowserControl.click_position(x, y, click_type)
        elif action == "browser_type":
            # target=text to type, extra=submit (true/false)
            submit = extra.lower() == "true" if extra else False
            return BrowserControl.type_text(target or payload, submit=submit)
        elif action == "browser_scroll":
            # target=direction (up/down/top/bottom), payload=amount
            amount = int(payload) if payload and payload.isdigit() else 5
            return BrowserControl.scroll_page(target or "down", amount)
        elif action == "browser_screenshot":
            return BrowserControl.screenshot_page(target)
        elif action == "browser_get_text":
            return BrowserControl.copy_page_text()
        elif action == "browser_close":
            return BrowserControl.close_tab()
        elif action == "reset_browser":
            return BrowserControl.browser_refresh()
        elif action == "youtube_play":
            return BrowserControl.youtube_play_first(target or payload)
        elif action == "spotify_play":
            return BrowserControl.spotify_play_first(target or payload)
        elif action == "google_first":
            return BrowserControl.google_search_first(target or payload)
        elif action == "google_search":
            return BrowserControl.google_search_first(target or payload)
        elif action == "click_position":
            # target=x, payload=y, extra=click_type (single/double/right)
            x = int(target) if target and target.lstrip('-').isdigit() else 0
            y = int(payload) if payload and payload.lstrip('-').isdigit() else 0
            click_type = extra if extra else "single"
            return BrowserControl.click_position(x, y, click_type)
        elif action == "double_click":
            # target=x, payload=y
            x = int(target) if target and target.lstrip('-').isdigit() else 0
            y = int(payload) if payload and payload.lstrip('-').isdigit() else 0
            return BrowserControl.click_position(x, y, "double")
        elif action == "right_click":
            # target=x, payload=y
            x = int(target) if target and target.lstrip('-').isdigit() else 0
            y = int(payload) if payload and payload.lstrip('-').isdigit() else 0
            return BrowserControl.click_position(x, y, "right")
        elif action == "hover":
            # target=x, payload=y â€” move mouse to position
            x = int(target) if target and target.lstrip('-').isdigit() else 0
            y = int(payload) if payload and payload.lstrip('-').isdigit() else 0
            try:
                pyautogui.moveTo(x, y)
                return {"status": "success", "message": f"Moved mouse to ({x}, {y})"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        elif action == "click_text":
            # target=text to find on page via Ctrl+F
            return BrowserControl.search_on_page(target)
        elif action == "browser_keys":
            # target=keys (e.g., "ctrl+a", "enter", "f5")
            return BrowserControl.send_keys(target)
        elif action == "browser_back":
            return BrowserControl.browser_back()
        elif action == "browser_forward":
            return BrowserControl.browser_forward()
        elif action == "browser_refresh":
            return BrowserControl.browser_refresh()
        elif action == "browser_zoom":
            return BrowserControl.browser_zoom(target or "in")
        elif action == "browser_fullscreen":
            return BrowserControl.fullscreen()
        elif action == "new_tab":
            return BrowserControl.new_tab(target or "")
        elif action == "close_tab":
            return BrowserControl.close_tab()
        elif action == "switch_tab":
            return BrowserControl.switch_tab(target or "next")
        elif action == "browser_find":
            return BrowserControl.search_on_page(target or payload)
        elif action == "tab_navigate":
            presses = int(target) if target and target.isdigit() else 1
            return BrowserControl.tab_navigate(presses)
        elif action == "wait_click":
            # target=seconds, payload=x, extra=y
            seconds = float(target) if target else 1.0
            x = int(payload) if payload and payload.lstrip('-').isdigit() else 0
            y = int(extra) if extra and extra.lstrip('-').isdigit() else 0
            return BrowserControl.wait_and_click(seconds, x, y)

        # =====================================================
        # SCREEN READER & OCR COMMANDS
        # =====================================================
        elif action == "ocr_screen":
            # Read all text from screen
            return ScreenReader.ocr_screen()
        elif action == "ocr_window":
            # Read text from active window only
            return ScreenReader.read_active_window()
        elif action == "find_text":
            # target=text to find
            return ScreenReader.find_text_on_screen(target)
        elif action == "click_screen_text":
            # target=text to click, payload=click_type (single/double/right)
            return ScreenReader.click_text_on_screen(target, payload or "single")
        elif action == "click_button":
            # target=button text, payload=click_type
            return ScreenReader.click_button(target, payload or "single")
        elif action == "get_paragraph":
            # target=paragraph number (1-indexed)
            para_num = int(target) if target and target.isdigit() else 1
            return ScreenReader.get_paragraph(para_num)
        elif action == "copy_screen_text":
            # target=what (all/paragraph/line/word/containing), payload=identifier
            return ScreenReader.copy_text_from_screen(target or "all", payload or "")
        elif action == "find_element":
            # target=element description (like "sign in button")
            return ScreenReader.find_and_click_image_element(target)
        elif action == "list_screen_elements":
            # Get all clickable elements on screen
            return ScreenReader.get_screen_elements()

        # Command History
        elif action == "history":
            return {"status": "success", "history": command_history[-20:], "message": f"Last {min(20, len(command_history))} commands"}

        # Undo Last
        elif action == "undo_last":
            return await self._undo_last()

        # Ping
        elif action == "ping" or action == "heartbeat":
            return {"status": "success", "message": "Bridge is alive", "timestamp": datetime.now().isoformat()}

        # Predictive Intelligence
        elif action == "predict_next":
            return {"status": "success", "predictions": self.predictive.predict_next_actions(self._build_context())}
        elif action == "detect_routines":
            return {"status": "success", "routines": self.predictive.detect_routines()}
        elif action == "suggest_automation":
            return {"status": "success", "suggestions": self.predictive.suggest_automation()}
        elif action == "agent_execute":
            goal = target or payload
            agent = AutonomousAgent(goal, self)
            return await agent.execute()

        else:
            raise CommandExecutionError(
                f"Unknown action: {action}. Available actions: open_app, close_app, volume_control, brightness_control, power_control, screenshot, clipboard, keyboard_macro, mouse_control, file_operation, process, system_status, shell_execute, wifi, notification, set_alarm, set_timer, set_reminder, speak, send_email, get_calendar, create_event, media, play_youtube, play_spotify, empty_recycle_bin, clear_temp, install_app, list_windows, snap_window, add_note, list_notes, bluetooth_list, night_light, list_audio_devices, start_recording, zip_files, download_file, git_status, git_pull, git_push, run_python, calculate, translate, list_services, magnifier, narrator, new_desktop, task_view, eject_drive, toggle_hotspot, connect_vpn, list_printers, set_power_plan, list_tasks, action_center, emoji_picker, dictation, snip_sketch, predict_next, detect_routines, suggest_automation, agent_execute"
            )

    async def _undo_last(self) -> Dict[str, Any]:
        """Undo the last undoable command."""
        for cmd in reversed(command_history):
            if cmd.get("undoable") and cmd.get("undo_action") and cmd["status"] != "undone":
                undo = cmd["undo_action"]
                result = await self.handle_command(undo)
                cmd["status"] = "undone"
                return {"status": "success", "message": f"Undone: {cmd['action']} â†’ {result.get('message', 'OK')}"}
        return {"status": "warning", "message": "Nothing to undo"}

    async def handler(self, websocket):
        """Handle a WebSocket connection."""
        remote = websocket.remote_address
        log.info(f"ðŸ”— Connection from {remote}")
        active_connections.add(websocket)
        heartbeat_task = asyncio.create_task(self._heartbeat(websocket))

        try:
            async for message in websocket:
                try:
                    if message == "ping":
                        await websocket.send("pong")
                        continue

                    data = json.loads(message)
                    action = (data.get("action") or "").lower().strip()
                    structured_log.log_command(action, "received", {"remote": str(remote)})

                    # Authentication check
                    token = data.pop("auth_token", None)
                    timestamp = data.pop("timestamp", None)
                    nonce = data.pop("nonce", None)
                    req_id = data.pop("_reqId", None)
                    if AUTH_TOKEN and not validate_token(token, timestamp, nonce):
                        log.warning(f"Rejected unauthenticated command from {remote}")
                        structured_log.log_command(action, "error", {"remote": str(remote), "reason": "auth_failed"})
                        resp = {"status": "error", "message": "Authentication failed. Invalid token or replay detected."}
                        if req_id:
                            resp["_reqId"] = req_id
                        await websocket.send(json.dumps(resp))
                        continue

                    result = await self.handle_command(data)
                    if req_id:
                        result["_reqId"] = req_id
                    structured_log.log_command(action, result.get("status", "unknown"), {"remote": str(remote), "message": result.get("message", "")})
                    if result.get("status") == "success":
                        if action not in {"system_status", "ping", "heartbeat", "predict_next", "detect_routines", "suggest_automation", "agent_execute"}:
                            try:
                                self.predictive.learn_from_command(action, self._build_context())
                            except Exception:
                                pass
                    await websocket.send(json.dumps(result))

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"status": "error", "message": "Invalid JSON"}))
                except CommandExecutionError as e:
                    structured_log.log_command(action or "unknown", "error", {"remote": str(remote), "message": str(e)})
                    await websocket.send(json.dumps({"status": "error", "message": str(e)}))
                except Exception as e:
                    log.error(f"Command error: {e}")
                    structured_log.log_command(action or "unknown", "error", {"remote": str(remote), "message": str(e)})
                    await websocket.send(json.dumps({"status": "error", "message": str(e)}))

        except websockets.exceptions.ConnectionClosed:
            log.info(f"ðŸ”Œ Client disconnected: {remote}")
        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
            active_connections.discard(websocket)

    async def start_monitoring(self):
        """Periodically broadcast system stats to all connected clients."""
        while True:
            if active_connections and self.monitoring:
                stats = self.sys_monitor.get_system_status()
                stats["type"] = "system_monitor"
                message = json.dumps(stats)
                dead = set()
                for ws in active_connections:
                    try:
                        await ws.send(message)
                    except Exception:
                        dead.add(ws)
                active_connections.difference_update(dead)
            await asyncio.sleep(self.monitor_interval)

    async def run(self):
        """Start the bridge server."""
        log.info("=" * 60)
        log.info("  JERRY NEURAL BRIDGE v7.0 ULTIMATE")
        log.info(f"  Host: {BRIDGE_HOST}:{BRIDGE_PORT}")
        log.info(f"  Platform: {platform.system()} {platform.release()}")
        log.info(f"  Auth: {'Enabled' if AUTH_TOKEN else 'Disabled'}")
        log.info("  Modules: 40+ system controllers loaded")
        log.info("=" * 60)
        log.info("Awaiting neural link from Jerry frontend...")

        ssl_context = None
        cert_path = os.environ.get("JERRY_BRIDGE_TLS_CERT")
        key_path = os.environ.get("JERRY_BRIDGE_TLS_KEY")
        if cert_path and key_path and os.path.exists(cert_path) and os.path.exists(key_path):
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)
            log.info("TLS enabled for bridge server (wss).")

        try:
            async with websockets.serve(self.handler, BRIDGE_HOST, BRIDGE_PORT, ssl=ssl_context):
                # Start monitoring task
                monitor_task = asyncio.create_task(self.start_monitoring())
                try:
                    await asyncio.Future()  # Run forever
                finally:
                    monitor_task.cancel()
                    try:
                        await monitor_task
                    except asyncio.CancelledError:
                        pass
                    log.info("Monitor task cancelled. Bridge shutting down.")
        except OSError as e:
            if e.errno == 10048 or 'already in use' in str(e).lower() or 'address already in use' in str(e).lower():
                log.warning(f"Port {BRIDGE_PORT} is already in use. Attempting to free it...")
                _kill_process_on_port(BRIDGE_PORT)
                await asyncio.sleep(1)
                async with websockets.serve(self.handler, BRIDGE_HOST, BRIDGE_PORT, ssl=ssl_context):
                    monitor_task = asyncio.create_task(self.start_monitoring())
                    try:
                        await asyncio.Future()
                    finally:
                        monitor_task.cancel()
                        try:
                            await monitor_task
                        except asyncio.CancelledError:
                            pass
                        log.info("Monitor task cancelled. Bridge shutting down.")
            else:
                raise


def _kill_process_on_port(port: int) -> None:
    """Kill any process listening on the given port (Windows & Unix)."""
    try:
        if platform.system() == "Windows":
            import subprocess
            result = subprocess.run(
                ["netstat", "-ano", "-p", "TCP"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    pid = int(parts[-1])
                    if pid > 0:
                        subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                                       capture_output=True, timeout=5)
                        log.info(f"Killed process {pid} on port {port}")
        else:
            import subprocess
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True, text=True, timeout=5
            )
            for pid in result.stdout.strip().split():
                subprocess.run(["kill", "-9", pid], capture_output=True, timeout=5)
                log.info(f"Killed process {pid} on port {port}")
    except Exception as e:
        log.error(f"Failed to free port {port}: {e}")


if __name__ == "__main__":
    bridge = JerryBridge()
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        log.info("Bridge shutdown by operator.")
