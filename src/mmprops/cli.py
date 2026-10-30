"""One-shot wrappers over the `mmprops` command line (public surface)."""

from __future__ import annotations

import json
import math
import os
import subprocess
from dataclasses import dataclass
from typing import Any, Optional, Sequence

from .binary import find_binary
from .errors import MmpropsBinaryNotFound, MmpropsError, MmpropsProtocolError, MmpropsTimeout


@dataclass
class PropertyResult:
    """`props` / `sat` / `flash` result: SI values keyed by property name."""

    fluid: str
    values: dict
    units: dict
    raw: dict


@dataclass
class VleResult:
    """Binary VLE bubble/dew point (fixed T)."""

    components: list
    kind: str
    converged: bool
    status: str
    t: float
    p: float
    x: list
    y: list
    rho_l: Optional[float]
    rho_v: Optional[float]
    raw: dict


@dataclass
class EnvelopeResult:
    """T-x-y envelope rows (bubble tie line, deterministic order)."""

    components: list
    rows: list
    raw: dict


def props(
    fluid: str,
    t,
    p,
    *,
    data: Optional[str | os.PathLike] = None,
    binary: Optional[str | os.PathLike] = None,
    timeout: Optional[float] = 120.0,
) -> PropertyResult:
    """State-point properties (rho / h / s / cp / cv / w / m)."""
    args = _base("props", binary, data) + [
        "--fluid", _name(fluid, "fluid"),
        "--t", _quantity(t, "t"),
        "--p", _quantity(p, "p"),
        "--format", "json",
    ]
    return _property(_json(args, "props", timeout))


def sat(
    fluid: str,
    t,
    *,
    data: Optional[str | os.PathLike] = None,
    binary: Optional[str | os.PathLike] = None,
    timeout: Optional[float] = 120.0,
) -> PropertyResult:
    """Saturation state at T (psat / rho_l / rho_v / hfg)."""
    args = _base("sat", binary, data) + [
        "--fluid", _name(fluid, "fluid"),
        "--t", _quantity(t, "t"),
        "--format", "json",
    ]
    return _property(_json(args, "sat", timeout))


def flash(
    fluid: str,
    *,
    p,
    h=None,
    s=None,
    data: Optional[str | os.PathLike] = None,
    binary: Optional[str | os.PathLike] = None,
    timeout: Optional[float] = 120.0,
) -> PropertyResult:
    """Flash at p,h or p,s; exactly one of `h` / `s` is required."""
    if (h is None) == (s is None):
        raise ValueError("flash needs exactly one of h=... or s=...")
    spec = "ph" if h is not None else "ps"
    args = _base("flash", binary, data) + [
        "--fluid", _name(fluid, "fluid"),
        "--spec", spec,
        "--p", _quantity(p, "p"),
        "--format", "json",
    ]
    if h is not None:
        args += ["--h", _quantity(h, "h")]
    else:
        args += ["--s", _quantity(s, "s")]
    return _property(_json(args, "flash", timeout))


def vle(
    kind: str,
    components: Sequence[str],
    t,
    *,
    x: Optional[Sequence[float]] = None,
    y: Optional[Sequence[float]] = None,
    data: Optional[str | os.PathLike] = None,
    binary: Optional[str | os.PathLike] = None,
    timeout: Optional[float] = 120.0,
) -> VleResult:
    """Binary VLE bubble/dew point at fixed T."""
    kind = kind.lower()
    if kind not in ("bubble", "dew"):
        raise ValueError(f"vle kind must be 'bubble' or 'dew' (got {kind!r})")
    comps = _components(components)
    if kind == "bubble":
        if x is None:
            raise ValueError("bubble vle requires x=[...]")
        if y is not None:
            raise ValueError("bubble vle takes x, not y")
        args = ["--x", _fractions(x, len(comps), "x")]
    else:
        if y is None:
            raise ValueError("dew vle requires y=[...]")
        if x is not None:
            raise ValueError("dew vle takes y, not x")
        args = ["--y", _fractions(y, len(comps), "y")]
    args = _base("vle", binary, data) + [
        "--kind", kind,
        "--components", ",".join(comps),
        "--t", _quantity(t, "t"),
        "--format", "json",
    ] + args
    env = _json(args, "vle", timeout)
    return VleResult(
        components=[str(c) for c in env.get("components", [])],
        kind=str(env.get("kind", "")),
        converged=bool(env.get("converged", False)),
        status=str(env.get("status", "")),
        t=float(env["t"]),
        p=float(env["p"]),
        x=[float(v) for v in env.get("x", [])],
        y=[float(v) for v in env.get("y", [])],
        rho_l=_maybe_float(env.get("rho_l")),
        rho_v=_maybe_float(env.get("rho_v")),
        raw=env,
    )


