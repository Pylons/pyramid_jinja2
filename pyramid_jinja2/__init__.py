import atexit
import inspect
import os
import sys
import warnings

from zope.interface import implementer
from zope.interface import Interface

from jinja2 import Environment
from jinja2 import BytecodeCache
from jinja2 import FileSystemBytecodeCache
from jinja2 import Undefined
from jinja2 import StrictUndefined
from jinja2 import DebugUndefined

from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader
from jinja2.utils import import_string
from jinja2.utils import open_if_exists

from pyramid_jinja2.compat import string_types
from pyramid_jinja2.compat import text_type

from pyramid.asset import abspath_from_asset_spec
from pyramid.resource import abspath_from_resource_spec
from pyramid.settings import asbool
from pyramid import i18n
from pyramid.threadlocal import get_current_request


class IJinja2Environment(Interface):
    pass


# defaults we want to override
_JINJA2_ENVIRONMENT_DEFAULTS = {
    'autoescape': True
}


def maybe_import_string(val):
    if isinstance(val, string_types):
        return import_string(val.strip())
    return val


def splitlines(s):
    return filter(None, [x.strip() for x in s.splitlines()])


def parse_config(config):
    """
    Parses config values from .ini file and returns a dictionary with
    imported objects
    """
    # input must be a string or dict
    result = {}
    if isinstance(config, string_types):
        for f in splitlines(config):
            name, impl = f.split('=', 1)
            result[name.strip()] = maybe_import_string(impl)
    else:
        for name, impl in config.items():
            result[name] = maybe_import_string(impl)
    return result


def parse_multiline(extensions):
    if isinstance(extensions, string_types):
        extensions = splitlines(extensions)
    return list(extensions)  # py3


def parse_undefined(undefined):
    if undefined == 'strict':
        return StrictUndefined
    if undefined == 'debug':
        return DebugUndefined
    return Undefined


class FileInfo(object):
    open_if_exists = staticmethod(open_if_exists)
    getmtime = staticmethod(os.path.getmtime)

    def __init__(self, filename, encoding='utf-8'):
        self.filename = filename
        self.encoding = encoding

    def _delay_init(self):
        if '_mtime' in self.__dict__:
            return

        f = self.open_if_exists(self.filename)
        if f is None:
            raise TemplateNotFound(self.filename)
        self._mtime = self.getmtime(self.filename)

        data = ''
        try:
            data = f.read()
        finally:
            f.close()

        if not isinstance(data, text_type):
            data = data.decode(self.encoding)
        self._contents = data

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


class _PackageFinder(object):
    inspect = staticmethod(inspect)

    def caller_package(self, allowed=()):
        f = None
        for t in self.inspect.stack():
            f = t[0]
            if f.f_globals.get('__name__') not in allowed:
                break

        if f is None:
            return None

        pname = f.f_globals.get('__name__') or '__main__'
        m = sys.modules[pname]
        f = getattr(m, '__file__', '')
        if (('__init__.py' in f) or ('__init__$py' in f)):  # empty at >>>
            return m

        pname = m.__name__.rsplit('.', 1)[0]

        return sys.modules[pname]

_caller_package = _PackageFinder().caller_package


class SmartAssetSpecLoader(FileSystemLoader):
    '''A Jinja2 template loader that knows how to handle
    asset specifications.
    '''

    def __init__(self, searchpath=(), encoding='utf-8', debug=False):
        FileSystemLoader.__init__(self, searchpath, encoding)
        self.debug = debug

    def list_templates(self):
        raise TypeError('this loader cannot iterate over all templates')

    def _get_asset_source_fileinfo(self, environment, template):
        if getattr(environment, '_default_package', None) is not None:
            pname = environment._default_package
            filename = abspath_from_asset_spec(template, pname)
        else:
            filename = abspath_from_asset_spec(template)
        fileinfo = FileInfo(filename, self.encoding)
        return fileinfo

    def get_source(self, environment, template):
        # keep legacy asset: prefix checking that bypasses
        # source path checking altogether
        if template.startswith('asset:'):
            newtemplate = template.split(':', 1)[1]
            fi = self._get_asset_source_fileinfo(environment, newtemplate)
            return fi.contents, fi.filename, fi.uptodate

        fi = self._get_asset_source_fileinfo(environment, template)
        if os.path.isfile(fi.filename):
            return fi.contents, fi.filename, fi.uptodate

        try:
            return FileSystemLoader.get_source(self, environment, template)
        except TemplateNotFound:
            ex = sys.exc_info()[1]  # py2.5-3.2 compat
            message = ex.message
            message += ('; asset=%s; searchpath=%r'
                        % (fi.filename, self.searchpath))
            raise TemplateNotFound(name=ex.name, message=message)


