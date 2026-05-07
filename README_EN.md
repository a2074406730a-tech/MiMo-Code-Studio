# MiMo Code Studio

> AI programming assistant desktop app — powered by MiMo LLM, with code editing, file operations, command execution, and voice synthesis

English | [中文](./README.md)

## Features

- **AI Chat** — Streaming output with real-time response display
- **Tool Calling** — Automatic file read/write, code editing, directory browsing, terminal commands, content search
- **Voice Synthesis** — Edge TTS with 5 Chinese voices, adjustable speed and volume
- **Multi-Conversation** — Create, switch, rename, delete conversations with persistent history
- **Dark/Light Theme** — One-click toggle with auto-save preferences
- **Markdown Rendering** — Strips formatting for clean text display
- **Emoji Filtering** — Auto-removes emoji and special Unicode characters during speech

## Preview

```
+----------------------------------------------------------+
|  MiMo Code Studio                              [Light]   |
+----------+-----------------------------------------------+
| [New Chat]|  User: Write a sorting algorithm for me       |
|          |                                               |
| Chat 1   |  MiMo: Sure, here's a quick sort impl...      |
| Chat 2   |       [Speak] [Copy]                          |
| Chat 3   |                                               |
|          |  [Tool] read_file → main.py                   |
|          |       Completed                                |
| [Settings]|  +------------------------------------------+|
|          |  | MiMo is thinking...                       ||
|          |  +------------------------------------------+|
+----------+-----------------------------------------------+
|  Xiaoxiao | Speed [----o----] | Vol [------o--] | Auto   |
|  [Send]                                                      |
+----------------------------------------------------------+
|  Ready                       | Token: In 1234 | Out 567  |
+----------------------------------------------------------+
```

## Quick Start

### Requirements

| Dependency | Minimum Version | Notes |
|------------|-----------------|-------|
| Windows | 10/11 | Windows only |
| Python | 3.10+ | 3.12 recommended |
| PowerShell | 5.1+ | For installation and launching |
| pip | Bundled with Python | Package manager |
| Git | 2.30+ | Clone the repo (optional) |

### Step 1: Clone the Repository

```powershell
cd mimo-speaker
```

### Step 2: Check Python Environment

```powershell
# Check Python version (3.10+ required)
python --version

# If Python is not installed, install from Microsoft Store
winget install Python.Python.3.12

# Or download from: https://www.python.org/downloads/
# IMPORTANT: Check "Add Python to PATH" during installation
```

### Step 3: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

After activation, your terminal prompt will show a `(venv)` prefix.

