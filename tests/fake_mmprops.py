#!/usr/bin/env python3
"""A faithful fake of the `mmprops` CLI for client tests.

Canned values match the real engine at the states used by the tests. Set
``FAKE_MMPROPS_MODE`` to ``bad-json``, ``crash``, or ``silent`` to exercise
failure paths.
"""

from __future__ import annotations

import json
import os
import sys
import time

MODE = os.environ.get("FAKE_MMPROPS_MODE", "ok")


def emit(obj):
    print(json.dumps(obj))
    return 0


def opt(argv, name):
    try:
        return argv[argv.index(name) + 1]
    except (ValueError, IndexError):
        return None


def main(argv):
    if "--version" in argv:
        print("mmprops 0.6.0")
        return 0
    if MODE == "crash":
        print("fake mmprops: crashed", file=sys.stderr)
        return 3
    if MODE == "silent":
        time.sleep(30)
    if MODE == "bad-json":
        print("this is not json")
        return 0
    sub = argv[0] if argv else ""
    if sub == "props":
        if opt(argv, "--fluid") != "water" or opt(argv, "--format") != "json":
            print("fake: props needs --fluid water --format json", file=sys.stderr)
            return 2
        return emit(
            {
                "engine": "Water",
                "fluid": "water",
                "props": [
                    {"name": "rho", "unit": "kg/m3", "value": 996.5563375115394},
                    {"name": "h", "unit": "J/kg", "value": 112653.67968883849},
                    {"name": "s", "unit": "J/(kg·K)", "value": 393.0624338144479},
                ],
                "spec": {"p": 100000.0, "t": 300.0},
            }
        )
    if sub == "sat":
        if opt(argv, "--fluid") != "water":
            return 2
        return emit(
            {
                "fluid": "water",
                "props": [
                    {"name": "psat", "unit": "Pa", "value": 101417.99636841458},
                    {"name": "rho_l", "unit": "mol/m3", "value": 53196.49137818544},
                    {"name": "rho_v", "unit": "mol/m3", "value": 33.20349107249471},
                    {"name": "hfg", "unit": "J/kg", "value": 2256403.7215263885},
                ],
                "spec": "T=373.15 K",
            }
        )
    if sub == "flash":
        if opt(argv, "--spec") not in ("ph", "ps"):
            return 2
        if opt(argv, "--h") is None and opt(argv, "--s") is None:
            return 2
        return emit(
            {
                "fluid": "water",
                "props": [
                    {"name": "t", "unit": "K", "value": 372.75592898398463},
                    {"name": "x", "unit": "-", "value": 0.2580334879067689},
                    {"name": "rho", "unit": "kg/m3", "value": None},
                    {"name": "h", "unit": "J/kg", "value": 1000000.0},
                    {"name": "s", "unit": "J/(kg·K)", "value": None},
                ],
                "spec": "p=100000 Pa · phase=two_phase",
            }
        )
    if sub == "vle":
        kind = opt(argv, "--kind")
        comps = (opt(argv, "--components") or "").split(",")
        if kind == "bubble" and opt(argv, "--x") is None:
            return 2
        if kind == "dew" and opt(argv, "--y") is None:
            return 2
        x = [0.5, 0.5] if kind == "bubble" else [0.5, 0.5]
        y = [0.8479107508105308, 0.15208924918946917]
        return emit(
            {
                "components": comps,
                "converged": True,
                "kind": kind,
                "p": 3993218.987928392,
                "rho_l": 16561.445375954965,
                "rho_v": 3187.3457116610057,
                "status": "ok",
                "t": 220.0,
                "x": x,
                "y": y,
            }
        )
    if sub == "envelope":
        return emit(
            {
                "components": (opt(argv, "--components") or "").split(","),
                "rows": [
                    {"x1": 0.001, "y1": 0.0135, "p": 499115.0, "status": "ok", "converged": True},
                    {"x1": 0.5, "y1": 0.8479, "p": 3993218.0, "status": "ok", "converged": True},
                    {"x1": 1.0, "y1": 1.0, "p": 1000000.0, "status": "ok", "converged": True},
                ],
            }
        )
    if sub == "db":
        action = argv[1] if len(argv) > 1 else ""
        if action == "props":
            print("T_sat_water\nT_sat_R134a\nT_sat_NH3")
            return 0
        if action == "pack":
            print("baseline@1#abc123")
            return 0
        if action == "show":
            print("T_sat_water exists arity=1")
            return 0
    print(f"fake: unknown command {argv!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
