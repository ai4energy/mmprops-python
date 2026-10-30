"""MMPROPS: MIT Python client for the MMPROPS property engine.

The engine (`mmprops`) is a commercial binary distributed separately; this
package only runs its public JSON command line and parses the result.

Quick start::

    from mmprops import props, sat

    water = props("water", "300 K", "1 bar")
    print(water.values["rho"], water.units["rho"])
"""

from __future__ import annotations

from .binary import engine_version, find_binary
from .cli import (
    EnvelopeResult,
    PropertyResult,
    VleResult,
    db_pack,
    db_props,
    db_show,
    envelope,
    flash,
    props,
    sat,
    vle,
)
from .errors import (
    MmpropsBinaryNotFound,
    MmpropsError,
    MmpropsProtocolError,
    MmpropsTimeout,
)

__version__ = "0.1.0"

__all__ = [
    "props",
    "sat",
    "flash",
    "vle",
    "envelope",
    "db_props",
    "db_pack",
    "db_show",
    "PropertyResult",
    "VleResult",
    "EnvelopeResult",
    "MmpropsError",
    "MmpropsBinaryNotFound",
    "MmpropsProtocolError",
    "MmpropsTimeout",
    "find_binary",
    "engine_version",
    "__version__",
]
