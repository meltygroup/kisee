from kisee import serializers
from kisee.serializers import Document, Field, Link


def test_default_serializer():
    assert serializers.serializers[""] is serializers.serializers.default
    assert serializers.serializers[None] is serializers.serializers.default


def test_corejson_serializer():
    assert (
        serializers.serializers["application/vnd.coreapi+json"]
        is serializers.coreapi_serializer
    )


def test_json_serializer():
    json_serializer = serializers.serializers["application/json"]
    assert json_serializer([]) == []
    assert json_serializer("Hello world") == "Hello world"
    assert json_serializer(Document(url="/", title="Test", content={})) == {}
    assert json_serializer(Link(url="/link/", action="POST", title="Foo")) == "/link/"
    assert (
        json_serializer(
            Field(name="username", required=False, description="Just a login")
        )
        == "username"
    )
