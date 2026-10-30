"""Locate the MMPROPS **engine binary** and read its version."""

from __future__ import annotations

import os
import re
import shutil
import subprocess

from .errors import MmpropsBinaryNotFound

_VERSION_RE = re.compile(r"\bmmprops\s+(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\b")


def find_binary(explicit: str | os.PathLike | None = None) -> str:
    """Return the path to the `mmprops` executable.

    Resolution order: ``explicit`` argument → ``$MMPROPS_BIN`` → ``PATH``.
    An explicitly given path that is not executable is a **loud** error.
    """
    for source, candidate in (("argument", explicit), ("MMPROPS_BIN", os.environ.get("MMPROPS_BIN"))):
        if not candidate:
            continue
        path = os.path.expanduser(os.fspath(candidate))
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
        raise MmpropsBinaryNotFound(
            f"the MMPROPS engine binary from {source} is not an executable file: {path!r}"
        )
    found = shutil.which("mmprops")
    if found:
        return found
    raise MmpropsBinaryNotFound(
        "the MMPROPS engine binary (`mmprops`) was not found: put it on PATH or set "
        "MMPROPS_BIN=<path>. The academic binary is published at "
        "https://github.com/ai4energy/mmprops/releases."
    )


def engine_version(binary: str, timeout: float = 10.0) -> str | None:
    """Return the engine version string (e.g. ``0.6.0``), or ``None``."""
    try:
        out = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    match = _VERSION_RE.search(out.stdout or out.stderr)
    return match.group(1) if match else None
