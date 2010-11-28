from pyramid.url import model_url, route_url
from pyramid.threadlocal import get_current_request

__all__ = [
    'model_url_filter',
    'route_url_filter',
        ]
def model_url_filter(model, *elements):
    request = get_current_request()
    return model_url(model, request, *elements)

def route_url_filter(route_name, *elements, **kw):
    request = get_current_request()
    return route_url(route_name, request, *elements, **kw)

