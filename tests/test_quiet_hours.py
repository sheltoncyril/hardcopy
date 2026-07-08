from unittest.mock import patch
from datetime import time

from hardcopy.__main__ import is_quiet


def _cfg(enabled: bool = True, start: str = "22:00", end: str = "08:00") -> dict:
    return {"quiet_hours": {"enabled": enabled, "start": start, "end": end}}


def _mock_time(hour: int, minute: int = 0):
    return patch("hardcopy.__main__.datetime") if False else None  # noqa: placeholder


@patch("hardcopy.__main__.datetime")
def test_quiet_during_window_midnight_crossing(mock_dt):
    mock_dt.now.return_value.time.return_value = time(23, 30)
    assert is_quiet(_cfg()) is True


@patch("hardcopy.__main__.datetime")
def test_quiet_during_window_after_midnight(mock_dt):
    mock_dt.now.return_value.time.return_value = time(3, 0)
    assert is_quiet(_cfg()) is True


@patch("hardcopy.__main__.datetime")
def test_not_quiet_outside_window(mock_dt):
    mock_dt.now.return_value.time.return_value = time(12, 0)
    assert is_quiet(_cfg()) is False


@patch("hardcopy.__main__.datetime")
def test_not_quiet_at_boundary_end(mock_dt):
    mock_dt.now.return_value.time.return_value = time(8, 1)
    assert is_quiet(_cfg()) is False


@patch("hardcopy.__main__.datetime")
def test_quiet_disabled(mock_dt):
    mock_dt.now.return_value.time.return_value = time(23, 30)
    assert is_quiet(_cfg(enabled=False)) is False


def test_quiet_missing_config():
    assert is_quiet({}) is False


@patch("hardcopy.__main__.datetime")
def test_same_day_window(mock_dt):
    mock_dt.now.return_value.time.return_value = time(14, 0)
    assert is_quiet(_cfg(start="13:00", end="17:00")) is True


@patch("hardcopy.__main__.datetime")
def test_same_day_window_outside(mock_dt):
    mock_dt.now.return_value.time.return_value = time(12, 0)
    assert is_quiet(_cfg(start="13:00", end="17:00")) is False
