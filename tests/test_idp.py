"""Tests for the identification provider class
"""


import pytest
import shapeidp.identity_provider as idp


def test_import_idp():
    """Test importing identification provider
    """
    with pytest.raises(ImportError):
        idp.import_idp("helloworldxddd~~~")
    with pytest.raises(ImportError):
        idp.import_idp("my.dummy.path")
    with pytest.raises(ImportError):
        idp.import_idp("shapeidp.kisee.UnknownClass")
