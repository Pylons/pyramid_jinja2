from pyramid.url import resource_url, route_url
from pyramid.threadlocal import get_current_request

__all__ = [
    'model_url_filter',
    'route_url_filter',
        ]


def model_url_filter(model, *elements, **kw):
    """A filter from ``model`` to a string representing the absolute URL.
    this filter call `pyramid.url.resource_url`.
    """
    request = get_current_request()
    return resource_url(model, request, *elements, **kw)


def route_url_filter(route_name, *elements, **kw):
    """A filter from ``route_name`` to a string representing the absolute URL.
    this filter call `pyramid.url.route_url`.
    """
    request = get_current_request()
    return route_url(route_name, request, *elements, **kw)
