#!/usr/bin/env python3
"""Build .plugin and/or .skill files from this repo."""

import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path.cwd()
BUILD_DIR = REPO_ROOT / "dist"


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

RESET = "\033[0m"
BOLD  = "\033[1m"
BLUE  = "\033[1;34m"
GREEN = "\033[1;32m"
RED   = "\033[1;31m"
DIM   = "\033[2m"


def info(msg: str) -> None:
    print(f"{BLUE}  {msg}{RESET}")


def ok(msg: str) -> None:
    print(f"{GREEN}✓ {msg}{RESET}")


def die(msg: str) -> None:
    print(f"{RED}error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def choose(prompt: str, options: list[tuple[str, str]]) -> list[int]:
    """
    Display a numbered menu and return the selected indices (0-based).
    Supports multi-select by entering comma-separated numbers or 'all'.
    """
    print(f"\n{BOLD}{prompt}{RESET}")
    for i, (label, desc) in enumerate(options, 1):
        print(f"  {BOLD}{i}{RESET}. {label}{DIM}  — {desc}{RESET}")
    print(f"  {BOLD}a{RESET}. all")
    print()

    while True:
        raw = input("Choice(s) [1]: ").strip() or "1"
        if raw.lower() == "a":
            return list(range(len(options)))
        try:
            selected = [int(x.strip()) - 1 for x in raw.split(",")]
            if all(0 <= i < len(options) for i in selected):
                return selected
        except ValueError:
            pass
        print(f"{RED}  Invalid — enter numbers like 1 or 1,2 or 'a'{RESET}")


def confirm(prompt: str, default: bool = True) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    raw = input(f"{BOLD}{prompt}{RESET} {hint} ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes")


# ---------------------------------------------------------------------------
# Build logic
# ---------------------------------------------------------------------------

def read_manifest() -> dict:
    manifest = REPO_ROOT / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        die(f"plugin.json not found at {manifest}")
    with manifest.open() as f:
        data = json.load(f)
    for key in ("name", "version"):
        if key not in data:
            die(f"'{key}' missing in plugin.json")
    return data


def zip_dir(source: Path, archive: Path) -> None:
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in source.rglob("*"):
            zf.write(file, file.relative_to(source))


def build_plugin(manifest: dict, out_dir: Path) -> Path:
    slug = f"{manifest['name']}-{manifest['version']}"
    out = out_dir / f"{slug}.plugin"
    info(f"Building {out.name} …")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Always include the manifest dir
        shutil.copytree(REPO_ROOT / ".claude-plugin", tmp_path / ".claude-plugin")

        # Include optional top-level artefacts if present
        for item in ("skills", "agents", "hooks", ".mcp.json", "LICENSE", "README.md"):
            src = REPO_ROOT / item
            if src.exists():
                dest = tmp_path / item
                if src.is_dir():
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)

        zip_dir(tmp_path, out)

    ok(f"Plugin → dist/{out.name}")
    return out


def list_skills() -> list[Path]:
    skills_dir = REPO_ROOT / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(p for p in skills_dir.iterdir() if p.is_dir())


def build_skill(skill_dir: Path, out_dir: Path) -> Path:
    name = skill_dir.name
    out = out_dir / f"{name}.skill"
    info(f"Building {out.name} …")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / name
        shutil.copytree(skill_dir, tmp_path)
        zip_dir(Path(tmp), out)

    ok(f"Skill  → dist/{out.name}")
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"\n{BOLD}ckstack builder{RESET}")
    print(DIM + "─" * 40 + RESET)

    manifest = read_manifest()
    skills = list_skills()

    # --- What to build ---
    options = [
        ("Plugin (.plugin)", f"{manifest['name']}-{manifest['version']}.plugin"),
    ]
    skill_start = len(options)
    for s in skills:
        options.append((f"Skill: {s.name}", f"{s.name}.skill"))

    selected = choose("What would you like to build?", options)

    build_plugin_flag = any(i < skill_start for i in selected)
    selected_skills = [skills[i - skill_start] for i in selected if i >= skill_start]

    # --- Output dir ---
    raw_out = input(f"\nOutput directory [{BUILD_DIR}]: ").strip()
    out_dir = Path(raw_out).expanduser() if raw_out else BUILD_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- Build ---
    print()
    built: list[Path] = []

    if build_plugin_flag:
        built.append(build_plugin(manifest, out_dir))

    for skill_dir in selected_skills:
        built.append(build_skill(skill_dir, out_dir))

    print(f"\n{GREEN}{BOLD}Done.{RESET} {len(built)} artifact(s) in {out_dir}/\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
