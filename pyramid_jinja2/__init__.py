import inspect
import os
import posixpath
import sys

from jinja2 import Environment as _Jinja2Environment

from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader
from jinja2.utils import open_if_exists

from pyramid.asset import abspath_from_asset_spec
from pyramid.path import DottedNameResolver

from zope.deprecation import deprecated
from zope.interface import Interface

from .compat import text_type
from .settings import (
    parse_env_options_from_settings,
    parse_loader_options_from_settings,
    parse_multiline,
)


ENV_CONFIG_PHASE = 0
EXTRAS_CONFIG_PHASE = 1
PARENT_RELATIVE_DELIM = '@@FROM_PARENT@@'


class IJinja2Environment(Interface):
    pass


class Environment(_Jinja2Environment):
    def join_path(self, uri, parent):
        if os.path.isabs(uri) or ':' in uri:
            # we have an asset spec or absolute path
            return uri

        # uri may be relative to the parent, shuffle it through to the loader
        return uri + PARENT_RELATIVE_DELIM + parent


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

    def caller_package(self, excludes=()):
        """A list of excluded patterns, optionally containing a `.` suffix.
        For example, ``'pyramid.'`` would exclude exclude ``'pyramid.config'``
        but not ``'pyramid'``.
        """
        f = None
        for t in self.inspect.stack():
            f = t[0]
            name = f.f_globals.get('__name__')
            if name:
                excluded = False
                for pattern in excludes:
                    if pattern[-1] == '.' and name.startswith(pattern):
                        excluded = True
                        break
                    elif name == pattern:
                        excluded = True
                        break
                if not excluded:
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

    def _get_absolute_source(self, template):
        filename = abspath_from_asset_spec(template)
        fi = FileInfo(filename, self.encoding)
        if os.path.isfile(fi.filename):
            return fi.contents, fi.filename, fi.uptodate

    def _relative_searchpath(self, chain):
        """ Combine paths in the chain to construct search paths.

        The precedence is for the most-specific paths to be tested first,
        anchored at an absolute path or asset spec. From there, less-specific
        paths are tested.

        For example::
            chain = [
                '../forms.jinja2', 'sub/nav.jinja2',
                'base.jinja2', 'myapp:templates/index.jinja2',
            ]
            searchpath = ['myapp:templates/sub/..', 'sub/..', '..', '']
        """
        # the initial empty string is important because not only does it allow
        # the stack to always contain something join, but it allows the
        # later for-loops to fallback to the original search path by
        # joining to an empty string since os.path.join('', 'foo') == 'foo'
        stack = ['']
        for path in chain:
            is_abspath = os.path.isabs(path)
            is_spec = not is_abspath and ':' in path

            if not is_abspath and is_spec:
                ppkg, ppath = path.split(':', 1)
                path = '{0}:{1}'.format(ppkg, posixpath.dirname(ppath))
            else:
                # this should split windows and posix paths
                path = os.path.dirname(path)

            if not path:
                # skip empty directories
                continue

            subpath = stack[-1]
            path = posixpath.join(path, subpath)
            stack.append(path)

            # do not continue further, all paths are relative to this
            if is_abspath or is_spec:
                break
        return list(reversed(stack))

    def get_source(self, environment, template):
        # keep legacy asset: prefix checking that bypasses
        # source path checking altogether
        if template.startswith('asset:'):
            template = template[6:]

        # split the template into the chain of relative-imports
        rel_chain = template.split(PARENT_RELATIVE_DELIM)
        template, rel_chain = rel_chain[0], rel_chain[1:]

        # load the template directly if it's an absolute path or asset spec
        if os.path.isabs(template) or ':' in template:
            src = self._get_absolute_source(template)
            if src is not None:
                return src
            else:
                # fallback to the search path just incase
                return FileSystemLoader.get_source(self, environment, template)

        # try to import the template as an asset spec or absolute path
        # relative to its parents
        rel_searchpath = self._relative_searchpath(rel_chain)
        for parent in rel_searchpath:
            if os.path.isabs(parent):
                uri = os.path.join(parent, template)
                # avoid recursive includes
                if uri not in rel_chain:
                    src = self._get_absolute_source(uri)
                    if src is not None:
                        return src
            # avoid doing "':' in" and then redundant "split"
            parts = parent.split(':', 1)
            if len(parts) > 1:
                # parent is an asset spec
                ppkg, ppath = parts
                ppath = posixpath.join(ppath, template)
                uri = '{0}:{1}'.format(ppkg, ppath)
                # avoid recursive includes
                if uri not in rel_chain:
                    src = self._get_absolute_source(uri)
                    if src is not None:
                        return src

        # try to load the template from the default search path
        for parent in rel_searchpath:
            try:
                uri = os.path.join(parent, template)
                # avoid recursive includes
                if uri not in rel_chain:
                    return FileSystemLoader.get_source(self, environment, uri)
            except TemplateNotFound:
                pass

        # we're here because of an exception during the last step so extend
        # the message and raise an appropriate error
        # there should always be an exception because the rel_searchpath is
        # guaranteed to contain at least one element ('')
        searchpath = [p for p in rel_searchpath if p] + self.searchpath
        message = '{0}; searchpath={1}'.format(template, searchpath)
        raise TemplateNotFound(name=template, message=message)


