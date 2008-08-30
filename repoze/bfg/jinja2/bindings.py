from webob import Response

from repoze.bfg.path import caller_path

from jinja2.loaders import FunctionLoader
from jinja2 import Environment

def load_template(path):
    path = caller_path(path)
    data = open(path, 'rb').read()
    return unicode(data, 'utf-8')

env = Environment(loader=FunctionLoader(load_template))

def get_template(path):
    """ Return a z3c.pt template object at the package-relative path
    (may also be absolute) """
    path = caller_path(path)
    return env.get_template(path)

def render_template(path, **kw):
    """ Render a z3c.pt (ZPT) template at the package-relative path
    (may also be absolute) using the kwargs in ``*kw`` as top-level
    names and return a string. """
    path = caller_path(path)
    template = get_template(path)
    return template.render(**kw)

def render_template_to_response(path, **kw):
    """ Render a z3c.pt (ZPT) template at the package-relative path
    (may also be absolute) using the kwargs in ``*kw`` as top-level
    names and return a Response object. """
    path = caller_path(path)
    result = render_template(path, **kw)
    return Response(result)

