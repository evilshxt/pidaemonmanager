# 🧠 ProcSight
> **Cross-platform Process & Network Insight CLI**

ProcSight is a **powerful, safe, and developer-friendly command-line tool** for inspecting and managing system processes, services, and network connections across Windows, Linux, and macOS.

Whether you're a **developer debugging port conflicts**, a **sysadmin monitoring services**, or a **security enthusiast auditing your system**, ProcSight gives you visibility and control — all in a single, pretty, cross-platform Python CLI.

---

## ✨ Key Features

### ⚙️ Core Process Management
- 🔍 **Search for processes** by name or command fragment.
- 📊 **Inspect process details** — PID, user, CPU%, memory, I/O, threads, and child processes.
- ⚠️ **Terminate or restart processes safely**, with admin gating and user confirmation.
- 🕵️ **Monitor process behavior live** (`procsight watch <process>`): see CPU, memory, and I/O updates in real-time.
- 🧾 **Export process lists** to CSV or JSON for external analysis.
- 🧱 **Cross-platform service management:**
  - Linux: systemd (`systemctl`)
  - Windows: native Services (`sc`, `pywin32`)
  - macOS: launchd (`launchctl`)

---

### 🌐 Network Visibility
- 🔌 **List listening ports** — find what's running on which port.
- 🌍 **Inspect active network connections** (local + remote addresses, status, protocol).
- 🧭 **Map port → process** instantly (`procsight map --port <number>`).
- 🧩 **Identify port conflicts** or find **free ports** for new services.
- 📈 **Show top network consumers** or per-PID connection stats.
- 🧠 **Security mode:** highlight unknown or high-privilege listeners (<1024).

