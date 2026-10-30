"""Shared fixture: an executable `mmprops` shim running the fake CLI."""

from __future__ import annotations

import pathlib
import shlex
import sys

import pytest

FAKE = pathlib.Path(__file__).with_name("fake_mmprops.py")


@pytest.fixture
def fake_bin(tmp_path: pathlib.Path) -> str:
    shim = tmp_path / "mmprops"
    shim.write_text(
        "#!/bin/sh\nexec %s %s \"$@\"\n"
        % (shlex.quote(sys.executable), shlex.quote(str(FAKE)))
    )
    shim.chmod(0o755)
    return str(shim)