class Jinja2TemplateRenderer(object):
    '''Renderer for a jinja2 template'''
    def __init__(self, template_loader):
        self.template_loader = template_loader

    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError) as ex:
            raise ValueError('renderer was passed non-dictionary '
                             'as value: %s' % str(ex))
        template = self.template_loader()
        return template.render(system)


class Jinja2RendererFactory(object):
    environment = None

    def __call__(self, info):
        name, package = info.name, info.package

        def template_loader():
            # attempt to turn the name into a caller-relative asset spec
            if ':' not in name and package is not None:
                try:
                    name_with_package = '%s:%s' % (package.__name__, name)
                    return self.environment.get_template(name_with_package)
                except TemplateNotFound:
                    pass

            return self.environment.get_template(name)

        return Jinja2TemplateRenderer(template_loader)


def renderer_factory(info):
    registry = info.registry
    env = registry.queryUtility(IJinja2Environment, name='.jinja2')
    if env is None:
        raise ValueError(
            'As of pyramid_jinja2 2.3, the use of the '
            '"pyramid_jinja2.renderer_factory" requires that pyramid_jinja2 '
            'be configured via config.include("pyramid_jinja2") or the '
            'equivalent "pyramid.includes" setting.')
    factory = Jinja2RendererFactory()
    factory.environment = env
    return factory(info)


deprecated(
    'renderer_factory',
    'The pyramid_jinja2.renderer_factory was deprecated in version 2.0 and '
    'will be removed in the future. You should upgrade to the newer '
    'config.add_jinja2_renderer() API.')


def add_jinja2_search_path(config, searchpath, name='.jinja2', prepend=False):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.add_jinja2_search_path('anotherpackage:templates/')

    It will add the directory or :term:`asset specification` passed as
    ``searchpath`` to the current search path of the
    :class:`jinja2.Environment` used by the renderer identified by ``name``.

    By default the path is appended to the end of the search path. If
    ``prepend`` is set to ``True`` then the path will be inserted at the start
    of the search path.

    """
    def register():
        env = get_jinja2_environment(config, name)
        searchpaths = parse_multiline(searchpath)
        for folder in searchpaths:
            path = abspath_from_asset_spec(folder, config.package)
            if prepend:
                env.loader.searchpath.insert(0, path)
            else:
                env.loader.searchpath.append(path)
    config.action(None, register, order=EXTRAS_CONFIG_PHASE)


def add_jinja2_extension(config, ext, name='.jinja2'):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.add_jinja2_extension(myext)

    It will add the Jinja2 extension passed as ``ext`` to the current
    :class:`jinja2.Environment` used by the renderer named ``name``.

    """
    ext = config.maybe_dotted(ext)
    def register():
        env = get_jinja2_environment(config, name)
        env.add_extension(ext)
    config.action(None, register, order=EXTRAS_CONFIG_PHASE)