def _parse_config_for_settings(settings):
    """
    Generate a dictionary with Jinja2 settings parsed from the config,
    settings.

    :param settings: configurator registry settings.
    :type settings: dict

    :return: dictionary to passed into Jinja2 Environment object
    :rtype: dict
    """

    environ_args = {}
    defaults = _JINJA2_ENVIRONMENT_DEFAULTS

    # set up the keys with the defaults
    # this ensures that the defaults are still setup if they are not
    # specified in the config
    environ_args = defaults.copy()

    # set string settings
    for short_key_name in ('block_start_string', 'block_end_string',
                           'variable_start_string', 'variable_end_string',
                           'comment_start_string', 'comment_end_string',
                           'line_statement_prefix', 'line_comment_prefix',
                           'newline_sequence'):
        key_name = 'jinja2.%s' % (short_key_name,)
        if key_name in settings:
            environ_args[short_key_name] = \
                settings.get(key_name, defaults.get(key_name))

    # boolean settings
    for short_key_name in ('autoescape', 'trim_blocks', 'optimized'):
        key_name = 'jinja2.%s' % (short_key_name,)
        if key_name in settings:
            environ_args[short_key_name] = \
                asbool(settings.get(key_name, defaults.get(key_name)))

    # integer settings
    for short_key_name in ('cache_size',):
        key_name = 'jinja2.%s' % (short_key_name,)
        if key_name in settings:
            environ_args[short_key_name] = \
                int(settings.get(key_name, defaults.get(key_name)))

    return environ_args


def _get_or_build_default_environment(registry):
    environment = registry.queryUtility(IJinja2Environment)
    if environment is not None:
        return environment

    settings = registry.settings
    kw = {}

    package = _caller_package(('pyramid_jinja2', 'jinja2', 'pyramid.config'))
    debug = asbool(settings.get('debug_templates', False))

    # get basic environment jinja2 settings
    kw.update(_parse_config_for_settings(settings))
    reload_templates = settings.get('reload_templates', None)
    if reload_templates is None:
        # since version 1.5, both settings are supported
        reload_templates = settings.get('pyramid.reload_templates', False)
    reload_templates = asbool(reload_templates)
    undefined = parse_undefined(settings.get('jinja2.undefined', ''))

    # get supplementary jinja2 settings
    input_encoding = settings.get('jinja2.input_encoding', 'utf-8')
    domain = settings.get('jinja2.i18n.domain', package and package.__name__ or 'messages')

    # get jinja2 extensions
    extensions = parse_multiline(settings.get('jinja2.extensions', ''))
    if 'jinja2.ext.i18n' not in extensions:
        extensions.append('jinja2.ext.i18n')

    # get jinja2 directories
    directories = parse_multiline(settings.get('jinja2.directories') or '')
    directories = [abspath_from_resource_spec(d, package) for d in directories]
    loader = SmartAssetSpecLoader(
        directories,
        encoding=input_encoding,
        debug=debug)

    # get jinja2 bytecode caching settings and set up bytecaching
    bytecode_caching = settings.get('jinja2.bytecode_caching', False)
    if isinstance(bytecode_caching, BytecodeCache):
        kw['bytecode_cache'] = bytecode_caching
    elif asbool(bytecode_caching):
        bytecode_caching_directory = \
            settings.get('jinja2.bytecode_caching_directory', None)
        kw['bytecode_cache'] = \
            FileSystemBytecodeCache(bytecode_caching_directory)

    # should newstyle gettext calls be enabled?
    newstyle = asbool(settings.get('jinja2.newstyle', False))

    environment = Environment(loader=loader,
                              auto_reload=reload_templates,
                              extensions=extensions,
                              undefined=undefined,
                              **kw)

    # register pyramid i18n functions
    wrapper = GetTextWrapper(domain=domain)
    environment.install_gettext_callables(wrapper.gettext, wrapper.ngettext, newstyle=newstyle)

    # register global repository for templates
    if package is not None:
        environment._default_package = package.__name__

    #add custom jinja2 filters
    filters = parse_config(settings.get('jinja2.filters', ''))
    environment.filters.update(filters)

    #add custom jinja2 tests
    tests = parse_config(settings.get('jinja2.tests', ''))
    environment.tests.update(tests)

    # add custom jinja2 functions
    jinja_globals = parse_config(settings.get('jinja2.globals', ''))
    environment.globals.update(jinja_globals)

    registry.registerUtility(environment, IJinja2Environment)
    return registry.queryUtility(IJinja2Environment)


