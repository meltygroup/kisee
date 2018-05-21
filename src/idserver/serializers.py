from aiohttp import web
import coreapi


class BaseRenderer(object):
    """
    All renderers should extend this class, setting the `media_type`
    and `format` attributes, and override the `.render()` method.
    """
    media_type = ''
    format = ''
    render_style = 'text'

    def render(self, data, media_type=None, renderer_context=None):
        raise NotImplementedError('Renderer class requires .render() '
                                  'to be implemented')


class CoreJSONRenderer(BaseRenderer):
    media_type = 'application/coreapi+json'
    format = 'corejson'

    def __init__(self):
        assert coreapi, ('Using CoreJSONRenderer, '
                         'but `coreapi` is not installed.')

    def render(self, data, media_type=None, renderer_context=None):
        indent = bool(renderer_context.get('indent', 0))
        codec = coreapi.codecs.CoreJSONCodec()
        return codec.dump(data, indent=indent)


def serialize(request, document, headers=None):
    accept = request.headers.get('Accept')
    codec = coreapi.utils.negotiate_encoder(
        [coreapi.codecs.CoreJSONCodec()], accept)
    content = codec.dump(document)
    return web.Response(body=content, content_type=codec.media_type,
                        headers=headers)
