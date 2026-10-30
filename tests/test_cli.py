"""Protocol tests for the MMPROPS Python client, against a faithful fake CLI."""

from __future__ import annotations

import math
import time

import pytest

from mmprops import (
    MmpropsBinaryNotFound,
    MmpropsError,
    MmpropsProtocolError,
    MmpropsTimeout,
    db_pack,
    db_props,
    db_show,
    envelope,
    find_binary,
    flash,
    props,
    sat,
    vle,
)


def test_props_parses_values_and_units(fake_bin):
    out = props("water", "300 K", "1 bar", binary=fake_bin)
    assert out.fluid == "water"
    assert out.values["rho"] == pytest.approx(996.5563375115394)
    assert out.values["h"] == pytest.approx(112653.67968883849)
    assert out.units["rho"] == "kg/m3"
    assert out.raw["engine"] == "Water"


def test_sat(fake_bin):
    out = sat("water", "373.15 K", binary=fake_bin)
    assert out.values["psat"] == pytest.approx(101417.99636841458)
    assert out.values["hfg"] == pytest.approx(2256403.7215263885)


def test_flash_ph_and_ps(fake_bin):
    out = flash("water", p="1 bar", h="1000 kJ/kg", binary=fake_bin)
    assert out.values["t"] == pytest.approx(372.75592898398463)
    assert out.values["x"] == pytest.approx(0.2580334879067689)
    assert out.values["rho"] is None

    out = flash("water", p="1 bar", s="1.1 kJ/(kg·K)", binary=fake_bin)
    assert out.values["h"] == pytest.approx(1.0e6)

    with pytest.raises(ValueError):
        flash("water", p="1 bar", binary=fake_bin)
    with pytest.raises(ValueError):
        flash("water", p="1 bar", h="1 kJ/kg", s="1 kJ/(kg·K)", binary=fake_bin)


def test_vle_bubble_and_dew(fake_bin):
    out = vle("bubble", ["methane", "ethane"], "220 K", x=[0.5, 0.5], binary=fake_bin)
    assert out.converged is True
    assert out.kind == "bubble"
    assert out.p == pytest.approx(3993218.987928392)
    assert out.y[0] == pytest.approx(0.8479107508105308)

    out = vle("dew", ["methane", "ethane"], "220 K", y=[0.85, 0.15], binary=fake_bin)
    assert out.kind == "dew"

    with pytest.raises(ValueError):
        vle("bubble", ["methane", "ethane"], "220 K", binary=fake_bin)
    with pytest.raises(ValueError):
        vle("bubble", ["methane", "ethane"], "220 K", x=[0.5], binary=fake_bin)
    with pytest.raises(ValueError):
        vle("bubble", ["methane"], "220 K", x=[1.0], binary=fake_bin)
    with pytest.raises(ValueError):
        vle("bubble", ["methane", "ethane"], "220 K", x=[0.5, 1.2], binary=fake_bin)


def test_envelope(fake_bin):
    out = envelope(["methane", "ethane"], "220 K", points=3, binary=fake_bin)
    assert len(out.rows) == 3
    assert out.rows[1]["x1"] == pytest.approx(0.5)


def test_db_commands(fake_bin):
    assert "T_sat_water" in db_props(binary=fake_bin)
    assert db_pack(binary=fake_bin) == "baseline@1#abc123"
    assert "exists" in db_show("T_sat_water", binary=fake_bin)


def test_client_validation(fake_bin):
    with pytest.raises(ValueError):
        props("water", math.nan, "1 bar", binary=fake_bin)
    with pytest.raises(ValueError):
        props("water", "300 K", "", binary=fake_bin)
    with pytest.raises(ValueError):
        envelope(["methane", "ethane"], "220 K", points=0, binary=fake_bin)
    with pytest.raises(ValueError):
        props(123, "300 K", "1 bar", binary=fake_bin)
    # None of the rejections sent a request; the fake still works.
    assert props("water", "300 K", "1 bar", binary=fake_bin).values["rho"] > 0


def test_engine_error_carries_op(fake_bin, monkeypatch):
    monkeypatch.setenv("FAKE_MMPROPS_MODE", "crash")
    with pytest.raises(MmpropsError) as excinfo:
        props("water", "300 K", "1 bar", binary=fake_bin)
    assert excinfo.value.op == "props"
    assert "crashed" in str(excinfo.value)


def test_bad_json_is_a_protocol_error(fake_bin, monkeypatch):
    monkeypatch.setenv("FAKE_MMPROPS_MODE", "bad-json")
    with pytest.raises(MmpropsProtocolError):
        props("water", "300 K", "1 bar", binary=fake_bin)


def test_timeout(fake_bin, monkeypatch):
    monkeypatch.setenv("FAKE_MMPROPS_MODE", "silent")
    started = time.monotonic()
    with pytest.raises(MmpropsTimeout):
        props("water", "300 K", "1 bar", binary=fake_bin, timeout=0.3)
    assert time.monotonic() - started < 5.0


def test_binary_resolution(tmp_path, monkeypatch, fake_bin):
    missing = tmp_path / "missing-mmprops"
    with pytest.raises(MmpropsBinaryNotFound):
        find_binary(missing)
    monkeypatch.setenv("MMPROPS_BIN", str(missing))
    with pytest.raises(MmpropsBinaryNotFound):
        find_binary()
    assert find_binary(fake_bin) == fake_bin
