from zope.interface import implements
from zope.interface import Interface

from jinja2.loaders import FileSystemLoader
from jinja2 import Environment

from pyramid.interfaces import ITemplateRenderer

from pyramid.exceptions import ConfigurationError
from pyramid.resource import abspath_from_resource_spec
from pyramid.decorator import reify

class IJinja2Environment(Interface):
    pass

def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)

def renderer_factory(info):
    registry = info.registry
    settings = info.settings
    environment = registry.queryUtility(IJinja2Environment)
    if environment is None:
        reload_templates = settings.get('reload_templates', False)
        directories = settings.get('jinja2.directories')
        input_encoding = settings.get('jinja2.input_encoding', 'utf-8')
        autoescape = settings.get('jinja2.autoescape', True)
        if directories is None:
            raise ConfigurationError(
                'Jinja2 template used without a ``jinja2.directories`` setting')
        directories = directories.splitlines()
        directories = [ abspath_from_resource_spec(d) for d in directories ]
        loader = FileSystemLoader(directories,
                                  encoding=input_encoding)
        autoescape = asbool(autoescape)
        environment = Environment(loader=loader, auto_reload=reload_templates,
                                  autoescape=True)
        registry.registerUtility(environment, IJinja2Environment)
    return Jinja2TemplateRenderer(info, environment)

class Jinja2TemplateRenderer(object):
    implements(ITemplateRenderer)
    template = None
    def __init__(self, info, environment):
        self.info = info
        self.environment = environment
 
    def implementation(self):
        return self.template

    @reify
    def template(self):
        return self.environment.get_template(self.info.name)
   
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.template.render(system)
        return result


