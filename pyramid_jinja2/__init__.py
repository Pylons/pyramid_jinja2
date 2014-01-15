import os
import sys

from jinja2 import Environment as _Jinja2Environment

from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader
from jinja2.utils import open_if_exists

from pyramid.asset import abspath_from_asset_spec

from zope.interface import Interface

from .compat import text_type
from .settings import (
    parse_env_options_from_settings,
    parse_loader_options_from_settings,
    parse_multiline,
)


ENV_CONFIG_PHASE = 0
EXTRAS_CONFIG_PHASE = 1


class IJinja2Environment(Interface):
    pass


class Environment(_Jinja2Environment):
    def join_path(self, template, parent):
        return os.path.join(os.path.dirname(parent), template)


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


class Jinja2TemplateRenderer(object):
    '''Renderer for a jinja2 template'''
    def __init__(self, template):
        self.template = template

    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            ex = sys.exc_info()[1]  # py2.5 - 3.2 compat
            raise ValueError('renderer was passed non-dictionary '
                             'as value: %s' % str(ex))
        return self.template.render(system)


class Jinja2RendererFactory(object):
    def __init__(self, environment):
        self.environment = environment

    def __call__(self, info):
        # get template based on searchpaths, then try relavtive one
        name = info.name
        name_with_package = None
        if ':' not in name and getattr(info, 'package', None) is not None:
            package = info.package
            name_with_package = '%s:%s' % (package.__name__, name)
        try:
            template = self.environment.get_template(name)
        except TemplateNotFound:
            if name_with_package is not None:
                template = self.environment.get_template(name_with_package)
            else:
                raise

        return Jinja2TemplateRenderer(template)


def add_jinja2_search_path(config, searchpath, renderer_extension='.jinja2'):
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
    def register():
        env = get_jinja2_environment(config, renderer_extension)
        searchpaths = parse_multiline(searchpath)
        for folder in searchpaths:
            env.loader.searchpath.append(abspath_from_asset_spec(folder,
                                         config.package_name))
    config.action(None, register, order=EXTRAS_CONFIG_PHASE)


def add_jinja2_extension(config, ext, renderer_extension='.jinja2'):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.add_jinja2_extension(myext)

    It will add the Jinja2 extension passed as ``ext`` to the current
    ``jinja2.environment.Environment`` used by :mod:`pyramid_jinja2`.
    """
    def register():
        env = get_jinja2_environment(config, renderer_extension)
        env.add_extension(ext)
    config.action(None, register, order=EXTRAS_CONFIG_PHASE)


def get_jinja2_environment(config, renderer_extension='.jinja2'):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.get_jinja2_environment()

    It will return the current ``jinja2.environment.Environment`` used by
    :mod:`pyramid_jinja2` or ``None`` if no environment has yet been set up.
    """
    registry = config.registry
    return registry.queryUtility(IJinja2Environment, name=renderer_extension)


def create_environment_from_options(env_opts, loader_opts):
    loader = SmartAssetSpecLoader(**loader_opts)

    newstyle = env_opts.pop('newstyle', False)
    gettext = env_opts.pop('gettext', None)
    package_name = env_opts.pop('package_name', None)
    filters = env_opts.pop('filters', {})
    tests = env_opts.pop('tests', {})
    globals = env_opts.pop('globals', {})

    env = Environment(
        loader=loader,
        **env_opts
    )

    if package_name is not None:
        env._default_package = package_name

    env.install_gettext_callables(
        gettext.gettext, gettext.ngettext, newstyle=newstyle)

    env.filters.update(filters)
    env.tests.update(tests)
    env.globals.update(globals)

    return env


def add_jinja2_renderer(config, extension, settings_prefix='jinja2.'):
    renderer_factory = Jinja2RendererFactory()
    config.add_renderer(extension, renderer_factory)

    def register():
        registry = config.registry
        settings = config.get_settings()

        loader_opts = parse_loader_options_from_settings(
            settings,
            settings_prefix,
            config.maybe_dotted,
            config.package,
        )
        env_opts = parse_env_options_from_settings(
            settings,
            settings_prefix,
            config.maybe_dotted,
            config.package,
        )
        env = create_environment_from_options(env_opts, loader_opts)

        registry.registerUtility(env, IJinja2Environment, name=extension)

    config.action(
        ('jinja2-renderer', extension), register, order=ENV_CONFIG_PHASE)


def includeme(config):
    """Set up standard configurator registrations.  Use via:

    .. code-block:: python

       config = Configurator()
       config.include('pyramid_jinja2')

    Once this function has been invoked, the ``.jinja2`` renderer is
    available for use in Pyramid and these new directives are available as
    methods of the configurator:

    - ``add_jinja2_renderer``: Add another Jinja2 renderer, with a different
      extension and/or settings.

    - ``add_jinja2_search_path``: Add a search path location to the search
      path.

    - ``add_jinja2_extension``: Add a list of extensions to the Jinja2
      environment.

    - ``get_jinja2_environment``: Return the Jinja2 ``environment.Environment``
      used by ``pyramid_jinja2``.

    """
    config.add_directive('add_jinja2_renderer', add_jinja2_renderer)
    config.add_directive('add_jinja2_search_path', add_jinja2_search_path)
    config.add_directive('add_jinja2_extension', add_jinja2_extension)
    config.add_directive('get_jinja2_environment', get_jinja2_environment)
    config.add_jinja2_renderer('.jinja2')
