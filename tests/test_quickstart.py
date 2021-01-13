"""Test kisee quickstart
"""

import io
from test.support import temp_cwd

import pytest
from _pytest.monkeypatch import MonkeyPatch

from kisee import quickstart


def test_quickstart(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("\n" * 1000))
    with temp_cwd():
        quickstart.main()
        with open("settings.toml") as first_settings_file:
            first_settings = first_settings_file.read()
        quickstart.main()
        with open("settings.toml") as second_settings_file:
            second_settings = second_settings_file.read()
        assert first_settings != second_settings


def test_input(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("youpi"))
    assert quickstart.input_or_default("Say youpi?") == "youpi"


def test_2nd_time(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("youpi\nyes"))
    assert quickstart.input_or_default("Say yes?", validator=quickstart.boolean) is True


def test_invalid_default_value() -> None:
    with pytest.raises(ValueError):
        quickstart.input_or_default(
            "Give a bool", "not a bool", validator=quickstart.boolean
        )


def test_good_boolean_input_true(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("y"))
    assert quickstart.input_or_default("Hello", "N", quickstart.boolean) is True


def test_bad_then_good_boolean_input_true(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("pouette\ny"))
    assert quickstart.input_or_default("Hello", "N", quickstart.boolean) is True


def test_good_boolean_input_false(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("n"))
    assert quickstart.input_or_default("Hello", "N", quickstart.boolean) is False


def test_bad_then_good_boolean_input_false(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("pouette\nn"))
    assert quickstart.input_or_default("Hello", "N", quickstart.boolean) is False


def test_default_boolean_input(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("\n"))
    assert quickstart.input_or_default("Hello", "N", quickstart.boolean) is False


def test_bad_boolean_input(monkeypatch: MonkeyPatch) -> None:
    with pytest.raises(ValueError):
        quickstart.boolean("world")
