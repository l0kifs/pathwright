"""Test helper utilities."""

from __future__ import annotations

import json
import re
from typing import Any

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def parse_cli_json(output: str) -> Any:
    """Parse JSON payload printed by rich console output."""
    clean = ANSI_RE.sub("", output).strip()

    try:
        parsed = json.loads(clean)
        if isinstance(parsed, str):
            return json.loads(parsed)
        return parsed
    except json.JSONDecodeError:
        pass

    object_start = clean.find("{")
    list_start = clean.find("[")

    starts = [index for index in (object_start, list_start) if index >= 0]
    if not starts:
        raise ValueError(f"No JSON payload found in output: {output!r}")

    payload = clean[min(starts) :]
    first = json.loads(payload)
    if isinstance(first, str):
        return json.loads(first)
    return first
