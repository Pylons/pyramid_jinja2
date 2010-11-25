from zope.interface import implements
from zope.interface import Interface

from jinja2.loaders import FileSystemLoader
from jinja2 import Environment

from pyramid.interfaces import ITemplateRenderer

from pyramid.exceptions import ConfigurationError
from pyramid.resource import abspath_from_resource_spec

class IJinja2Environment(Interface):
    pass

class IJinja2FilterRegistry(Interface):
    def register_filter(key, value):
        """ register filter
        """
    def get_filter(key):
        """ get registered filter
        """

    def install(environment):
        """ install registered filters to environment
        """

class FilterRegistry(object):

    implements(IJinja2FilterRegistry)

    def __init__(self):
        self.reg = {}

    def register_filter(self, key, value):
        self.reg[key] = value

    def get_filter(key):
        return self.reg[key]

    def install(self, environment):
        for key, func in self.reg.iteritems():
            environment.filters[key] = func

def _get_filter_registry():
    from pyramid.threadlocal import get_current_registry
    reg = get_current_registry()
    filterreg = reg.queryUtility(IJinja2FilterRegistry)
    if filterreg is None:
        filterreg = FilterRegistry()
        reg.registerUtility(filterreg)
    return filterreg

def register_filter(name, filterfunc):
    filterreg = _get_filter_registry()
    filterreg.register_filter(name, filterfunc)
    return filterfunc



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
        filterreg = _get_filter_registry()
        filterreg.install(environment)
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

    @property
    def template(self):
        return self.environment.get_template(self.info.name)
   
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.template.render(system)
        return result