def envelope(
    components: Sequence[str],
    t,
    *,
    points: int = 21,
    data: Optional[str | os.PathLike] = None,
    binary: Optional[str | os.PathLike] = None,
    timeout: Optional[float] = 120.0,
) -> EnvelopeResult:
    """T-x-y envelope for a binary mixture at fixed T."""
    comps = _components(components)
    n = _points(points)
    args = _base("envelope", binary, data) + [
        "--components", ",".join(comps),
        "--t", _quantity(t, "t"),
        "--points", str(n),
        "--format", "json",
    ]
    env = _json(args, "envelope", timeout)
    return EnvelopeResult(
        components=[str(c) for c in env.get("components", [])],
        rows=list(env.get("rows", [])),
        raw=env,
    )


def db_props(
    *,
    data: Optional[str | os.PathLike] = None,
    binary: Optional[str | os.PathLike] = None,
    timeout: Optional[float] = 120.0,
) -> list:
    """Names of the registered property functions."""
    text = _text(_base("db", binary, data) + ["props"], "db props", timeout)
    return [line.strip() for line in text.splitlines() if line.strip()]


def db_pack(
    *,
    data: Optional[str | os.PathLike] = None,
    binary: Optional[str | os.PathLike] = None,
    timeout: Optional[float] = 120.0,
) -> str:
    """Current data-pack identity (`pack_id@pack_version#manifest_sha256`)."""
    return _text(_base("db", binary, data) + ["pack"], "db pack", timeout)


def db_show(
    name: str,
    *,
    data: Optional[str | os.PathLike] = None,
    binary: Optional[str | os.PathLike] = None,
    timeout: Optional[float] = 120.0,
) -> str:
    """Look up one registered property function."""
    return _text(_base("db", binary, data) + ["show", _name(name, "name")], "db show", timeout)


def _base(sub: str, binary, data) -> list:
    args = [find_binary(binary), sub]
    if data is not None:
        args += ["--data", os.fspath(data)]
    return args


def _run(args: list, op: str, timeout: Optional[float]) -> subprocess.CompletedProcess:
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        raise MmpropsBinaryNotFound(f"the MMPROPS engine binary disappeared: {args[0]!r}", op=op) from None
    except subprocess.TimeoutExpired:
        raise MmpropsTimeout(f"`mmprops {op}` did not finish within {timeout}s", op=op) from None
    if proc.returncode != 0:
        message = (proc.stderr or proc.stdout or "").strip()
        if not message:
            message = f"`mmprops {op}` exited with code {proc.returncode}"
        raise MmpropsError(message, op=op, raw={"returncode": proc.returncode})
    return proc


def _json(args: list, op: str, timeout: Optional[float]) -> dict:
    proc = _run(args, op, timeout)
    try:
        env = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise MmpropsProtocolError(
            f"`mmprops {op} --format json` emitted non-JSON output: {proc.stdout!r} ({exc})", op=op
        ) from None
    if not isinstance(env, dict):
        raise MmpropsProtocolError(f"expected a JSON object from `mmprops {op}`, got {env!r}", op=op)
    return env


def _text(args: list, op: str, timeout: Optional[float]) -> str:
    return _run(args, op, timeout).stdout.strip()


def _property(env: dict) -> PropertyResult:
    rows = env.get("props", [])
    values = {str(row["name"]): _maybe_float(row.get("value")) for row in rows}
    units = {str(row["name"]): str(row.get("unit", "")) for row in rows}
    return PropertyResult(str(env.get("fluid", "")), values, units, env)


def _maybe_float(value) -> Optional[float]:
    return None if value is None else float(value)


def _name(value, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{what} must be a non-empty string (got {value!r})")
    return value.strip()


def _quantity(value, what: str) -> str:
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError(f"{what} must not be empty")
        return text
    if isinstance(value, bool):
        raise ValueError(f"{what} must be a number or a unit string (got {value!r})")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{what} must be a number or a unit string (got {value!r})") from None
    if not math.isfinite(number):
        raise ValueError(f"{what} must be finite (got {value!r})")
    return str(number)


def _components(components: Sequence[str]) -> list:
    comps = [_name(c, "component") for c in components]
    if len(comps) != 2:
        raise ValueError(f"binary mixtures need exactly two components (got {len(comps)})")
    return comps


def _fractions(values: Sequence[float], n: int, what: str) -> str:
    if len(values) != n:
        raise ValueError(f"{what} needs {n} fractions (got {len(values)})")
    out = []
    for value in values:
        if isinstance(value, bool):
            raise ValueError(f"{what} entries must be numbers (got {value!r})")
        number = float(value)
        if not math.isfinite(number) or number < 0.0 or number > 1.0:
            raise ValueError(f"{what} entries must be finite and within [0, 1] (got {value!r})")
        out.append(str(number))
    return ",".join(out)


def _points(value) -> int:
    if isinstance(value, bool):
        raise ValueError(f"points must be an integer >= 1 (got {value!r})")
    try:
        out = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"points must be an integer >= 1 (got {value!r})") from None
    if out != value or out < 1:
        raise ValueError(f"points must be an integer >= 1 (got {value!r})")
    return out
