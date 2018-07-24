"""Tests for the identification provider class
"""


import pytest

import kisee.identity_provider as idp


def test_import_idp():
    """Test importing identification provider
    """
    with pytest.raises(ImportError):
        idp.import_idp("helloworldxddd~~~")
    with pytest.raises(ImportError):
        idp.import_idp("my.dummy.path")
    with pytest.raises(ImportError):
        idp.import_idp("kisee.kisee.kisee.UnknownClass")
    with pytest.raises(ImportError):
        idp.import_idp("kisee.providers.dumb.UnknownClass")
