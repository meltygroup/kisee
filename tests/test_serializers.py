from kisee import serializers


def test_default_serializer():
    assert serializers.serializers[""] is serializers.serializers.default
    assert serializers.serializers[None] is serializers.serializers.default


def test_corejson_serializer():
    assert (
        serializers.serializers["application/coreapi+json"]
        is serializers.coreapi_serializer
    )
