from pyramid.threadlocal import get_current_request
from pyramid.url import resource_url, route_path, route_url, static_path, static_url

try:
    from jinja2 import pass_context
except ImportError:
    # jinja2 < 3.0 fallback
    from jinja2 import contextfilter as pass_context

__all__ = [
    "resource_url_filter",
    "model_url_filter",
    "route_url_filter",
    "route_path_filter",
    "static_url_filter",
    "static_path_filter",
]


@pass_context
def resource_url_filter(ctx, model, *elements, **kw):
    """A filter from ``model`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.resource_url`.

    Example::

        <a href="{{ "my_traversable_object"|resource_url }}">
            See my object
        </a>

    You can also specify optional view name attached at the end of a path::

        <a href="{{ "my_traversable_object"|resource_url("edit") }}">
            Edit my object
        </a>

    """
    request = ctx.get("request") or get_current_request()
    return resource_url(model, request, *elements, **kw)


@pass_context
def model_url_filter(ctx, model, *elements, **kw):
    """A filter from ``model`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.resource_url`.

    .. note ::

        This is being deprecated.
        See :py:func:`pyramid_jinja2.filters.resource_url`

    """
    request = ctx.get("request") or get_current_request()
    return resource_url(model, request, *elements, **kw)


@pass_context
def model_path_filter(ctx, model, *elements, **kw):
    """A filter from ``model`` to a string representing the relative URL.
    This filter calls :py:meth:`pyramid.request.Request.resource_path`.
    """
    request = ctx.get("request") or get_current_request()
    return request.resource_path(model, *elements, **kw)


@pass_context
def route_url_filter(ctx, route_name, *elements, **kw):
    """A filter from ``route_name`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.route_url`.

    Example::

        <a href="{{ "login"|route_url }}">
            Sign in
        </a>

    """
    request = ctx.get("request") or get_current_request()
    return route_url(route_name, request, *elements, **kw)


@pass_context
def route_path_filter(ctx, route_name, *elements, **kw):
    """A filter from ``route_name`` to a string representing the relative URL.
    This filter calls :py:func:`pyramid.url.route_path`.
    """
    request = ctx.get("request") or get_current_request()
    return route_path(route_name, request, *elements, **kw)


@pass_context
def static_url_filter(ctx, path, **kw):
    """A filter from ``path`` to a string representing the absolute URL.
    This filter calls :py:func:`pyramid.url.static_url`.

    Example::

       <link rel="stylesheet" href="{{ "yourapp:static/css/style.css"|static_url }}" />

    """
    request = ctx.get("request") or get_current_request()
    return static_url(path, request, **kw)


@pass_context
def static_path_filter(ctx, path, **kw):
    """A filter from ``path`` to a string representing the relative URL.
    This filter calls :py:func:`pyramid.url.static_path`.
    """
    request = ctx.get("request") or get_current_request()
    return static_path(path, request, **kw)
