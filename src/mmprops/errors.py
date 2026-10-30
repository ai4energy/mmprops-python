"""Exceptions raised by the MMPROPS Python client."""

from __future__ import annotations


class MmpropsError(Exception):
    """An error reported by the MMPROPS engine (or by the client)."""

    def __init__(self, message: str, *, op: str | None = None, raw: dict | None = None) -> None:
        super().__init__(message)
        self.op = op
        self.raw = raw


class MmpropsBinaryNotFound(MmpropsError):
    """The `mmprops` engine binary could not be located."""


class MmpropsProtocolError(MmpropsError):
    """The engine emitted something that is not the expected JSON."""


class MmpropsTimeout(MmpropsError):
    """The engine did not finish within the client timeout."""