### Step 4: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install customtkinter requests edge-tts pygame chardet pygments
```

**Dependency Details:**

| Package | Version | Purpose |
|---------|---------|---------|
| `customtkinter` | 5.2+ | Modern Tkinter GUI framework |
| `requests` | 2.28+ | HTTP client for MiMo API |
| `edge-tts` | 6.1+ | Microsoft Edge TTS engine |
| `pygame` | 2.5+ | Audio playback engine |
| `chardet` | 5.0+ | File encoding auto-detection |
| `pygments` | 2.14+ | Code syntax highlighting |

Or install everything at once with requirements.txt:

```powershell
pip install -r requirements.txt
```

### Step 5: Configure API

```powershell
# Copy the example config
Copy-Item data\settings.example.json data\settings.json
```

Edit `data/settings.json` with your API credentials:

```json
{
  "api_url": "https://your-api-endpoint/v1/messages",
  "api_key": "your-api-key-here",
  "model": "mimo-v2.5-pro",
  "max_tokens": 4096
}
```

### Step 6: Launch

**Option 1: Double-click (Recommended)**

Double-click `start.bat` in the project root.

**Option 2: PowerShell**

```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Launch the app
python main.py
```

**Option 3: Without activating venv**

```powershell
.\venv\Scripts\python.exe main.py
```

### Run Tests

```powershell
# After activating venv
python test.py
```

Covers 10 modules, 56 test cases: config management, tools, message sending, tool call parsing, TTS synthesis, audio player, text processing, multi-conversation, tool call integration, stability tests.

## Project Structure

```
mimo-speaker/
├── main.py                    # Entry point
├── config.py                  # Config management + conversation persistence
├── api_client.py              # MiMo API client (SSE streaming + tool calling)
├── tools.py                   # Tool definitions and implementations
├── tts_engine.py              # Edge TTS voice synthesis engine
├── audio_player.py            # Pygame audio player
├── start.bat                  # Windows launcher script
├── test.py                    # Automated test suite (56 cases)
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
├── README.md                  # Chinese documentation
├── README_EN.md               # English documentation
├── data/
│   ├── settings.example.json  # Config template (safe to commit)
│   ├── settings.json          # User config (git ignored)
│   └── conversations.json     # Chat history (git ignored)
└── ui/
    ├── __init__.py
    ├── app.py                 # Main window
    ├── chat_area.py           # Chat area + message bubbles
    ├── sidebar.py             # Sidebar + conversation list
    ├── input_bar.py           # Input bar + voice controls
    ├── settings_panel.py      # Settings panel
    ├── themes.py              # Dark/light theme colors
    ├── widgets.py             # Custom widgets (ToolCallCard, etc.)
    └── markdown_renderer.py   # Markdown renderer
```

## Tool Calling

The AI assistant can automatically invoke these tools during conversation:

| Tool | Description | Example |
|------|-------------|---------|
| `read_file` | Read file with auto encoding detection | "Show me the content of main.py" |
| `write_file` | Write file, auto-create directories | "Create a hello.py file" |
| `edit_file` | Precise text replacement | "Change line 10 from print to logging" |
| `list_directory` | List directory structure | "What files are in this project?" |
| `run_command` | Execute terminal commands (60s timeout) | "Run python --version" |
| `search_files` | Search file content | "Find all files using requests" |

## Tech Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| GUI Framework | customtkinter | Modern UI based on Tkinter |
| AI Interface | Anthropic Messages API | SSE streaming protocol |
| Voice Synthesis | Edge TTS | Microsoft free TTS service |
| Audio Playback | Pygame | Cross-platform audio engine |
| Encoding Detection | chardet | Auto-detect file encoding |
| HTTP Client | requests | API communication |
| Python | 3.10+ | Minimum version required |

## Troubleshooting

### PowerShell Execution Policy Error

```powershell
# Error: Cannot load file because running scripts is disabled on this system
# Fix:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### pip install Timeout

```powershell
# Use a mirror source (for users in China)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### edge-tts Installation Fails

```powershell
# Make sure Python version >= 3.10
python --version

# Install edge-tts separately
pip install edge-tts --no-cache-dir
```

### pygame Initialization Fails

```powershell
# Reinstall pygame
pip uninstall pygame
pip install pygame --no-cache-dir
```

### App Shows Blank Screen on Launch

```powershell
# Check customtkinter version
pip show customtkinter

# Upgrade to latest
pip install customtkinter --upgrade
```

## Complete Dependency Installation

### One-Click PowerShell Install (Recommended)

```powershell
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Install all dependencies
pip install customtkinter>=5.2.0 requests>=2.28.0 edge-tts>=6.1.0 pygame>=2.5.0 chardet>=5.0.0 pygments>=2.14.0

# 4. Or use requirements.txt
pip install -r requirements.txt
```

### Mirror Acceleration (China)

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Dependency Version List

| Package | Minimum Version | Purpose |
|---------|-----------------|---------|
| customtkinter | 5.2.0 | GUI framework |
| requests | 2.28.0 | HTTP client |
| edge-tts | 6.1.0 | Voice synthesis |
| pygame | 2.5.0 | Audio playback |
| chardet | 5.0.0 | Encoding detection |
| pygments | 2.14.0 | Code highlighting |