> Uses [`psutil`](https://github.com/giampaolo/psutil) for cross-platform network and process inspection.

---

### 🧠 Advanced System Insight
- 📊 **Top mode:** sort by CPU, memory, or network usage (`procsight top --net`).
- 🔄 **Restart stuck daemons** safely with confirmation.
- 📋 **System snapshot reports** (processes + ports + performance) — exportable as JSON/CSV.
- 📜 **Audit mode:** flag suspicious processes (unsigned binaries, weird ports, zombie processes).
- ⏱️ **Time-series logging:** record CPU/memory stats to a log for later analysis.
- 🧰 **Developer utilities:** find local dev servers, free ports, or zombie processes.

---

### 🔐 Security & Admin Controls

Some actions require elevated privileges:

| OS | How to run with admin privileges |
|----|----------------------------------|
| 🪟 **Windows** | Run your terminal as **Administrator** (Right-click → *Run as administrator*) |
| 🐧 **Linux / Kali / Ubuntu** | Prefix with `sudo`, e.g. `sudo procsight ports` |
| 🍎 **macOS** | Prefix with `sudo`, e.g. `sudo procsight ports` (uses `launchctl` for services) |

ProcSight automatically detects privilege level and will warn you if certain actions require elevation.

---

### 🎨 Polished CLI Experience
ProcSight is built for readability and comfort:
- 🎨 **Color output** with [`colorama`](https://pypi.org/project/colorama/) (green = success, yellow = warning, red = danger).
- 📋 **Tables** powered by [`PrettyTable`](https://pypi.org/project/PrettyTable/) for clean formatted listings.
- ⌛ **Progress indicators** for scans and watchers.
- 🧾 **Audit & action logging**:
  - Logs all admin actions (`terminate`, `restart`, `enable/disable`) to `logs/procsight.log`
  - Includes timestamps, usernames, and outcomes.

---

### 🧩 Extensible Plugin System
ProcSight can be extended via simple plugins:
- Drop Python files into the `plugins/` directory.
- Each plugin exposes a `register()` function to add new commands or integrations.
- Example ideas: Docker monitoring, GPU stats, remote SSH control, system cleanup.

Future versions may support plugin installation via `pip install procsight-plugin-xyz`.

---

### 🧱 Clean Architecture & Directory Structure

```
procsight/
├── procsight.py           # Main entry point script
├── core/                  # Core functionalities as plugins
│   ├── core.py            # Process management
│   ├── network.py         # Ports & connections
│   ├── monitor.py         # Live stats (watch mode)
│   ├── privilege_check.py # Detects admin/root privileges
│   └── utils.py           # Color, formatting, and logging helpers
├── services/              # OS-specific service backends
│   ├── systemd_backend.py
│   ├── windows_backend.py
│   └── launchd_backend.py
├── plugins/               # Additional extensible custom commands
├── tests/
│   ├── test_core.py
│   ├── test_network.py
│   └── test_privileges.py
├── logs/
│   └── procsight.log
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🧰 Installation

```bash
# Clone the repo
git clone https://github.com/<yourusername>/procsight.git
cd procsight

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the tool
python procsight.py
```

---

## 💻 Basic Usage

### 🔍 Find processes

```bash
procsight inspect chrome
```

Lists all processes containing "chrome" in name or command.

### 📊 Show detailed info

```bash
procsight info --pid 1234
```

### ⚙️ Terminate a process (admin)

```bash
sudo procsight terminate --pid 1234 --admin
```

### 🔌 List all listening ports

```bash
procsight ports --listening
```

### 🌍 Show active connections for a process

```bash
procsight ports --pid 1234
```

### 🕵️ Monitor process in real time

```bash
procsight watch nginx
```

### 📋 Export snapshot

```bash
procsight export --format csv --out snapshot.csv
```

---

## 📖 Logging

All admin or system-level actions are recorded automatically in:

```
logs/procsight.log
```

Each entry includes:

* Timestamp
* Command and arguments
* User who ran it
* Result (success/failure)

Example:

```
[2025-11-02 15:41:22] INFO  User=eva Action=terminate PID=4456 Status=success
[2025-11-02 15:42:08] WARN  User=eva Action=restart PID=7721 Status=denied (insufficient privileges)
```

---

## 🧭 Feature Roadmap

| Category                   | Planned Features                                                           |
| -------------------------- | -------------------------------------------------------------------------- |
| 🔐 **Security & Audit**    | Detect unsigned binaries, highlight privileged processes, suspicious ports |
| 📡 **Remote Ops**          | SSH connection & agent for multi-host management                           |
| 🧩 **Plugins**             | Public plugin API (`procsight plugin list / run`)                          |
| 🕰️ **Performance Logs**   | Periodic system snapshots for performance profiling                        |
| 📈 **UI Enhancements**     | ASCII charts (using `plotext` or `rich`) for real-time data                |
| 🧰 **Developer Utilities** | Auto-clean dev servers, identify stale ports                               |
| 💬 **Notifications**       | Optional desktop/Slack alerts for anomalies                                |
| 🌍 **Packaging**           | Publish to PyPI and add Windows EXE wrapper                                |
| 🧪 **Testing**             | GitHub Actions for Linux/Windows/macOS builds                              |

---

## 💡 Why ProcSight Exists

There are hundreds of platform-specific process tools — `htop`, `tasklist`, `netstat`, etc. — but very few that are:

✅ **Cross-platform**
✅ **Readable and colorful**
✅ **Safe (confirmations & logs)**
✅ **Scriptable**
✅ **Extensible**

ProcSight bridges that gap, giving you one clean CLI to **see, understand, and manage** what's happening on your system — processes, services, and ports alike.

---

## 🧑‍💻 Technologies Used

* 🐍 **Python 3.9+**
* 🔧 [`psutil`](https://pypi.org/project/psutil/) — process, system, and network insight
* 🎨 [`colorama`](https://pypi.org/project/colorama/) — terminal colors
* 📋 [`PrettyTable`](https://pypi.org/project/PrettyTable/) — clean table output
* 🧩 [`argparse`](https://docs.python.org/3/library/argparse.html) or [`typer`](https://typer.tiangolo.com/) — CLI framework
* 🧠 `logging` — structured logs in `logs/procsight.log`

---

## 🧾 License

This project is licensed under the **MIT License** — feel free to fork, extend, or adapt it.

---

## 🧑‍💻 Author

**ProcSight** is maintained by [Your Name or Alias].

> "Transparency is power — ProcSight lets you *see* your system."