class GetTextWrapper(object):

    def __init__(self, domain):
        self.domain = domain

    @property
    def localizer(self):
        return i18n.get_localizer(get_current_request())

    def gettext(self, message):
        return self.localizer.translate(message,
                                        domain=self.domain)

    def ngettext(self, singular, plural, n):
        return self.localizer.pluralize(singular, plural, n,
                                        domain=self.domain)


class Jinja2TemplateRenderer(object):
    '''Renderer for a jinja2 template'''
    template = None

    def __init__(self, info, environment):
        self.info = info
        self.environment = environment

    def implementation(self):
        return self.template

    @property
    def template(self):
        # get template based on searchpaths, then try relavtive one
        info = self.info
        name = info.name
        name_with_package = None
        if ':' not in name and getattr(info, 'package', None) is not None:
            package = self.info.package
            name_with_package = '%s:%s' % (package.__name__, name)
        try:
            return self.environment.get_template(name)
        except TemplateNotFound:
            if name_with_package is not None:
                return self.environment.get_template(name_with_package)
            else:
                raise

    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            ex = sys.exc_info()[1]  # py2.5 - 3.2 compat
            raise ValueError('renderer was passed non-dictionary '
                             'as value: %s' % str(ex))
        return self.template.render(system)


def renderer_factory(info):
    environment = _get_or_build_default_environment(info.registry)
    return Jinja2TemplateRenderer(info, environment)


def add_jinja2_search_path(config, searchpath):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.add_jinja2_search_path('anotherpackage:templates/')

    It will add the directory or :term:`asset spec` passed as ``searchpath``
    to the current search path of the ``jinja2.environment.Environment`` used
    by :mod:`pyramid_jinja2`.
    """
    registry = config.registry
    env = _get_or_build_default_environment(registry)
    searchpath = parse_multiline(searchpath)

    for folder in searchpath:
        env.loader.searchpath.append(abspath_from_resource_spec(folder,
                                     config.package_name))


def add_jinja2_extension(config, ext):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.add_jinja2_extension(myext)

    It will add the Jinja2 extension passed as ``ext`` to the current
    ``jinja2.environment.Environment`` used by :mod:`pyramid_jinja2`.
    """
    env = _get_or_build_default_environment(config.registry)
    env.add_extension(ext)


def get_jinja2_environment(config):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.get_jinja2_environment()

    It will return the current ``jinja2.environment.Environment`` used by
    :mod:`pyramid_jinja2` or ``None`` if no environment has yet been set up.
    """
    return config.registry.queryUtility(IJinja2Environment)


def includeme(config):
    """Set up standard configurator registrations.  Use via:

    .. code-block:: python

       config = Configurator()
       config.include('pyramid_jinja2')

    Once this function has been invoked, the ``.jinja2`` renderer is
    available for use in Pyramid and these new directives are available as
    methods of the configurator:

    - ``add_jinja2_search_path``: Add a search path location to the search
      path.

    - ``add_jinja2_extension``: Add a list of extensions to the Jinja2
      environment.

    - get_jinja2_environment``: Return the Jinja2 ``environment.Environment``
      used by ``pyramid_jinja2``.

    """
    config.add_renderer('.jinja2', renderer_factory)
    config.add_directive('add_jinja2_search_path', add_jinja2_search_path)
    config.add_directive('add_jinja2_extension', add_jinja2_extension)
    config.add_directive('get_jinja2_environment', get_jinja2_environment)
    _get_or_build_default_environment(config.registry)
