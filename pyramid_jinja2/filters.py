from pyramid.url import resource_url, route_url, static_url
from pyramid.threadlocal import get_current_request

__all__ = [
    'model_url_filter',
    'route_url_filter',
    'static_url_filter',
        ]


def model_url_filter(model, *elements, **kw):
    """A filter from ``model`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.resource_url`.
    """
    request = get_current_request()
    return resource_url(model, request, *elements, **kw)


def route_url_filter(route_name, *elements, **kw):
    """A filter from ``route_name`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.route_url`.
    """
    request = get_current_request()
    return route_url(route_name, request, *elements, **kw)

def static_url_filter(path, **kw):
    """A filter from ``path`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.static_url`.
    """
    request = get_current_request()
    return static_url(path, request, **kw)
