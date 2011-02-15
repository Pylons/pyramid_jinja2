import os

from zope.interface import (
    implements,
    Interface,
    )

from jinja2 import Environment
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader
from jinja2.utils import (
    import_string,
    open_if_exists
    )

from pyramid.asset import abspath_from_asset_spec
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import ITemplateRenderer
from pyramid.path import caller_package
from pyramid.resource import abspath_from_resource_spec


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


def maybe_import_string(val):
    if isinstance(val, basestring):
        return import_string(val.strip())
    return val


def splitlines(s):
    return filter(None, [x.strip() for x in s.splitlines()])


def parse_filters(filters):
    # input must be a string or dict
    result = {}
    if isinstance(filters, basestring):
        for f in splitlines(filters):
            name, impl = f.split('=', 1)
            result[name.strip()] = maybe_import_string(impl)
    else:
        for name, impl in filters.items():
            result[name] = maybe_import_string(impl)
    return result


def parse_extensions(extensions):
    if isinstance(extensions, basestring):
        extensions = splitlines(extensions)
    return [maybe_import_string(x) for x in extensions]


class FileInfo(object):

    def __init__(self, filename, encoding='utf-8'):
        self.filename = filename
        self.encoding = encoding

    def _delay_init(self):
        if '_mtime' in self.__dict__:
            return

        f = open_if_exists(self.filename)
        if f is None:
            raise TemplateNotFound(self.filename)
        self._mtime = os.path.getmtime(self.filename)
        try:
            self._contents = f.read().decode(self.encoding)
        finally:
            f.close()

    @property
    def contents(self):
        self._delay_init()
        return self._contents

    @property
    def mtime(self):
        self._delay_init()
        return self._mtime

    def uptodate(self):
        try:
            return os.path.getmtime(self.filename) == self.mtime
        except OSError:
            return False


def lookup_asset(asset_spec):
    package = caller_package()
    pname = None
    if package is not None:
        pname = package.__name__
    return abspath_from_asset_spec(asset_spec, pname)


class SmartAssetSpecLoader(FileSystemLoader):
    '''A Jinja2 template loader that knows how to handle
    asset specifications starting with the ``asset:`` prefix.
    '''

    def __init__(self, searchpath=(), encoding='utf-8'):
        FileSystemLoader.__init__(self, searchpath, encoding)

    def list_templates(self):
        raise TypeError('this loader cannot iterate over all templates')

    def _get_asset_source(self, environment, template):
        filename = lookup_asset(template)
        fileinfo = FileInfo(filename, self.encoding)
        return fileinfo.contents, fileinfo.filename, fileinfo.uptodate

    def get_source(self, environment, template):
        if template.startswith('asset:'):
            newtemplate = template.split(':', 1)[1]
            return self._get_asset_source(environment, newtemplate)
        if not self.searchpath:
            raise ConfigurationError('Jinja2 template used without a '
                                     '``jinja2.directories`` setting')
        return FileSystemLoader.get_source(self, environment, template)


def directory_loader_factory(settings):
    input_encoding = settings.get('jinja2.input_encoding', 'utf-8')
    directories = settings.get('jinja2.directories') or ''
    if isinstance(directories, basestring):
        directories = splitlines(directories)
    directories = [abspath_from_resource_spec(d) for d in directories]
    loader = SmartAssetSpecLoader(directories, encoding=input_encoding)
    return loader


def _get_or_build_default_environment(registry):
    environment = registry.queryUtility(IJinja2Environment)
    if environment is not None:
        return environment

    _setup_environment(registry)
    return registry.queryUtility(IJinja2Environment)


def _setup_environment(registry):
    settings = registry.settings
    reload_templates = settings.get('reload_templates', False)
    autoescape = settings.get('jinja2.autoescape', True)
    extensions = settings.get('jinja2.extensions', '')
    filters = settings.get('jinja2.filters', '')
    autoescape = asbool(autoescape)
    extensions = parse_extensions(extensions)
    filters = parse_filters(filters)
    environment = Environment(loader=directory_loader_factory(settings),
                              auto_reload=reload_templates,
                              autoescape=autoescape,
                              extensions=extensions)
    environment.filters.update(filters)
    registry.registerUtility(environment, IJinja2Environment)


def renderer_factory(info):
    environment = _get_or_build_default_environment(info.registry)
    return Jinja2TemplateRenderer(info, environment)


class Jinja2TemplateRenderer(object):
    '''Renderer for a jinja2 template'''
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


def _add_jinja2_search_path(config, searchpath):
    registry = config.registry
    env = _get_or_build_default_environment(registry)
    if isinstance(searchpath, basestring):
        searchpath = [x.strip() for x in searchpath.split('\n') if x.strip()]
    for d in searchpath:
        env.loader.searchpath.append(abspath_from_resource_spec(d))


def includeme(config):
    '''Setup standard configurator registrations.'''
    _get_or_build_default_environment(config.registry)
    config.add_renderer('.jinja2', renderer_factory)
    config.add_directive('add_jinja2_search_path', _add_jinja2_search_path)