def get_jinja2_environment(config, name='.jinja2'):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.get_jinja2_environment()

    It will return the configured ``jinja2.Environment`` for the
    renderer named ``name``. Configuration is delayed until a call to
    ``config.commit()`` or ``config.make_wsgi_app()``. As such, if this
    method is called prior to committing the changes, it may return ``None``.

    """
    registry = config.registry
    return registry.queryUtility(IJinja2Environment, name=name)


def create_environment_from_options(env_opts, loader_opts):
    loader = SmartAssetSpecLoader(**loader_opts)

    newstyle = env_opts.pop('newstyle', False)
    gettext = env_opts.pop('gettext', None)
    filters = env_opts.pop('filters', {})
    tests = env_opts.pop('tests', {})
    globals = env_opts.pop('globals', {})

    env = Environment(
        loader=loader,
        **env_opts
    )

    env.install_gettext_callables(
        gettext.gettext, gettext.ngettext, newstyle=newstyle)

    env.filters.update(filters)
    env.tests.update(tests)
    env.globals.update(globals)

    return env


def add_jinja2_renderer(config, name, settings_prefix='jinja2.', package=None):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.add_jinja2_renderer('.html', settings_prefix='jinja2.')

    It will register a new renderer, loaded from settings at the specified
    ``settings_prefix`` prefix. This renderer will be active for files using
    the specified extension ``name``.

    """
    renderer_factory = Jinja2RendererFactory()
    config.add_renderer(name, renderer_factory)

    package = package or config.package
    resolver = DottedNameResolver(package=package)

    def register():
        registry = config.registry
        settings = config.get_settings()

        loader_opts = parse_loader_options_from_settings(
            settings,
            settings_prefix,
            resolver.maybe_resolve,
            package,
        )
        env_opts = parse_env_options_from_settings(
            settings,
            settings_prefix,
            resolver.maybe_resolve,
            package,
        )
        env = create_environment_from_options(env_opts, loader_opts)
        renderer_factory.environment = env

        registry.registerUtility(env, IJinja2Environment, name=name)

    config.action(
        ('jinja2-renderer', name), register, order=ENV_CONFIG_PHASE)


def includeme(config):
    """Set up standard configurator registrations.  Use via:

    .. code-block:: python

       config = Configurator()
       config.include('pyramid_jinja2')

    Once this function has been invoked, the ``.jinja2`` renderer is
    available for use in Pyramid and these new directives are available as
    methods of the configurator:

    - ``add_jinja2_renderer``: Add a new Jinja2 renderer, with a different
      file extension and/or settings.

    - ``add_jinja2_search_path``: Add a new location to the search path
      for the specified renderer.

    - ``add_jinja2_extension``: Add a list of extensions to the Jinja2
      environment used by the specified renderer.

    - ``get_jinja2_environment``: Return the :class:`jinja2.Environment`
      used by the specified renderer.

    """
    config.add_directive('add_jinja2_renderer', add_jinja2_renderer)
    config.add_directive('add_jinja2_search_path', add_jinja2_search_path)
    config.add_directive('add_jinja2_extension', add_jinja2_extension)
    config.add_directive('get_jinja2_environment', get_jinja2_environment)

    package = _caller_package(('pyramid', 'pyramid.', 'pyramid_jinja2'))
    config.add_jinja2_renderer('.jinja2', package=package)

    # always insert default search path relative to package
    default_search_path = '%s:' % (package.__name__,)
    config.add_jinja2_search_path(default_search_path, name='.jinja2')
