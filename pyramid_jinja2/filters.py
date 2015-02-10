from pyramid.url import resource_url, route_url, static_url
from pyramid.url import route_path, static_path
from pyramid.threadlocal import get_current_request
from jinja2 import contextfilter


__all__ = [
    'model_url_filter',
    'route_url_filter',
    'route_path_filter',
    'static_url_filter',
    'static_path_filter',
]


@contextfilter
def model_url_filter(ctx, model, *elements, **kw):
    """A filter from ``model`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.resource_url`.
    """
    request = ctx.get('request') or get_current_request()
    return resource_url(model, request, *elements, **kw)


@contextfilter
def model_path_filter(ctx, model, *elements, **kw):
    """A filter from ``model`` to a string representing the relative URL.
    This filter calls :py:meth:`pyramid.request.Request.resource_path`.
    """
    request = ctx.get('request') or get_current_request()
    return request.resource_path(model, *elements, **kw)


@contextfilter
def route_url_filter(ctx, route_name, *elements, **kw):
    """A filter from ``route_name`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.route_url`.
    """
    request = ctx.get('request') or get_current_request()
    return route_url(route_name, request, *elements, **kw)


@contextfilter
def route_path_filter(ctx, route_name, *elements, **kw):
    """A filter from ``route_name`` to a string representing the relative URL.
    This filter calls :py:func:`pyramid.url.route_path`.
    """
    request = ctx.get('request') or get_current_request()
    return route_path(route_name, request, *elements, **kw)


@contextfilter
def static_url_filter(ctx, path, **kw):
    """A filter from ``path`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.static_url`.
    """
    request = ctx.get('request') or get_current_request()
    return static_url(path, request, **kw)


@contextfilter
def static_path_filter(ctx, path, **kw):
    """A filter from ``path`` to a string representing the relative URL.
    This filter calls :py:func:`pyramid.url.static_path`.
    """
    request = ctx.get('request') or get_current_request()
    return static_path(path, request, **kw)
