## come on python gimme some of that sweet, sweet -*- coding: utf-8 -*-

import unittest
from pyramid import testing

from pyramid_jinja2.compat import (
    text_type,
    text_,
    bytes_,
    StringIO,
)
from .base import Base, Mock


def dummy_filter(value): return 'hoge'


class Test_renderer_factory(Base, unittest.TestCase):

    def setUp(self):
        Base.setUp(self)
        import warnings
        self.warnings = warnings.catch_warnings()
        self.warnings.__enter__()
        warnings.simplefilter('ignore', DeprecationWarning)

    def tearDown(self):
        self.warnings.__exit__(None, None, None)
        Base.tearDown(self)

    def _callFUT(self, info):
        from pyramid_jinja2 import renderer_factory
        return renderer_factory(info)

    def test_require_default_renderer(self):
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        self.assertRaises(ValueError, lambda: self._callFUT(info))

    def test_no_directories(self):
        from jinja2.exceptions import TemplateNotFound
        self.config.include('pyramid_jinja2')
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        renderer = self._callFUT(info)
        self.assertRaises(
            TemplateNotFound, lambda: renderer({}, {'system': 1}))

    def test_no_environment(self):
        self.config.registry.settings.update(
            {'jinja2.directories': self.templates_dir})
        self.config.include('pyramid_jinja2')
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        renderer = self._callFUT(info)
        environ = self.config.get_jinja2_environment()
        self.assertEqual(environ.loader.searchpath[0], self.templates_dir)
        self.assertTrue(renderer.template_loader is not None)

    def test_composite_directories_path(self):
        twice = self.templates_dir + '\n' + self.templates_dir
        self.config.registry.settings['jinja2.directories'] = twice
        self.config.include('pyramid_jinja2')
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        self._callFUT(info)
        environ = self.config.get_jinja2_environment()
        self.assertEqual(environ.loader.searchpath[:2],
                         [self.templates_dir] * 2)

    def test_with_environ(self):
        from pyramid_jinja2 import IJinja2Environment
        environ = DummyEnviron()
        self.config.registry.registerUtility(
            environ, IJinja2Environment, name='.jinja2')
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        renderer = self._callFUT(info)
        self.assertTrue(renderer.template_loader)

    def test_with_filters_object(self):
        self.config.registry.settings.update(
            {'jinja2.directories': self.templates_dir,
             'jinja2.filters': {'dummy': dummy_filter}})
        self.config.include('pyramid_jinja2')
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        self._callFUT(info)
        environ = self.config.get_jinja2_environment()
        self.assertEqual(environ.filters['dummy'], dummy_filter)

    def test_with_filters_string(self):
        m = 'pyramid_jinja2.tests.test_it'
        self.config.registry.settings.update(
            {'jinja2.directories': self.templates_dir,
             'jinja2.filters': 'dummy=%s:dummy_filter' % m})
        self.config.include('pyramid_jinja2')
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        self._callFUT(info)
        environ = self.config.get_jinja2_environment()
        self.assertEqual(environ.filters['dummy'], dummy_filter)


