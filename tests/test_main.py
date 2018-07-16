"""Tests for the app
"""


import sys
import pytest
from unittest.mock import patch
import kisee


def test_load_conf():
    """Test the configuration loading
    """
    with pytest.raises(SystemExit):
        kisee.load_conf("settings.toml")
    config = kisee.load_conf("tests/test_settings.toml")
    assert config["server"]["host"] == "0.0.0.0"


def test_parse_args():
    """Test the argument parsing
    """
    with patch.object(sys, "argv", ["dummy"]):
        args = kisee.parse_args()
        assert args.settings == "settings.toml"
    args = kisee.parse_args(["--settings", "hi.toml"])
    assert args.settings == "hi.toml"
