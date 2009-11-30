import os
from webob import Response

from zope.interface import implements
from zope.component import queryUtility

from jinja2.loaders import FileSystemLoader
from jinja2 import Environment

from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.renderers import template_renderer_factory
from repoze.bfg.settings import get_settings

def renderer_factory(path):
    return template_renderer_factory(path, Jinja2TemplateRenderer)

class Jinja2TemplateRenderer(object):
    implements(ITemplateRenderer)
    template = None
    def __init__(self, path):
        settings = get_settings()
        auto_reload = settings and settings['reload_templates']
        directory, filename = os.path.split(path)
        loader = FileSystemLoader(directory)
        self.filename = filename
        self.environment = Environment(loader=loader, auto_reload=auto_reload,
                                       autoescape=True)
        if not auto_reload:
            self.template = self.environment.get_template(self.filename)
 
    def implementation(self):
        if self.template is None:
            # autoreload in effect
            return self.environment.get_template(self.filename)
        return self.template
   
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        template = self.template
        if template is None:
            # autoreload in effect
            template = self.environment.get_template(self.filename)
        result = template.render(system)
        return result

def get_renderer(path):
    """ Return a callable ``ITemplateRenderer`` object representing a
    ``jinja2`` template at the package-relative path (may also
    be absolute). """
    return renderer_factory(path)
    

def get_template(path):
    """ Return a ``jinja2`` template object at the package-relative path
    (may also be absolute) """
    renderer = renderer_factory(path)
    return renderer.implementation()

def render_template(path, **kw):
    """ Render a ``jinja2`` template at the package-relative path
    (may also be absolute) using the kwargs in ``*kw`` as top-level
    names and return a string. """
    renderer = renderer_factory(path)
    return renderer(kw, {})

def render_template_to_response(path, **kw):
    """ Render a ``jinja2`` template at the package-relative path
    (may also be absolute) using the kwargs in ``*kw`` as top-level
    names and return a Response object. """
    renderer = renderer_factory(path)
    result = renderer(kw, {})
    response_factory = queryUtility(IResponseFactory, default=Response)
    return response_factory(result)