class TestJinja2TemplateRenderer(Base, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_jinja2 import Jinja2TemplateRenderer
        return Jinja2TemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_call(self):
        template = DummyTemplate()
        instance = self._makeOne(lambda: template)
        result = instance({}, {'system': 1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, 'result')

    def test_call_with_system_context(self):
        template = DummyTemplate()
        instance = self._makeOne(lambda: template)
        result = instance({}, {'context': 1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, 'result')

    def test_call_with_nondict_value(self):
        template = DummyTemplate()
        instance = self._makeOne(lambda: template)
        self.assertRaises(ValueError, instance, None, {'context': 1})


class SearchPathTests(object):
    def test_relative_tmpl_helloworld(self):
        from pyramid.renderers import render
        result = render('templates/helloworld.jinja2', {})
        self.assertEqual(result, text_('\nHello föö', 'utf-8'))

    def test_relative_tmpl_extends(self):
        from pyramid.renderers import render
        result = render('templates/extends.jinja2', {})
        self.assertEqual(result, text_('\nHello fööYo!', 'utf-8'))

    def test_relative_tmpl_extends_spec(self):
        from pyramid.renderers import render
        result = render('templates/extends_spec.jinja2', {'a': 1})
        self.assertEqual(result, text_('\nHello fööYo!', 'utf-8'))

    def test_asset_tmpl_helloworld(self):
        from pyramid.renderers import render
        result = render('pyramid_jinja2.tests:templates/helloworld.jinja2',
                        {'a': 1})
        self.assertEqual(result, text_('\nHello föö', 'utf-8'))

    def test_asset_tmpl_extends(self):
        from pyramid.renderers import render
        result = render('pyramid_jinja2.tests:templates/extends.jinja2',
                        {'a': 1})
        self.assertEqual(result, text_('\nHello fööYo!', 'utf-8'))

    def test_asset_tmpl_extends_spec(self):
        from pyramid.renderers import render
        result = render('pyramid_jinja2.tests:templates/extends_spec.jinja2',
                        {'a': 1})
        self.assertEqual(result, text_('\nHello fööYo!', 'utf-8'))

    def test_asset_tmpl_deep_sub_leaf(self):
        from pyramid.renderers import render
        result = render('pyramid_jinja2.tests:templates/deep/sub/leaf.jinja2', {})
        self.assertEqual(result, text_('deep-base sub-base sub-leaf', 'utf-8'))

    def test_asset_tmpl_deep_leaf(self):
        from pyramid.renderers import render
        result = render('pyramid_jinja2.tests:templates/deep/leaf.jinja2', {})
        self.assertEqual(
            result,
            text_('sub-nav\n\ndeep-formsdeep-base deep-leaf', 'utf-8'))

    def test_abs_tmpl_extends(self):
        import os.path
        from pyramid.renderers import render
        here = os.path.abspath(os.path.dirname(__file__))
        result = render(os.path.join(here, 'templates', 'extends.jinja2'),
                        {'a': 1})
        self.assertEqual(result, text_('\nHello fööYo!', 'utf-8'))

    def test_abs_tmpl_extends_missing(self):
        import os.path
        from jinja2 import TemplateNotFound
        from pyramid.renderers import render
        here = os.path.abspath(os.path.dirname(__file__))
        templates_dir = os.path.join(here, 'templates')
        self.assertRaises(
            TemplateNotFound,
            lambda: render(
                os.path.join(templates_dir, '/extends_missing.jinja2'), {}))


class TestIntegrationWithSearchPath(SearchPathTests, unittest.TestCase):
    def setUp(self):
        config = testing.setUp()
        config.add_settings({'jinja2.directories':
                             'pyramid_jinja2.tests:templates'})
        config.include('pyramid_jinja2')
        self.config = config

    def tearDown(self):
        testing.tearDown()

    def test_tmpl_helloworld(self):
        from pyramid.renderers import render
        result = render('helloworld.jinja2', {'a': 1})
        self.assertEqual(result, text_('\nHello föö', 'utf-8'))

    def test_tmpl_extends(self):
        from pyramid.renderers import render
        result = render('extends.jinja2', {'a': 1})
        self.assertEqual(result, text_('\nHello fööYo!', 'utf-8'))

    def test_tmpl_extends_spec(self):
        from pyramid.renderers import render
        result = render('extends_spec.jinja2', {'a': 1})
        self.assertEqual(result, text_('\nHello fööYo!', 'utf-8'))

    def test_tmpl_extends_relbase(self):
        from pyramid.renderers import render
        # this should pass as it will fallback to the new search path
        # and find it from there
        self.config.add_jinja2_search_path('pyramid_jinja2.tests:')
        result = render('extends_relbase.jinja2', {'a': 1})
        self.assertEqual(result, text_('\nHello fööYo!', 'utf-8'))

    def test_caller_relative_tmpl_extends_relbase(self):
        from pyramid.renderers import render
        # this should pass as it will fallback to the new search path
        # and find it from there
        self.config.add_jinja2_search_path('pyramid_jinja2.tests:')
        result = render('templates/extends_relbase.jinja2', {'a': 1})
        self.assertEqual(result, text_('\nHello fööYo!', 'utf-8'))

    def test_recursive_tmpl(self):
        from pyramid.renderers import render
        self.config.add_jinja2_renderer('.html')
        self.config.add_jinja2_search_path(
            'pyramid_jinja2.tests:templates/recursive', name='.html')
        result = render('admin/index.html', {})
        self.assertEqual(result, text_('foo'))


class TestIntegrationDefaultSearchPath(SearchPathTests, unittest.TestCase):
    def setUp(self):
        config = testing.setUp()
        config.include('pyramid_jinja2')

    def tearDown(self):
        testing.tearDown()


class TestIntegrationReloading(unittest.TestCase):
    def setUp(self):
        config = testing.setUp()
        config.add_settings({
            'pyramid.reload_templates': 'true',
        })
        config.include('pyramid_jinja2')
        self.config = config

    def tearDown(self):
        testing.tearDown()

    def test_render_reload_templates(self):
        import os, tempfile, time
        from webtest import TestApp

        fd, path = tempfile.mkstemp('.jinja2')
        try:
            with open(path, 'wb') as fp:
                fp.write(b'foo')

            self.config.add_view(lambda r: {}, renderer=path)
            app = TestApp(self.config.make_wsgi_app())

            result = app.get('/').body
            self.assertEqual(result, b'foo')

            time.sleep(1)  # need mtime to change and most systems
                           # have 1-second resolution
            with open(path, 'wb') as fp:
                fp.write(b'bar')

            result = app.get('/').body
            self.assertEqual(result, b'bar')
        finally:
            os.close(fd)
            os.unlink(path)


class Test_filters_and_tests(Base, unittest.TestCase):

    def _set_up_environ(self):
        self.config.include('pyramid_jinja2')
        return self.config.get_jinja2_environment()

    def _assert_has_test(self, test_name, test_obj):
        environ = self._set_up_environ()
        self.assertTrue(test_name in environ.tests)
        self.assertEqual(environ.tests[test_name], test_obj)

    def _assert_has_filter(self, filter_name, filter_obj):
        environ = self._set_up_environ()
        self.assertTrue(filter_name in environ.filters)
        self.assertEqual(environ.filters[filter_name], filter_obj)

    def _assert_has_global(self, global_name, global_obj):
        environ = self._set_up_environ()
        self.assertTrue(global_name in environ.globals)
        self.assertEqual(environ.globals[global_name], global_obj)

    def test_set_single_filter(self):
        self.config.registry.settings['jinja2.filters'] = \
                'my_filter = pyramid_jinja2.tests.test_it.my_test_func'
        self._assert_has_filter('my_filter', my_test_func)

    def test_set_single_test(self):
        self.config.registry.settings['jinja2.tests'] = \
                'my_test = pyramid_jinja2.tests.test_it.my_test_func'
        self._assert_has_test('my_test', my_test_func)

    def test_set_single_global(self):
        self.config.registry.settings['jinja2.globals'] = \
                'my_test = pyramid_jinja2.tests.test_it.my_test_func'
        self._assert_has_global('my_test', my_test_func)

    def test_set_multi_filters(self):
        self.config.registry.settings['jinja2.filters'] = \
                'my_filter1 = pyramid_jinja2.tests.test_it.my_test_func\n' \
                'my_filter2 = pyramid_jinja2.tests.test_it.my_test_func\n' \
                'my_filter3 = pyramid_jinja2.tests.test_it.my_test_func'
        self._assert_has_filter('my_filter1', my_test_func)
        self._assert_has_filter('my_filter2', my_test_func)
        self._assert_has_filter('my_filter3', my_test_func)

    def test_set_multi_tests(self):
        self.config.registry.settings['jinja2.tests'] = \
                'my_test1 = pyramid_jinja2.tests.test_it.my_test_func\n' \
                'my_test2 = pyramid_jinja2.tests.test_it.my_test_func\n' \
                'my_test3 = pyramid_jinja2.tests.test_it.my_test_func'
        self._assert_has_test('my_test1', my_test_func)
        self._assert_has_test('my_test2', my_test_func)
        self._assert_has_test('my_test3', my_test_func)

    def test_set_multi_globals(self):
        self.config.registry.settings['jinja2.globals'] = \
                'my_global1 = pyramid_jinja2.tests.test_it.my_test_func\n' \
                'my_global2 = pyramid_jinja2.tests.test_it.my_test_func\n' \
                'my_global3 = pyramid_jinja2.tests.test_it.my_test_func'
        self._assert_has_global('my_global1', my_test_func)
        self._assert_has_global('my_global2', my_test_func)
        self._assert_has_global('my_global3', my_test_func)

    def test_filter_and_test_and_global_works_in_render(self):
        from pyramid.renderers import render
        config = testing.setUp()
        config.include('pyramid_jinja2')
        config.add_settings({
            'jinja2.directories': 'pyramid_jinja2.tests:templates',
            'jinja2.tests': 'my_test = pyramid_jinja2.tests.test_it.my_test_func',
            'jinja2.filters': 'my_filter = pyramid_jinja2.tests.test_it.my_test_func',
            'jinja2.globals': 'my_global = pyramid_jinja2.tests.test_it.my_test_func'
        })
        config.add_jinja2_renderer('.jinja2')
        result = render('tests_and_filters.jinja2', {})
        #my_test_func returs "True" - it will be render as True when usign
        # as filter and will pass in tests
        self.assertEqual(result, text_('True is not False True', 'utf-8'))
        testing.tearDown()


class Test_includeme(unittest.TestCase):
    def test_it(self):
        from pyramid.interfaces import IRendererFactory
        from pyramid_jinja2 import includeme
        from pyramid_jinja2 import Jinja2RendererFactory
        config = testing.setUp()
        config.registry.settings['jinja2.directories'] = '/foobar'
        includeme(config)
        utility = config.registry.getUtility(IRendererFactory, name='.jinja2')
        self.assertTrue(isinstance(utility, Jinja2RendererFactory))


class Test_add_jinja2_searchpath(unittest.TestCase):
    def test_it_relative_to_package(self):
        import pyramid_jinja2.tests
        from pyramid_jinja2 import includeme
        import os
        config = testing.setUp()
        # hack because pyramid pre 1.6 doesn't configure testing configurator
        # with the correct package name
        config.package = pyramid_jinja2.tests
        config.package_name = 'pyramid_jinja2.tests'
        config.add_settings({'jinja2.directories': 'foobar'})
        includeme(config)
        env = config.get_jinja2_environment()
        self.assertEqual(len(env.loader.searchpath), 2)
        self.assertEqual(
            [x.split(os.sep)[-3:] for x in env.loader.searchpath][0],
            ['pyramid_jinja2', 'tests', 'foobar'])
        self.assertEqual(
            [x.split(os.sep)[-2:] for x in env.loader.searchpath][1],
            ['pyramid_jinja2', 'tests'])

        config.add_jinja2_search_path('grrr', prepend=True)
        self.assertEqual(len(env.loader.searchpath), 3)
        self.assertEqual(
            [x.split(os.sep)[-3:] for x in env.loader.searchpath][0],
            ['pyramid_jinja2', 'tests', 'grrr'])
        self.assertEqual(
            [x.split(os.sep)[-3:] for x in env.loader.searchpath][1],
            ['pyramid_jinja2', 'tests', 'foobar'])
        self.assertEqual(
            [x.split(os.sep)[-2:] for x in env.loader.searchpath][2],
            ['pyramid_jinja2', 'tests'])


class Test_get_jinja2_environment(unittest.TestCase):
    def test_it(self):
        from pyramid_jinja2 import includeme, Environment
        config = testing.setUp()
        includeme(config)
        self.assertEqual(config.get_jinja2_environment().__class__,
                         Environment)


class Test_bytecode_caching(unittest.TestCase):
    def test_default(self):
        from pyramid_jinja2 import includeme
        config = testing.setUp()
        config.registry.settings = {}
        includeme(config)
        env = config.get_jinja2_environment()
        self.assertTrue(env.bytecode_cache is None)
        self.assertFalse(env.auto_reload)

    def test_default_bccache(self):
        from pyramid_jinja2 import includeme
        import jinja2.bccache
        config = testing.setUp()
        config.registry.settings = {'jinja2.bytecode_caching': 'true'}
        includeme(config)
        env = config.get_jinja2_environment()
        self.assertTrue(isinstance(env.bytecode_cache,
                                   jinja2.bccache.FileSystemBytecodeCache))
        self.assertTrue(env.bytecode_cache.directory)
        self.assertFalse(env.auto_reload)

    def test_directory(self):
        import tempfile
        from pyramid_jinja2 import includeme
        tmpdir = tempfile.mkdtemp()
        config = testing.setUp()
        config.registry.settings['jinja2.bytecode_caching'] = '1'
        config.registry.settings['jinja2.bytecode_caching_directory'] = tmpdir
        includeme(config)
        env = config.get_jinja2_environment()
        self.assertEqual(env.bytecode_cache.directory, tmpdir)
        # TODO: test tmpdir is deleted when interpreter exits

    def test_bccache_instance(self):
        from pyramid_jinja2 import includeme
        import jinja2.bccache
        mycache = jinja2.bccache.MemcachedBytecodeCache(DummyMemcachedClient())
        config = testing.setUp()
        config.registry.settings = {'jinja2.bytecode_caching': mycache}
        includeme(config)
        env = config.get_jinja2_environment()
        self.assertTrue(env.bytecode_cache is mycache)
        self.assertFalse(env.auto_reload)

    def test_pyramid_reload_templates(self):
        from pyramid_jinja2 import includeme
        config = testing.setUp()
        config.registry.settings = {}
        config.registry.settings['pyramid.reload_templates'] = 'true'
        includeme(config)
        env = config.get_jinja2_environment()
        self.assertTrue(env.auto_reload)


class TestSmartAssetSpecLoader(unittest.TestCase):

    def _makeOne(self, **kw):
        from pyramid_jinja2 import SmartAssetSpecLoader
        return SmartAssetSpecLoader(**kw)

    def test_list_templates(self):
        loader = self._makeOne()
        self.assertRaises(TypeError, loader.list_templates)

    def test_get_source_invalid_spec(self):
        from jinja2.exceptions import TemplateNotFound
        loader = self._makeOne()
        self.assertRaises(TemplateNotFound,
                          loader.get_source, None, 'asset:foobar.jinja2')

    def test_get_source_spec(self):
        loader = self._makeOne()
        asset = 'pyramid_jinja2.tests:templates/helloworld.jinja2'
        self.assertNotEqual(loader.get_source(None, asset), None)

    def test_get_source_legacy_spec(self):
        loader = self._makeOne()
        # make sure legacy prefixed asset spec based loading works
        asset = 'asset:pyramid_jinja2.tests:templates/helloworld.jinja2'
        self.assertNotEqual(loader.get_source(None, asset), None)

    def test_get_source_from_path(self):
        import os.path
        here = os.path.abspath(os.path.dirname(__file__))
        loader = self._makeOne(searchpath=[here])
        asset = 'templates/helloworld.jinja2'
        self.assertNotEqual(loader.get_source(None, asset), None)


class TestFileInfo(unittest.TestCase):

    def test_mtime(self):
        from pyramid_jinja2 import FileInfo
        from pyramid.asset import abspath_from_asset_spec

        filename = abspath_from_asset_spec('templates/helloworld.jinja2',
                                           'pyramid_jinja2.tests')

        fi = FileInfo(filename)
        assert '_mtime' not in fi.__dict__
        assert fi.mtime is not None
        assert fi.mtime == fi._mtime

    def test_uptodate(self):
        from pyramid_jinja2 import FileInfo
        fi = FileInfo('foobar')
        assert fi.uptodate() is False

    def test_notfound(self):
        from jinja2 import TemplateNotFound
        from pyramid_jinja2 import FileInfo
        fi = FileInfo('foobar')
        self.assertRaises(TemplateNotFound, lambda: fi._delay_init())

    def test_delay_init(self):
        from pyramid_jinja2 import FileInfo

        class MyFileInfo(FileInfo):
            filename = 'foo.jinja2'

            def __init__(self, data):
                self.data = data
                FileInfo.__init__(self, self.filename)

            def open_if_exists(self, fname):
                return StringIO(self.data)

            def getmtime(self, fname):
                return 1

        mi = MyFileInfo(text_('nothing good here, move along'))
        mi._delay_init()
        self.assertEqual(mi._contents, mi.data)


class TestJinja2SearchPathIntegration(unittest.TestCase):

    def test_it(self):
        from pyramid.config import Configurator
        from pyramid_jinja2 import includeme
        from webtest import TestApp
        import os

        here = os.path.abspath(os.path.dirname(__file__))
        templates_dir = os.path.join(here, 'templates')

        def myview(request):
            return {}

        config1 = Configurator(settings={
                'jinja2.directories': os.path.join(templates_dir, 'foo')})
        includeme(config1)
        config1.add_view(view=myview, renderer='mytemplate.jinja2')
        config2 = Configurator(settings={
                'jinja2.directories': os.path.join(templates_dir, 'bar')})
        includeme(config2)
        config2.add_view(view=myview, renderer='mytemplate.jinja2')
        self.assertNotEqual(config1.registry.settings,
                            config2.registry.settings)

        app1 = config1.make_wsgi_app()
        testapp = TestApp(app1)
        self.assertEqual(testapp.get('/').body, bytes_('foo'))

        app2 = config2.make_wsgi_app()
        testapp = TestApp(app2)
        self.assertEqual(testapp.get('/').body, bytes_('bar'))

    def test_it_relative_to_template(self):
        from pyramid.config import Configurator
        from pyramid_jinja2 import includeme
        from webtest import TestApp

        def myview(request):
            return {}

        config = Configurator(settings={'jinja2.directories': 'templates'})
        includeme(config)
        config.add_view(view=myview, name='baz1',
                        renderer='baz1/mytemplate.jinja2')
        config.add_view(view=myview, name='baz2',
                        renderer='baz2/mytemplate.jinja2')

        app1 = config.make_wsgi_app()
        testapp = TestApp(app1)
        self.assertEqual(testapp.get('/baz1').body, bytes_('baz1\nbaz1 body'))
        self.assertEqual(testapp.get('/baz2').body, bytes_('baz2\nbaz2 body'))


class TestPackageFinder(unittest.TestCase):

    def test_caller_package(self):
        from pyramid_jinja2 import _PackageFinder
        pf = _PackageFinder()

        class MockInspect(object):
            def __init__(self, items=()):
                self.items = items

            def stack(self):
                return self.items
        pf.inspect = MockInspect()
        self.assertEqual(pf.caller_package(), None)

        import xml
        pf.inspect.items = [(Mock(f_globals={'__name__': 'xml'}),)]


class TestNewstyle(unittest.TestCase):
    def test_it(self):
        from pyramid.config import Configurator
        from pyramid_jinja2 import includeme
        from webtest import TestApp
        import os

        here = os.path.abspath(os.path.dirname(__file__))
        templates_dir = os.path.join(here, 'templates')

        def myview(request):
            return {'what': 'eels'}

        config = Configurator(settings={
                'jinja2.directories': templates_dir,
                'jinja2.newstyle': True})
        includeme(config)
        config.add_view(view=myview, renderer='newstyle.jinja2')

        app = config.make_wsgi_app()
        testapp = TestApp(app)
        self.assertEqual(testapp.get('/').body.decode('utf-8'), text_('my hovercraft is full of eels!'))


class Test_add_jinja2_extension(Base, unittest.TestCase):

    def test_it(self):
        self.config.include('pyramid_jinja2')
        env_before = self.config.get_jinja2_environment()

        class MockExt(object):
            identifier = 'foobar'

            def __init__(self, x):
                self.x = x

        self.config.add_jinja2_extension(MockExt)

        env_after = self.config.get_jinja2_environment()
        self.assertTrue('foobar' in env_after.extensions)
        self.assertTrue(env_before is env_after)

    def test_alternate_renderer_extension(self):
        self.config.include('pyramid_jinja2')
        self.config.add_jinja2_renderer('.html')
        env_before = self.config.get_jinja2_environment('.html')

        class MockExt(object):
            identifier = 'foobar'

            def __init__(self, x):
                self.x = x

        self.config.add_jinja2_extension(MockExt, '.html')

        env_after = self.config.get_jinja2_environment('.html')
        default_env = self.config.get_jinja2_environment()

        self.assertTrue('foobar' in env_after.extensions)
        self.assertTrue('foobar' not in default_env.extensions)
        self.assertTrue(env_before is env_after)


def my_test_func(*args, **kwargs):
    """ Used as a fake filter/test function """
    return True

class DummyMemcachedClient(dict):
    """ A memcached client acceptable to jinja2.MemcachedBytecodeCache.
    """
    def set(self, key, value, timeout):
        self[key] = value               # pragma: no cover

class DummyEnviron(dict):
    def get_template(self, path):  # pragma: no cover
        return path

class DummyTemplate(object):
    def render(self, system):
        return b'result'.decode('utf-8')

class DummyRendererInfo(object):
    def __init__(self, kw):
        self.__dict__.update(kw)
        if 'registry' in self.__dict__:
            self.settings = self.registry.settings
