# Network Scanner

**Python-based TCP port inventory and change detection using Nmap.**

A lightweight network reconnaissance and inventory tool built with Python and Nmap. It automates TCP port scanning, extracts structured service information, persists scan results, and identifies changes between consecutive network inventories.

Designed as an educational cybersecurity project focused on network visibility, service discovery, security automation, and practical Python development.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Nmap](https://img.shields.io/badge/Nmap-Network%20Scanning-1679A7)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)

---

## Overview

Network visibility is an important component of infrastructure management and cybersecurity operations. Understanding which TCP ports and services are exposed by a system helps administrators identify configuration changes and investigate unexpected network behavior.

**Network Scanner** provides a simple workflow for collecting and comparing TCP port information.

The application integrates Nmap with Python to execute scans, parse XML results, generate JSON inventories, and detect differences between successive executions.

### Key capabilities

- **Automated host discovery:** determines the local IPv4 address used for outbound network communication.
- **TCP port scanning:** executes Nmap TCP Connect scans programmatically.
- **Service identification:** collects available service names and port states.
- **Structured data extraction:** parses Nmap XML output using Python's ElementTree library.
- **Persistent inventory:** stores collected information in JSON format.
- **Change detection:** identifies added, removed, and modified port records.
- **Local execution:** runs through the command-line interface without requiring a web service or external database.

## Architecture

The application follows a sequential scanning and comparison workflow.

```text
              ┌───────────────────────┐
              │   Application Start   │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Local IP Detection  │
              │       (socket)        │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Nmap Execution      │
              │     (subprocess)      │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │    XML Processing     │
              │    (ElementTree)      │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Inventory Creation   │
              │     (Python dict)     │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Previous Inventory   │
              │       (JSON)          │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Change Detection    │
              │  Added / Removed /    │
              │       Modified        │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Console Output and   │
              │   Inventory Update    │
              └───────────────────────┘
```

### Technology stack

| Component | Technology | Purpose |
|---|---|---|
| Programming language | Python 3 | Application logic and automation |
| Network scanner | Nmap | TCP scanning and service detection |
| Process execution | `subprocess` | Nmap integration |
| Network interface | `socket` | Local IPv4 detection |
| XML parser | `xml.etree.ElementTree` | Nmap output processing |
| Data persistence | `json` | Inventory storage |
| Version control | Git | Source code management |

The current implementation uses Python's standard library and the externally installed Nmap executable. No third-party Python packages are required.

---

## Getting Started

### Prerequisites

Before running the application, ensure the following dependencies are installed:

- Python 3
- Nmap
- Git (optional, for cloning the repository)

Both Python and Nmap must be accessible through the system's `PATH`.

Verify your installation:

```bash
python --version
nmap --version
```

### Installation

Clone the repository:

```bash
git clone https://github.com/RafaelMizobuchi/python-nmap-network-scanner.git
```

Navigate to the project directory:

```bash
cd python-nmap-network-scanner
```

No additional Python dependencies need to be installed.

### Usage

Run the application:

```bash
python main.py
```

The application automatically determines the local IPv4 address and initiates a TCP port scan.

**Note:** `main.py` is the suggested entry-point filename. Adjust this command if the project uses a different filename.

### Nmap configuration

The scanner currently executes the equivalent of:

```bash
nmap -sT -sV -Pn -oX scan_result.xml <TARGET_IP>
```

| Option | Description |
|---|---|
| `-sT` | TCP Connect scan |
| `-sV` | Service and version detection |
| `-Pn` | Skips host discovery |
| `-oX` | Exports scan results in XML format |

The target address is currently selected automatically using Python's `socket` module.

The current implementation does not support arbitrary target selection through command-line arguments.

---

## Data Model

Each detected port is represented as a structured Python dictionary.

Example JSON inventory:

```json
[
  {
    "ip": "192.168.0.101",
    "porta": "135",
    "protocolo": "tcp",
    "situacao": "open",
    "nome": "msrpc"
  },
  {
    "ip": "192.168.0.101",
    "porta": "445",
    "protocolo": "tcp",
    "situacao": "open",
    "nome": "microsoft-ds"
  }
]
```

This example is illustrative and does not represent a verified scan result.

### Field definitions

| Field | Description |
|---|---|
| `ip` | IPv4 address of the scanned host |
| `porta` | Port number |
| `protocolo` | Transport protocol |
| `situacao` | Port state reported by Nmap |
| `nome` | Service name reported by Nmap |

Scan results are stored locally in `inventario.json`.

The inventory file is overwritten after each completed comparison, retaining the latest collected snapshot.

---

## Change Detection

One of the core features of Network Scanner is its ability to compare two consecutive inventories.

The comparison algorithm uses Python dictionaries and set operations to efficiently identify differences.

### Record identification

Each port record is indexed using a composite key:

```python
key = (
    item["porta"],
    item["ip"],
    item["protocolo"]
)
```

The associated value contains:

```python
value = (
    item["nome"],
    item["situacao"]
)
```

This structure separates the identity of a port record from the attributes monitored for changes.

### Comparison operations

**Added ports**

Records present in the current inventory but absent from the previous inventory.

```python
added = current.keys() - previous.keys()
```

**Removed ports**

Records present in the previous inventory but absent from the current inventory.

```python
removed = previous.keys() - current.keys()
```

**Common ports**

Records whose composite keys exist in both inventories.

```python
common = previous.keys() & current.keys()
```

**Modified ports**

For common keys, the application compares the associated service name and port state.

```python
for key in common:
    if previous[key] != current[key]:
        modified.append({
            "porta": key,
            "anterior": previous[key],
            "atual": current[key]
        })
```

### Example scenario

Consider the following changes between two scans:

| Port | Previous state | Current state | Classification |
|---|---|---|---|
| 22/TCP | Absent | Open | Added |
| 80/TCP | Open | Open | Unchanged |
| 443/TCP | Open | Absent | Removed |
| 8080/TCP | `http` | `http-proxy` | Modified |

The scanner identifies changes based on the collected inventory records.

**Important:** a port reported as removed does not necessarily indicate that the underlying service was permanently removed. It indicates that the record is absent from the latest scan result.

Similarly, service identification is based on Nmap's detection and should not be treated as definitive proof of the software running on a port.

---

## Project Structure

```text
python-nmap-network-scanner/
│
├── main.py                # Scanner and comparison logic
├── README.md              # Project documentation
├── .gitignore             # Git exclusion rules
│
├── scan_result.xml        # Generated Nmap XML output
└── inventario.json        # Generated inventory snapshot
```

The generated XML and JSON files are intended for local execution and should normally be excluded from version control.

Recommended `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Scan artifacts
scan_result.xml
inventario.json

# Environment
.env
.env.*

# IDE and OS
.vscode/
.idea/
.DS_Store
Thumbs.db
```

---

## Current Limitations

The project is under active development and currently has the following limitations.

| Area | Current limitation |
|---|---|
| Target selection | Automatically scans the local IPv4 address |
| Scan scope | Uses Nmap's default TCP port selection |
| Inventory history | Only the latest snapshot is retained |
| Host identity | IP address changes may produce added/removed records |
| Error handling | Some malformed or incomplete XML structures are not yet handled |
| Reporting | Results are displayed in the terminal |
| Testing | Automated tests have not yet been implemented |
| Port states | Comparisons depend on records included in Nmap output |

The application currently processes the first host element found in the XML document.

These limitations are documented to distinguish implemented functionality from future development goals.

---

## Roadmap

### Phase 1 — Core functionality

- [x] Local IPv4 detection
- [x] Nmap integration
- [x] XML parsing
- [x] JSON inventory generation
- [x] Previous inventory loading
- [x] Added port detection
- [x] Removed port detection
- [x] Service and state change detection

### Phase 2 — Reliability and reporting

- [ ] Improve exception handling and input validation
- [ ] Add scan timestamps
- [ ] Implement persistent scan history
- [ ] Generate structured change reports
- [ ] Support CSV exports
- [ ] Add automated unit tests

### Phase 3 — Architecture and extensibility

- [ ] Refactor the application into independent modules
- [ ] Introduce command-line arguments using `argparse`
- [ ] Support user-defined target addresses
- [ ] Implement configurable scan options
- [ ] Add structured application logging
- [ ] Improve multi-host inventory support

The roadmap represents planned improvements rather than committed release dates.

---

## Security Considerations

Network scanning can generate traffic that is detected by security monitoring systems or restricted by organizational policies.

This application is intended for:

- Authorized security assessments
- Personal laboratory environments
- Network administration and inventory
- Cybersecurity education and research

**Only scan systems and networks you own or have explicit permission to assess.**

The application does not attempt exploitation, credential collection, or unauthorized access.

Scan results may contain sensitive infrastructure information. Generated inventory files should be handled appropriately and should not be committed to public repositories without review.

---

## Project Status

**Active development — Educational / Portfolio Project**

This project is being developed incrementally as part of a practical cybersecurity learning path.

The primary focus is to strengthen skills in Python programming, TCP/IP networking, service discovery, structured data processing, and security automation.

It is not currently intended to replace production-grade vulnerability scanners, network monitoring platforms, or asset management solutions.

## Author

**Rafael Ryuichi Mizobuchi**

Computer Engineering Student — Facens, Brazil

Focused on Cybersecurity, Network Security, Infrastructure, and Python Automation.

[GitHub Profile](https://github.com/RafaelMizobuchi)

---

*Built for learning, experimentation, and continuous improvement in cybersecurity engineering.*
