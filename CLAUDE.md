# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

APRSlog is the data crawling component for the SGP 2D live tracking application. It collects position data from multiple sources (OGN APRS, SPIDER, SPOT, Garmin InReach, LiveTrack24, SKYLINES/XCsoar, ADS-B, FANET, PilotAware, and more) and stores it in a MariaDB/MySQL or SQLite3 database.

## Running the Application

### Main data collector
```bash
# Via shell wrapper (preferred, reads config and logs output):
bash sh/aprslog.sh [param_file]

# Directly (param files are in sh/param and sh/paramfull):
python3 aprslog.py [options]
# Key flags: -p (print), -d (DATA mode), -l (LASTFIX mode), -m (MEM mode), -s (STATIONS mode)
```

### Position pusher (SPOT/SPIDER/INREACH/etc. to OGN APRS)
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

### Installation
```bash
bash install.sh [MySQL|mariadb|docker]
```

### Linting
```bash
flake8  # uses .flake8 config; ignores E501 (line length), E722 (bare except), F403 (star imports), etc.
```

There is no test suite or CI pipeline.

## Configuration

- Config file location: `/etc/local/APRSconfig.ini` (copied from `config.template` during install)
- Override config directory via `CONFIGDIR` environment variable
- `config.py` reads the INI file and exposes all settings as module-level variables — import with `import config`
- Boolean config values are stored as strings and converted manually: `if (MySQLtext == 'True'): MySQL = True`

## Architecture

### Core flow
1. `aprslog.py` — Main entry point. Connects to OGN APRS server via raw TCP socket (2MB receive buffer), receives APRS messages in a loop, parses them, and stores fixes in the database. Uses SIGTERM handler for orderly shutdown (removes PID file, closes DB).
2. `parserfuncs.py` — Parses APRS messages using `ogn.parser`. Contains `aprssources` dict mapping APRS TOCALLs to source types (OGN, ADSB, FANET, PAW, etc.). Key function: `parseraprs()`.
3. `push2ogn.py` — Separate process that polls non-APRS data sources (SPOT, SPIDER, InReach, LiveTrack24, SKYLINES, Capturs, AvioniX) and pushes their positions into the OGN APRS network.
4. `dlym2ogn.py` — Processes delayed IGC fixes and relays them.

### Symlink structure
Most `*funcs.py` modules are **symlinks** to `/nfs/OGN/src/funcs/` — they are shared across multiple projects. `Keysfuncs.py` links to `../TRKSsrc/Keysfuncs.py`. Only `aprslog.py`, `push2ogn.py`, `dlym2ogn.py`, `config.py`, and a few others are local to this repo. When editing a symlinked file, the change affects all projects that share it.

### Data source modules (each `*funcs.py` handles one source)
- `spotfuncs.py` — SPOT satellite tracker
- `spifuncs.py` — SPIDER
- `inreachfuncs.py` — Garmin InReach
- `lt24funcs.py` — LiveTrack24
- `skylfuncs.py` — SKYLINES/XCsoar
- `captfuncs.py` — Capturs
- `avxfuncs.py` — AvioniX
- `adsbfuncs.py` — ADS-B (local dump1090)
- `enafuncs.py` — ENAIRE (uses MQTT via paho_mqtt)
- `bstopfuncs.py` — BirdStop (drones)
- `flarmfuncs.py` — Flarm ID utilities
- `ogntfuncs.py` — OGN tracker equivalence
- `ognddbfuncs.py` — OGN Device Database (DDB) lookups for Flarm ID to registration mapping

### Supporting modules
- `config.py` — Reads `/etc/local/APRSconfig.ini` (ConfigParser-based), exposes all settings as module globals
- `dtfuncs.py` — Timezone-aware UTC datetime helpers (replacements for deprecated `datetime.utcnow()`)
- `geofuncs.py` — Geographic calculations
- `APRScalsunrisesunset.py` — Sunrise/sunset calculation for the configured location (run before main processes)
- `Keysfuncs.py` — Key/encryption functions
- `ICAO_ranges.py` — ICAO address range lookups

### Key code patterns
- **Global state**: Heavy use of module-level dictionaries for caching (e.g., `fsllo`, `fslla`, `acfttype`, `flastfix` in aprslog.py). Counters like `cin`, `cout`, `loopcnt`, `err` are module globals.
- **DB access**: Direct `MySQLdb.connect()` / `cursor()` calls throughout. Error handling via `except MySQLdb.Error as e:`.
- **Star imports**: `from dtfuncs import *` is standard practice in this codebase (flake8 F403 is suppressed).
- **Process lifecycle**: PID files in `/tmp/APRS.pid`, `/tmp/DLY.pid`. Alive markers (`APRS<hostname>.alive`) in `config.DBpath`. Both are cleaned up on shutdown via SIGTERM handler + atexit.

### Database
- Schema defined in `APRSLOG.template.sql` (MariaDB/MySQL)
- Database name: `APRSLOG`
- Includes custom SQL functions: `GETBEARING`, `GETBEARINGROSE`, `GETDISTANCE` (Haversine)
- DB user: `ogn` (configured in config file)

### Deployment
- `sh/` — Operational shell scripts for running, monitoring, and maintenance (crontab-driven via `sh/crontab.data`)
- `sh/aprslogcheck.sh` — Monitors if aprslog.py is running (every 10 min)
- `sh/aprsidaily.sh` — Daily maintenance tasks
- `dockerfiles/` — Docker-based deployment with MariaDB (`make dev`, `make build`, `make clean`)
- `provisioning/` — Server provisioning scripts (Vagrant/bare metal)
- `utils/` — Contains `ogndecode` (C-based OGN decoder), `dump1090` (ADS-B decoder), `calcelestial`

## Dependencies

- Python 3.5+ with packages in `requirements.txt` (key: `ogn_client`, `MySQLdb`, `geopy`, `requests`, `paho_mqtt`, `suntime`, `airportsdata`)
- Node.js with `forever` for process management
- MariaDB or MySQL server
- Apache2 web server
