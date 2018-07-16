"""Tests for the mysql identity provider
"""


import pytest
import shape.mysql as mysql


def test_constant_time_compare():
    """Test constant_time_compare() method
    """
    assert mysql.constant_time_compare("a", "a")
    assert not mysql.constant_time_compare("a", "b")


def test_verify():
    """Test verify() method
    """
    hello_e = "$2y$10$jw2QGuc00GW3SdMhWqLseuLFq6Ng4tHaW6e3qSjaDKxa5CZ.EEUzy"
    assert mysql.verify("hello".encode("utf8"), hello_e.encode("utf8"))
    assert not mysql.verify("world".encode("utf8"), hello_e.encode("utf8"))
    with pytest.raises(RuntimeError):
        mysql.verify("hello".encode("utf8"), "world".encode("utf8"))
