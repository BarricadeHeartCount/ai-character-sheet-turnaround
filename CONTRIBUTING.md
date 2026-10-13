# Contributing to ai-character-sheet-turnaround

Thanks for wanting to peel some taters with us. This repo is a Windows-first
desktop utility that turns a single character prompt (or reference sketch) into
a standardized character turnaround sheet — front, back, side, three-quarter,
plus a labeled expression/pose grid — using a local diffusion backend or a
pluggable remote renderer.

We're a small hobbyist crew. Contributions are welcome, but please read this
before opening a PR.

## Ground rules

- Python 3.11+ on Windows 10/11 is the primary target. Linux/macOS users are
  welcome but the UI layer (`PySide6`) is only tested on Windows.
- Keep the layered architecture intact. If you're adding a new render backend,
  it goes in `services/`, not in `handlers/`.
- No silent network calls. Every outbound request must go through
  `services/telemetry_gate.py` so users can audit or disable it.
- Every new handler needs a matching test in `tests/`.

## Dev setup

```powershell
git clone https://github.com/yourname/ai-character-sheet-turnaround
cd ai-character-sheet-turnaround
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Then run the smoke test:

```powershell
pytest tests/ -v
```

And launch the app in dev mode:

```powershell
python -m bootstrap.entry --dev
```

## Folder map

| Folder | What lives here |
| --- | --- |
| `bootstrap/` | App entry point, CLI arg parsing, first-run wizard |
| `core/` | The turnaround engine: prompt → pose set → sheet layout |
| `handlers/` | Feature handlers (one per user-facing workflow) |
| `services/` | Backend adapters: local diffusion, remote renderer, cache |
| `models/` | Dataclasses and schemas for characters, poses, sheets |
| `utils/` | Image ops, color helpers, filesystem helpers |
| `config/` | TOML defaults, config loader, schema |
| `tests/` | Pytest suite |

## Style

- `ruff` for lint, `black` for format, `mypy --strict` on `core/` and `models/`.
- Docstrings on every public function. One-line summary, then args/returns if
  non-obvious.
- No bare `except:`. Catch specific exceptions and log with `logging`.

## PR checklist

- [ ] Ran `pytest tests/ -v` locally.
- [ ] Ran `ruff check .` and `black --check .`.
- [ ] If you added a service, updated `services/__init__.py` registry.
- [ ] If you touched the config schema, bumped `CONFIG_VERSION` in
      `config/schema.py` and added a migration note in this file.
- [ ] No new hardcoded paths. Use `utils.paths.project_root()`.

## Reporting bugs

Open an issue with:

1. Your Windows version and Python version.
2. The prompt you used.
3. The generated sheet (attach the PNG) if you can share it.
4. The contents of `logs/last_run.log`.

We're hobbyists. We'll get to it.