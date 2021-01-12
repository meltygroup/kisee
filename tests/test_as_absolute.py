import pytest

from kisee.serializers import as_absolute


@pytest.mark.parametrize(
    "url",
    [
        "https://mdk.fr",
        "https://mdk.fr/",
        "https://mdk.fr/foo",
        "https://mdk.fr/foo?bar",
    ],
)
def test_as_absolute_from_absolutes(url):
    assert as_absolute(url, url) == url


@pytest.mark.parametrize(
    "url,expected",
    [
        ("", "https://mdk.fr"),
        ("/", "https://mdk.fr/"),
        ("/foo", "https://mdk.fr/foo"),
        ("/foo?bar", "https://mdk.fr/foo?bar"),
    ],
)
def test_as_absolute_from_relatives(url, expected):
    assert as_absolute("https://mdk.fr", url) == expected
