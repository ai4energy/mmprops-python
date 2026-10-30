"""End-to-end tests against a real `mmprops` binary (set MMPROPS_BIN)."""

from __future__ import annotations

import os

import pytest

from mmprops import db_props, envelope, flash, props, sat, vle

BIN = os.environ.get("MMPROPS_BIN")

pytestmark = pytest.mark.skipif(
    not BIN, reason="set MMPROPS_BIN to a real `mmprops` binary to run integration tests"
)


def test_water_state_point():
    out = props("water", "300 K", "1 bar", binary=BIN)
    assert out.values["rho"] == pytest.approx(996.5563375115394, rel=1e-6)
    assert out.values["h"] == pytest.approx(112653.67968883849, rel=1e-6)
    assert out.units["rho"] == "kg/m3"


def test_water_saturation():
    out = sat("water", "373.15 K", binary=BIN)
    assert out.values["psat"] == pytest.approx(101417.99636841458, rel=1e-6)
    assert out.values["hfg"] == pytest.approx(2256403.7215263885, rel=1e-6)


def test_water_flash():
    out = flash("water", p="1 bar", h="1000 kJ/kg", binary=BIN)
    assert out.values["t"] == pytest.approx(372.75592898398463, rel=1e-6)
    assert out.values["x"] == pytest.approx(0.2580334879067689, rel=1e-6)


def test_binary_vle_and_envelope():
    point = vle("bubble", ["methane", "ethane"], "220 K", x=[0.5, 0.5], binary=BIN)
    assert point.converged is True
    assert point.p == pytest.approx(3993218.987928392, rel=1e-6)
    assert point.y[0] == pytest.approx(0.8479107508105308, rel=1e-6)

    curve = envelope(["methane", "ethane"], "220 K", points=3, binary=BIN)
    assert len(curve.rows) >= 3
    assert all("x1" in row and "y1" in row for row in curve.rows)


def test_database():
    names = db_props(binary=BIN)
    assert "T_sat_water" in names
