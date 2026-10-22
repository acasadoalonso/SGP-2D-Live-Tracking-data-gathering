# APRSlog

**OGN/APRS live tracking data crawler** — collects, normalises, and stores position data from dozens of glider tracker sources into a single database.

---

## Overview

APRSlog is the data-crawling backbone for the **SGP 2D live tracking** application. It ingests real-time positions from:

| Source | Module | Description |
|--------|--------|-------------|
| OGN APRS | `aprslog.py` | Raw TCP stream from Open Glider Network APRS servers |
| SPOT | `spotfuncs.py` | Garmin SPOT satellite messenger |
| SPIDER | `spifuncs.py` | SPIDER tracker system |
| Garmin InReach | `inreachfuncs.py` | Garmin InReach LiveTrack |
| LiveTrack24 | `lt24funcs.py` | LiveTrack24 smartphone app |
| SKYLINES / XCsoar | `skylfuncs.py` | SKYLINES virtual soaring / XCsoar |
| Capturs | `captfuncs.py` | Capturs tracker |
| AvioniX | `avxfuncs.py` | AvioniX flight computer |
| ADS-B (dump1090) | `adsbfuncs.py` | Local ADS-B receiver |
| ENAIRE | `enafuncs.py` | Spanish air navigation (MQTT) |
| BirdStop | `bstopfuncs.py` | Drone detection |
| FANET / PilotAware | via `parserfuncs.py` | Protocol-aware APRS parsing |

All data is stored in **MariaDB/MySQL** or **SQLite3**.

---

## Installation

```bash
# Self-installer (choose backend):
bash install.sh [mysql|mariadb|docker]
```

This copies `config.template` → `/etc/local/APRSconfig.ini` and installs dependencies.

### Manual setup

1. Copy the config template:
   ```bash
   cp config.template /etc/local/APRSconfig.ini
   # or override: export CONFIGDIR=/path/to/configs
   ```

2. Import the database schema:
   ```bash
   mysql -u root -p < APRSLOG.template.sql
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

Config file: `/etc/local/APRSconfig.ini` (INI format, read by `config.py`)

Override the config directory at runtime:
```bash
export CONFIGDIR=/custom/path
```

`config.py` exposes every INI key as a module-level variable — import with:
```python
import config
# e.g. config.MySQL, config.DBhost, config.DBname
```

Boolean values are stored as strings and converted manually (e.g. `if MySQLtext == 'True': MySQL = True`).

---

## Usage

### Main data collector (OGN APRS stream)

```bash
# Preferred — shell wrapper reads config & logs output:
bash sh/aprslog.sh [param_file]

# Direct Python invocation:
python3 aprslog.py [options]
# Key flags:
#   -p  print mode
#   -d  DATA mode
#   -l  LASTFIX mode
#   -m  MEM mode
#   -s  STATIONS mode
```

### Position pusher (non-APRS sources → OGN APRS)

```bash
bash sh/PUSH2ogn.sh
# or directly:
python3 push2ogn.py --SPIDER True --SPOT True --INREACH True --AVX True
```

### Delayed IGC fix processor

```bash
bash sh/dlym2ogn.sh
python3 dlym2ogn.py
```

### Sunrise/sunset calculator (run before main processes)

```bash
python3 APRScalsunrisesunset.py
```

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  aprslog.py                      │
│  OGN APRS TCP stream → parserfuncs.py → DB     │
└──────────────┬──────────────────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 parser   *funcs    config
 funcs    .py       .py
    │          │         │
    ▼          ▼         ▼
  source   device     INI
  types    modules   config
```

### Core flow

1. **`aprslog.py`** — Main entry point. Connects to OGN APRS server via raw TCP (2 MB receive buffer), receives APRS messages in a loop, parses them via `parserfuncs.py`, and stores fixes in the database. Handles SIGTERM for orderly shutdown (removes PID file, closes DB).

2. **`parserfuncs.py`** — Parses APRS messages using `ogn.parser`. Maintains an `aprssources` dict mapping APRS TOCALLs to source types (OGN, ADSB, FANET, PAW, etc.). Key function: `parseraprs()`.

