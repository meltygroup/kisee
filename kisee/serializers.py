"""Serialisers using coreapi, the idea is to (in the future) provide
various representations of our resources like mason, json-ld, hal, ...

"""

from collections import OrderedDict
import json
from typing import Optional, Union, List, Dict, Any
from urllib.parse import urljoin

from aiohttp import web


class Document:
    """An API response.

    Expresses the data that the client may access,
    and the actions that the client may perform.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        media_type: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
    ):  # pylint: disable=too-many-arguments
        content = {} if (content is None) else content

        self.url = "" if (url is None) else url
        self.title = "" if (title is None) else title
        self.description = "" if (description is None) else description
        self.media_type = "" if (media_type is None) else media_type
        self.data = content


class Field:
    """API Field, represent a key and a value in a document.
    Schema conforms to http://spec.openapis.org/oas/v3.0.2
    """

    def __init__(
        self, name=False, required="", location=None, schema=None, description=None,
    ):  # pylint: disable=too-many-arguments
        self.name = name
        self.schema = schema
        self.required = required
        self.location = location
        self.description = description


class Link:
    """Links represent the actions that a client may perform.
    """

    def __init__(
        self,
        url: str,
        action: str = None,
        encoding: str = None,
        transform: str = None,
        title: str = None,
        description: str = None,
        fields: List[Union[Field, str]] = None,
    ):  # pylint: disable=too-many-arguments
        self.url = url
        self.action = "" if (action is None) else action
        self._encoding = "" if (encoding is None) else encoding
        self.transform = "" if (transform is None) else transform
        self.title = "" if (title is None) else title
        self.description = "" if (description is None) else description
        self.fields = (
            ()
            if (fields is None)
            else tuple(
                [
                    item
                    if isinstance(item, Field)
                    else Field(item, required=False, location="")
                    for item in fields
                ]
            )
        )


def as_absolute(base, url):
    """Ensure an URL is absolute on the given base.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        return urljoin(base, url)
    return url


def coreapi_serializer(node, base_url=None):
    """Take a Core API document and return Python primitives
    ready to be rendered into the JSON style encoding.
    """
    if isinstance(node, Document):
        ret = OrderedDict()
        ret["_type"] = "document"

        meta = OrderedDict()
        url = node.url
        meta["url"] = as_absolute(base_url, url)
        meta["title"] = node.title
        ret["_meta"] = meta

        # Fill in key-value content.
        ret.update(
            [
                (key, coreapi_serializer(value, base_url=base_url))
                for key, value in node.data.items()
            ]
        )
        return ret

    if isinstance(node, Link):
        ret = OrderedDict()
        ret["_type"] = "link"
        url = node.url
        ret["url"] = as_absolute(base_url, url)
        ret["action"] = node.action
        if node.title:
            ret["title"] = node.title
        ret["description"] = node.description
        ret["fields"] = [
            coreapi_serializer(field, base_url=base_url) for field in node.fields
        ]
        return ret

    if isinstance(node, Field):
        ret = OrderedDict({"name": node.name})
        if node.required:
            ret["required"] = node.required
        ret["schema"] = node.schema
        return ret

    if isinstance(node, list):
        return [coreapi_serializer(value, base_url=base_url) for value in node]

    return node


def serialize(
    request: web.Request, document: Document, status=200, headers=None
) -> web.Response:
    """Serialize the given document according to the Accept header of the
    given request.
    """
    content = json.dumps(
        coreapi_serializer(document, request.app["settings"]["server"]["hostname"]),
        indent=4,
    ).encode("UTF-8")
    return web.Response(
        body=content, content_type="application/json", headers=headers, status=status,
    )
