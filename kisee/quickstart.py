"""Kisee quickstart"""

from subprocess import PIPE, run
from typing import Any, Callable, Dict, Optional, Union

import toml

ConfigurationValue = Union[str, int, bool]
Config = Dict[str, Dict[str, ConfigurationValue]]


def input_or_default(
    prompt: str,
    default: Optional[str] = None,
    validator: Callable[[str], ConfigurationValue] = lambda x: x,
) -> ConfigurationValue:
    """The validator is expected to either convert to the expected type,
    or raise a ValueError.

    Optional shortcut: If [] is present in prompt, it will be replaced
    by the default value.
    """
    if default:
        validator(default)  # Fail loudly if the default don't pass the validator.
    while True:
        response = input(prompt.replace("[]", f"[{default}]"))
        if default is not None and not response:
            return validator(default)
        try:
            return validator(response)
        except ValueError as err:
            print(err)
            continue


def boolean(value: str) -> bool:
    """Convert a "human" boolean (Y, Yes, True, ...) to a Python boolean,
    raising a ValueError if it can't be converted.
    """
    if value.lower() not in {"y", "yes", "n", "no", "true", "false"}:
        raise ValueError('Please enter either "y" or "n".')
    return value.lower() in {"y", "yes", "true"}


def questions() -> Dict[str, Any]:
    """Ask questions interactively to the user to build a settings file."""
    print(
        "Welcome to the Kisee quickstart configurator,",
        "Just press ENTER to accept a default value (if given, in brackets)",
        sep="\n",
    )
    responses: Config = {
        "server": {},
        "identity_backend": {"class": "kisee.providers.demo.DemoBackend"},
        "jwt": {"iss": "example.com"},
    }
    responses["server"]["host"] = input_or_default("Listen to []: ", "127.0.0.1")
    responses["server"]["port"] = input_or_default("Listen on port []: ", "8140")
    responses["server"]["hostname"] = input_or_default(
        "Exposed URL []: ", "http://localhost:8140"
    )
    responses["server"]["debug"] = input_or_default(
        "Debug mode []: ", "No", validator=boolean
    )
    return responses


def add_ec_keys(config: Config) -> None:
    """Invokes openssl to create a new secp256k1 key pair."""
    private_key_process = run(
        ["openssl", "ecparam", "-name", "secp256k1", "-genkey", "-noout", "-out", "-"],
        check=True,
        stdout=PIPE,
    )
    private_key = private_key_process.stdout.decode("ASCII")
    public_key_process = run(
        ["openssl", "ec", "-in", "-", "-pubout"],
        check=True,
        input=private_key_process.stdout,
        stdout=PIPE,
    )
    public_key = public_key_process.stdout.decode("ASCII")
    config["jwt"]["private_key"] = private_key
    config["jwt"]["public_key"] = public_key


def main() -> None:
    """Kisee-quickstart entry point."""
    config = questions()
    add_ec_keys(config)
    print("Writing configuration file to settings.toml...")
    with open("settings.toml", "w") as settings_file:
        toml.dump(config, settings_file)


if __name__ == "__main__":
    main()