3. **`push2ogn.py`** — Separate process that polls non-APRS data sources (SPOT, SPIDER, InReach, LiveTrack24, SKYLINES, Capturs, AvioniX) and pushes their positions into the OGN APRS network.

4. **`dlym2ogn.py`** — Processes delayed IGC fixes and relays them.

### Symlink structure

Most `*funcs.py` modules are **symlinks** to `/nfs/OGN/src/funcs/` — they are shared across multiple projects. Only a handful of files (`aprslog.py`, `push2ogn.py`, `config.py`, etc.) are local to this repo. Editing a symlinked file affects all sharing projects.

---

## Directory structure

```
APRSsrc/
├── aprslog.py              # Main OGN APRS data collector
├── push2ogn.py             # Push non-APRS positions to OGN network
├── dlym2ogn.py             # Delayed IGC fix processor
├── config.py               # INI config reader (module globals)
├── parserfuncs.py          # APRS message parser
├── *funcs.py               # Per-source device modules (symlinks → /nfs/OGN/src/funcs/)
├── APRScalsunrisesunset.py # Sunrise/sunset calculator
├── ICAO_ranges.py          # ICAO address range lookups
├── aircraftDatabase.csv    # Aircraft type database
├── APRSLOG.template.sql    # Database schema (MariaDB/MySQL)
├── aprslog.sql             # SQL dump
├── sh/                     # Operational shell scripts
│   ├── aprslog.sh          # Main collector wrapper
│   ├── PUSH2ogn.sh         # Position pusher wrapper
│   ├── dlym2ogn.sh         # Delayed IGC processor wrapper
│   ├── crontab.data        # Cron schedule
│   ├── param/              # Parameter files for aprslog.py
│   └── paramfull/          # Full parameter set
├── utils/                  # Testing utilities (symlinked *funcs.py helpers)
├── dockerfiles/            # Docker deployment configs
├── provisioning/           # Infrastructure provisioning
├── tar1090-db/             # ADS-B receiver integration
├── opensky-api/            # OpenSky Network API client
├── doc/                    # Documentation
├── archive/                # Archived data
├── install.sh              # Self-installer
└── requirements.txt        # Python dependencies
```

---

## Database

- **Schema**: `APRSLOG.template.sql` (MariaDB/MySQL)
- **Database name**: `APRSLOG`
- **Default user**: `ogn` (configured in INI file)
- **Custom SQL functions**: `GETBEARING`, `GETBEARINGROSE`, `GETDISTANCE` (Haversine formula)

---

## Operations

### Crontab

The operational schedule is defined in `sh/crontab.data`. Install with:
```bash
crontab sh/crontab.data
```

### Monitoring scripts

| Script | Purpose |
|--------|---------|
| `APRSlogcheck.sh` | Check APRS log health |
| `PUSHcheck.sh` | Check push process status |
| `DLYMcheck.sh` | Check delayed IGC processor |
| `aprsclean.sh` | Clean old data |
| `aprsidaily.sh` / `aprsmonthly.sh` / `aprsweekly.sh` / `aprsyearly.sh` | Periodic reports |
| `DUMPhourly.sh` | Hourly data dump |
| `NC2softrf.sh` / `nctosftrf.sh` | Network converter to software reference |

---

## Key code patterns

- **Global state**: Heavy use of module-level dictionaries for caching (e.g. `fsllo`, `fslla`, `acfttype`, `flastfix`). Counters like `cin`, `cout`, `loopcnt`, `err` are module globals.
- **DB access**: Direct `MySQLdb.connect()` / `cursor()` calls throughout. Error handling via `except MySQLdb.Error as e:`.
- **Star imports**: `from dtfuncs import *` is standard practice (flake8 F403 suppressed).
- **Process lifecycle**: PID files in `/tmp/APRS.pid`, `/tmp/DLY.pid`. Alive markers (`APRS<hostname>.alive`) in `config.DBpath`. Both cleaned up on shutdown via SIGTERM handler + `atexit`.

---

## Linting

```bash
flake8  # uses .flake8 config; ignores E501, E722, F403, etc.
```

---

## License

See [LICENSE](LICENSE) and [COPYING](COPYING).
