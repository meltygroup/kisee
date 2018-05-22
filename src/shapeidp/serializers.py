"""Serialisers using coreapi, the idea is to (in the future) provide
various representations of our resources like mason, json-ld, hal, ...

"""
import coreapi
from aiohttp import web


class CoreJSONRenderer:
    """Serializer using the coreapi+json representations.
    """
    # pylint: disable=too-few-public-methods
    media_type = 'application/coreapi+json'
    format = 'corejson'

    def __init__(self):
        assert coreapi, ('Using CoreJSONRenderer, '
                         'but `coreapi` is not installed.')

    def render(self, data, media_type=None, renderer_context=None):
        # pylint: disable=unused-argument, no-self-use
        """Render the given data as application/coreapi+json.
        """
        indent = bool(renderer_context.get('indent', 0))
        codec = coreapi.codecs.CoreJSONCodec()
        return codec.dump(data, indent=indent)


def serialize(request, document, headers=None):
    """Serialize the given document according to the Accept header of the
    given request.
    """
    accept = request.headers.get('Accept')
    codec = coreapi.utils.negotiate_encoder(
        [coreapi.codecs.CoreJSONCodec()], accept)
    content = codec.dump(document)
    return web.Response(body=content, content_type=codec.media_type,
                        headers=headers)
