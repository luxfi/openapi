#!/usr/bin/env python3
"""validate_openapi.py — Lux openapi v3.1 validator.

Validates every yaml file in the parent directory against a minimal
OpenAPI v3.1 shape contract and asserts every fixture file is valid
JSON. Pure-stdlib + PyYAML; no external openapi tooling required.

Exit 0 on success, non-zero on any failure.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("error: PyYAML not installed. Run: pip install pyyaml\n")
    sys.exit(2)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


# ---------------------------------------------------------------------
# Shape contract
# ---------------------------------------------------------------------


REQUIRED_TOPLEVEL = {"openapi", "info", "paths"}
OPENAPI_VERSION = "3.1.0"

# Banned vocabulary tokens; matched case-insensitively across yaml +
# markdown.
VOCAB_BANNED = [
    "avalanche",
    "etna",
    "avax",
    "ava-labs",
    "avalanchego",
]

# Whole-word banned tokens (regex-style word boundary check below).
VOCAB_BANNED_WORDS = ["subnet"]

# Other-brand tokens that must not leak into the Lux spec. All
# matched as whole words because every one of these has substring
# collisions in legitimate technical vocabulary (parse, hanzo, etc.).
OTHER_BRAND_WORDS = [
    "hanzo",
    "liquidity",
    "zoo",
    "pars",
    "spc",
    "onyx",
    "liquid",
    "ats",
    "bd",
    "ta",
    "dex",
]
OTHER_BRAND_TOKENS: list[str] = []


# ---------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------


def load_yaml(path: Path) -> dict:
    with path.open() as fh:
        return yaml.safe_load(fh)


def load_json(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


# ---------------------------------------------------------------------
# Shape checks
# ---------------------------------------------------------------------


def check_toplevel(spec: dict, name: str) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_TOPLEVEL - set(spec.keys())
    if missing:
        errors.append(f"{name}: missing top-level keys {sorted(missing)}")
    if spec.get("openapi") != OPENAPI_VERSION:
        errors.append(
            f"{name}: openapi version is {spec.get('openapi')!r}, want {OPENAPI_VERSION!r}"
        )
    info = spec.get("info") or {}
    for k in ("title", "version"):
        if not info.get(k):
            errors.append(f"{name}: info.{k} missing")
    paths = spec.get("paths") or {}
    if not paths:
        errors.append(f"{name}: paths is empty")
    return errors


def check_no_deprecated(spec: dict, name: str) -> list[str]:
    """v1 contract bans deprecated:true anywhere."""
    errors: list[str] = []

    def walk(node, ctx):
        if isinstance(node, dict):
            if node.get("deprecated") is True:
                errors.append(f"{name}: deprecated:true at {ctx} (v1 bans deprecation)")
            for k, v in node.items():
                walk(v, f"{ctx}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{ctx}[{i}]")

    walk(spec, name)
    return errors


def check_servers(spec: dict, name: str) -> list[str]:
    """Servers array must mention the three canonical gateway URLs."""
    errors: list[str] = []
    servers = spec.get("servers") or []
    urls = [s.get("url", "") for s in servers]
    required = {
        "https://api.lux.network/v1",
        "https://api-test.lux.network/v1",
        "https://api-dev.lux.network/v1",
    }
    missing = required - set(urls)
    if missing:
        errors.append(f"{name}: servers missing {sorted(missing)}")
    return errors


# ---------------------------------------------------------------------
# Vocabulary scrub
# ---------------------------------------------------------------------


import re


def scrub_text(text: str, path: Path) -> list[str]:
    errors: list[str] = []
    lower = text.lower()
    for tok in VOCAB_BANNED:
        if tok in lower:
            errors.append(f"{path.name}: banned token {tok!r}")
    for tok in VOCAB_BANNED_WORDS:
        if re.search(rf"\b{re.escape(tok)}\b", lower):
            errors.append(f"{path.name}: banned token {tok!r}")
    for tok in OTHER_BRAND_TOKENS:
        if tok in lower:
            errors.append(f"{path.name}: other-brand token {tok!r}")
    for tok in OTHER_BRAND_WORDS:
        if re.search(rf"\b{re.escape(tok)}\b", lower):
            errors.append(f"{path.name}: other-brand token {tok!r}")
    return errors


# ---------------------------------------------------------------------
# Fixture checks
# ---------------------------------------------------------------------


def check_fixtures(fixtures_dir: Path) -> list[str]:
    errors: list[str] = []
    if not fixtures_dir.is_dir():
        return [f"fixtures: directory {fixtures_dir} missing"]
    for fp in sorted(fixtures_dir.glob("*.json")):
        try:
            data = load_json(fp)
        except json.JSONDecodeError as e:
            errors.append(f"{fp.name}: invalid JSON: {e}")
            continue
        # JSON-RPC fixtures: envelope shape if jsonrpc key present.
        if isinstance(data, dict) and data.get("jsonrpc") == "2.0":
            if "id" not in data:
                errors.append(f"{fp.name}: JSON-RPC fixture missing 'id'")
            if "result" not in data and "error" not in data and "method" not in data:
                errors.append(
                    f"{fp.name}: JSON-RPC fixture has neither 'result', 'error', nor 'method'"
                )
    return errors


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main() -> int:
    yaml_files = sorted(ROOT.glob("*.yaml"))
    md_files = sorted(ROOT.glob("*.md"))
    if not yaml_files:
        sys.stderr.write(f"no yaml files in {ROOT}\n")
        return 2

    all_errors: list[str] = []

    for yp in yaml_files:
        try:
            spec = load_yaml(yp)
        except yaml.YAMLError as e:
            all_errors.append(f"{yp.name}: yaml parse error: {e}")
            continue
        if not isinstance(spec, dict):
            all_errors.append(f"{yp.name}: top-level is not a mapping")
            continue
        all_errors += check_toplevel(spec, yp.name)
        all_errors += check_no_deprecated(spec, yp.name)
        all_errors += check_servers(spec, yp.name)
        with yp.open() as fh:
            all_errors += scrub_text(fh.read(), yp)

    for mp in md_files:
        with mp.open() as fh:
            all_errors += scrub_text(fh.read(), mp)

    all_errors += check_fixtures(ROOT / "fixtures")

    if all_errors:
        for e in all_errors:
            sys.stderr.write(f"  {e}\n")
        sys.stderr.write(f"\n{len(all_errors)} error(s)\n")
        return 1

    counts = {
        "yaml": len(yaml_files),
        "md": len(md_files),
        "fixtures": len(list((ROOT / "fixtures").glob("*.json"))),
    }
    print(
        f"OK: {counts['yaml']} yaml + {counts['md']} markdown + "
        f"{counts['fixtures']} fixtures validated"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
