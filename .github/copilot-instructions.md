# Copilot instructions for APRSlog (APRSsrc)

Purpose: concise, actionable guidance for Copilot sessions working on this repository — how to run, lint, package, and where to look for non-obvious conventions.

---

1) Build, test, and lint commands

- Python deps (recommended virtualenv):
  - python3 -m pip install --upgrade pip
  - python3 -m pip install -r requirements.txt

- Linting (project uses a .flake8 config):
  - flake8  # uses .flake8 settings in repo
  - Lint a single file: flake8 path/to/file.py --max-line-length=120
  - .flake8 suppresses many errors (star imports, long lines, bare except) and sets max-complexity=10.

- Running the main processes (operational entrypoints in sh/):
  - Main collector (preferred wrapper): bash sh/aprslog.sh [param_file]
  - Direct run: python3 aprslog.py [options]
    - Key flags commonly used: -p (print), -d (DATA mode), -l (LASTFIX mode), -m (MEM mode), -s (STATIONS mode)
  - Push positions to OGN APRS:
    - bash sh/PUSH2ogn.sh
    - Direct: python3 push2ogn.py --SPIDER True --SPOT True --INREACH True --AVX True
  - Delayed-IGC processing: bash sh/dlym2ogn.sh or python3 dlym2ogn.py

- Packaging / build:
  - setup.py is present for distribution (metadata only). To build source: python3 setup.py sdist
  - Python version compatibility declared up to 3.9 in setup.py; CI is not present here.

- Docker:
  - Container helpers exist under dockerfiles/ — use the included Makefile and Dockerfiles; example:
    - docker build -f dockerfiles/Dockerfile -t aprslog:local .
    - See dockerfiles/README or Makefile under dockerfiles/ for exact targets (make dev, make build).

- Tests:
  - No formal test suite in-tree. If tests are added, run the whole suite with pytest, or a single test with:
    - pytest tests/test_module.py::test_name
    - or use pytest -k "keyword"

---

2) High-level architecture (big picture)

- Purpose: acquire position telemetry from many sources (OGN APRS, SPIDER, SPOT, Garmin InReach, LiveTrack24, SKYLINES/XCsoar, ADS‑B, etc.), normalize/parsing, persist to DB (SQLite or MySQL/MariaDB), and provide downstream exports.

- Core pieces:
  - aprslog.py — main collector: reads APRS (TCP) and other inputs, parses messages, writes fixes to DB.
  - push2ogn.py — polls external provider APIs (SPOT, SPIDER, InReach, LiveTrack24, etc.) and pushes positions into OGN/APRS when required.
  - dlym2ogn.py — delayed/IGC-related processing pipeline.
  - parserfuncs.py, adsbfuncs.py, flarmfuncs.py, enafuncs.py, etc. — one module per source/protocol for parsing/normalization.
  - sh/ — operational shell scripts used to start, monitor, schedule, and maintain processes (crontab/at-driven).
  - utils/ and provisioning/ — supporting binaries, Docker, provisioning, and compiled helpers (dump1090, calcelestial, etc.).

- Data flow (simplified): source(s) → parsing modules (parserfuncs.py + *funcs.py) → aprslog/push2ogn → DB (SQLite for local fast ingest or MySQL/MariaDB for central storage) → scheduled syncs and downstream consumers.

- Configuration & runtime:
  - Primary config file: /etc/local/APRSconfig.ini (template: config.template). Override directory via CONFIGDIR env var.
  - config.py reads the INI and exposes values as module globals (other modules import import config).

- Symlink/shared modules:
  - Many *funcs.py are symlinks to a shared /nfs/OGN/src/funcs/ tree. Editing such a file changes behavior across projects that share it.

---

3) Key conventions and repo-specific patterns

- Symlink-first layout: expect many modules (adsbfuncs.py, parserfuncs.py, etc.) to be symlinks pointing at a shared codebase under /nfs/OGN/src/funcs. Resolve symlinks before editing.

- Star-imports and global module state: codebase commonly uses `from dtfuncs import *` and module-level mutable globals (caches, counters). When altering parsing/state code, audit global side effects and PID lifecycle handling.

- Flake8 overrides: .flake8 intentionally ignores F403 (star imports), E501 (line length), E722 (bare except), and complexity rules tuned to legacy code. Use the repo .flake8 when linting to match CI expectations.

- PID / alive files: processes create PID files under /tmp (e.g., /tmp/APRS.pid) and alive markers in config.DBpath. Shutdown handlers remove these; tests/tools should respect that lifecycle.

- Database schema & naming:
  - Schema template: APRSLOG.template.sql (MySQL/MariaDB). DB name commonly APRSLOG; DB user configured via APRSconfig.ini.
  - The code uses direct MySQLdb / MySQL API calls rather than an ORM.

- Operational entrypoints: run operational scripts from repo root so relative paths and sh wrappers resolve correctly (e.g., sh/aprslog.sh assumes working dir and config locations).

- External dependencies & runtime privileges:
  - Some installer/provisioning scripts perform apt, mysql, and system configuration (install.sh). Run in controlled environments.
  - Node/forever is used for process management in some deployments — check package.json and node_modules when troubleshooting live deployments.

---

4) Existing AI assistant configs (important to respect)

- CLAUDE.md present: contains detailed usage notes, run commands, symlink warnings, and architecture points. Copy or consult CLAUDE.md when a deeper assistant needs fuller context.
- .claude/ directory exists with auxiliary guidance.

---

Where to look first (programmatic pointers)
- aprslog.py (main collector) — start here to understand parsing & persistence
- parserfuncs.py (shared parsing logic) — crucial for message normalization
- sh/ (operational wrappers) — how processes are started in production
- APRSLOG.template.sql — DB schema and SQL helper functions
- config.template and config.py — runtime configuration loading and default locations
- CLAUDE.md — assistant-oriented notes that may contain run flags and caveats

---

Summary: added concise Copilot instructions covering install/lint/run commands, architecture overview, and conventions (symlinks, global state, PID files, flake8 deviations). If you want additions (Docker-compose examples, a short troubleshooting checklist, or to enable MCP server configs), say which area to expand.