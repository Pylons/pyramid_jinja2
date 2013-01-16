## come on python gimme some of that sweet, sweet -*- coding: utf-8 -*-

import unittest
from pyramid import testing
from pyramid_jinja2.tests.base import (
    Base, DummyRendererInfo, DummyEnvironment, Mock)

from pyramid_jinja2.compat import text_type
from pyramid_jinja2.compat import text_
from pyramid_jinja2.compat import bytes_
from pyramid_jinja2.compat import StringIO
from pyramid_jinja2.compat import PY3

def dummy_filter(value): return 'hoge'


class Test_parse_config(unittest.TestCase):
    def _callFUT(self, value):
        from pyramid_jinja2 import parse_config
        return parse_config(value)

    def test_parse_singile_line(self):
        import pyramid_jinja2
        self.assertEqual(self._callFUT('dummy=pyramid_jinja2'),
                         {'dummy': pyramid_jinja2})

    def test_parse_multi_line(self):
        import pyramid_jinja2
        self.assertEqual(self._callFUT("""
            dummy = pyramid_jinja2
            dummy2 = pyramid_jinja2"""),
        {'dummy': pyramid_jinja2, 'dummy2': pyramid_jinja2})

    def test_parse_dict_stringvals(self):
        import pyramid_jinja2
        self.assertEqual(self._callFUT(
            {'dummy': 'pyramid_jinja2',
             'dummy2': 'pyramid_jinja2'}),
        {'dummy': pyramid_jinja2, 'dummy2': pyramid_jinja2})

    def test_parse_dict_objvals(self):
        import pyramid_jinja2
        self.assertEqual(self._callFUT(
            {'dummy': pyramid_jinja2,
             'dummy2': pyramid_jinja2}),
        {'dummy': pyramid_jinja2, 'dummy2': pyramid_jinja2})


class Test_renderer_factory(Base, unittest.TestCase):
    def _callFUT(self, info):
        from pyramid_jinja2 import renderer_factory
        return renderer_factory(info)

    def test_no_directories(self):
        from jinja2.exceptions import TemplateNotFound
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        renderer = self._callFUT(info)
        self.assertRaises(TemplateNotFound, lambda: renderer({}, {}))

    def test_no_environment(self):
        from pyramid_jinja2 import IJinja2Environment
        self.config.registry.settings.update(
            {'jinja2.directories': self.templates_dir})
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        renderer = self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.loader.searchpath, [self.templates_dir])
        self.assertEqual(renderer.info, info)
        self.assertEqual(renderer.environment, environ)

    def test_composite_directories_path(self):
        from pyramid_jinja2 import IJinja2Environment
        twice = self.templates_dir + '\n' + self.templates_dir
        self.config.registry.settings['jinja2.directories'] = twice
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.loader.searchpath, [self.templates_dir] * 2)

    def test_with_environ(self):
        from pyramid_jinja2 import IJinja2Environment
        environ = dict()
        self.config.registry.registerUtility(environ, IJinja2Environment)
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        renderer = self._callFUT(info)
        self.assertEqual(renderer.environment, environ)
        self.assertEqual(renderer.info, info)

    def test_with_filters_object(self):
        from pyramid_jinja2 import IJinja2Environment

        self.config.registry.settings.update(
            {'jinja2.directories': self.templates_dir,
             'jinja2.filters': {'dummy': dummy_filter}})
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.filters['dummy'], dummy_filter)

    def test_with_filters_string(self):
        from pyramid_jinja2 import IJinja2Environment

        m = 'pyramid_jinja2.tests.test_it'
        self.config.registry.settings.update(
            {'jinja2.directories': self.templates_dir,
             'jinja2.filters': 'dummy=%s:dummy_filter' % m})
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.filters['dummy'], dummy_filter)


class Jinja2TemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_jinja2 import Jinja2TemplateRenderer
        return Jinja2TemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import ITemplateRenderer
        verifyObject(ITemplateRenderer, self._makeOne(None, None))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_call(self):
        environ = DummyEnvironment()
        info = DummyRendererInfo({
            'name': 'name',
            })
        instance = self._makeOne(info, environ)
        result = instance({}, {'system': 1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, 'result')

    def test_call_with_system_context(self):
        environ = DummyEnvironment()
        info = DummyRendererInfo({
            'name': 'name',
            })
        instance = self._makeOne(info, environ)
        result = instance({}, {'context': 1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, 'result')
        self.assertEqual(environ.values, {'context': 1})

    def test_call_with_nondict_value(self):
        environ = DummyEnvironment()
        info = DummyRendererInfo({
            'name': 'name',
            })
        instance = self._makeOne(info, environ)
        self.assertRaises(ValueError, instance, None, {'context': 1})

    def test_implementation(self):
        environ = DummyEnvironment()
        info = DummyRendererInfo({
            'name': 'name',
            })
        instance = self._makeOne(info, environ)
        result = instance.implementation().render({})
        self.assertEqual(result, 'result')


class TestIntegration(unittest.TestCase):
    def setUp(self):
        import pyramid_jinja2
        config = testing.setUp()
        config.add_settings({'jinja2.directories':
                             'pyramid_jinja2.tests:templates'})
        config.add_renderer('.jinja2',
                            pyramid_jinja2.renderer_factory)

    def tearDown(self):
        testing.tearDown()

    def test_render(self):
        from pyramid.renderers import render
        result = render('helloworld.jinja2', {'a': 1})
        self.assertEqual(result, text_('\nHello föö', 'utf-8'))


class TestIntegration2(unittest.TestCase):
    def setUp(self):
        import pyramid_jinja2
        config = testing.setUp()
        config.add_renderer('.jinja2',
                            pyramid_jinja2.renderer_factory)
    
    def tearDown(self):
        testing.tearDown()
    
    def test_render_relative_to_package(self):
        from pyramid.renderers import render
        result = render('templates/helloworld.jinja2', {'a': 1})
        self.assertEqual(result, text_('\nHello föö', 'utf-8'))


class Test_filters_and_tests(Base, unittest.TestCase):

    def _set_up_environ(self):
        from pyramid_jinja2 import IJinja2Environment
        self.config.include('pyramid_jinja2')
        return self.config.registry.getUtility(IJinja2Environment)

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
        import pyramid_jinja2
        from pyramid.renderers import render
        config = testing.setUp()
        config.add_settings({
            'jinja2.directories': 'pyramid_jinja2.tests:templates',
            'jinja2.tests': 'my_test = pyramid_jinja2.tests.test_it.my_test_func',
            'jinja2.filters': 'my_filter = pyramid_jinja2.tests.test_it.my_test_func',
            'jinja2.globals': 'my_global = pyramid_jinja2.tests.test_it.my_test_func'
        })
        config.add_renderer('.jinja2', pyramid_jinja2.renderer_factory)
        result = render('tests_and_filters.jinja2', {})
        #my_test_func returs "True" - it will be render as True when usign
        # as filter and will pass in tests
        self.assertEqual(result, text_('True is not False True', 'utf-8'))
        testing.tearDown()


class Test_includeme(unittest.TestCase):
    def test_it(self):
        from pyramid.interfaces import IRendererFactory
        from pyramid_jinja2 import includeme
        from pyramid_jinja2 import renderer_factory
        config = testing.setUp()
        config.registry.settings['jinja2.directories'] = '/foobar'
        includeme(config)
        utility = config.registry.getUtility(IRendererFactory, name='.jinja2')
        self.assertEqual(utility, renderer_factory)


class Test_add_jinja2_assetdirs(unittest.TestCase):
    def test_it(self):
        from pyramid_jinja2 import includeme
        from pyramid_jinja2 import IJinja2Environment
        import os
        config = testing.setUp()
        config.package_name = __name__
        config.registry.settings['jinja2.directories'] = 'foobar'
        includeme(config)
        utility = config.registry.getUtility(IJinja2Environment)
        self.assertEqual(
            [x.split(os.sep)[-3:] for x in utility.loader.searchpath],
            [['pyramid_jinja2', 'tests', 'foobar']])

        config.add_jinja2_search_path('grrr')
        self.assertEqual(
            [x.split(os.sep)[-3:] for x in utility.loader.searchpath],
            [['pyramid_jinja2', 'tests', 'foobar'], ['pyramid_jinja2', 'tests', 'grrr']])

class Test_get_jinja2_environment(unittest.TestCase):
    def test_it(self):
        from jinja2.environment import Environment
        from pyramid_jinja2 import includeme
        config = testing.setUp()
        includeme(config)
        self.assertEqual(config.get_jinja2_environment().__class__,
                         Environment)


class Test_bytecode_caching(unittest.TestCase):
    def test_default(self):
        from pyramid_jinja2 import includeme
        import jinja2.bccache
        config = testing.setUp()
        config.registry.settings = {}
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
        config.registry.settings['jinja2.bytecode_caching_directory'] = tmpdir
        includeme(config)
        env = config.get_jinja2_environment()
        self.assertEqual(env.bytecode_cache.directory, tmpdir)
        # TODO: test tmpdir is deleted when interpreter exits

    def test_reload_templates(self):
        from pyramid_jinja2 import includeme
        config = testing.setUp()
        config.registry.settings = {}
        config.registry.settings['reload_templates'] = 'true'
        includeme(config)
        env = config.get_jinja2_environment()
        self.assertTrue(env.auto_reload)

    def test_pyramid_reload_templates(self):
        from pyramid_jinja2 import includeme
        config = testing.setUp()
        config.registry.settings = {}
        config.registry.settings['pyramid.reload_templates'] = 'true'
        includeme(config)
        env = config.get_jinja2_environment()
        self.assertTrue(env.auto_reload)


class TestSmartAssetSpecLoader(unittest.TestCase):

    def test_list_templates(self):
        from pyramid_jinja2 import SmartAssetSpecLoader
        loader = SmartAssetSpecLoader()
        self.assertRaises(TypeError, loader.list_templates)

    def test_get_source(self):
        from pyramid_jinja2 import SmartAssetSpecLoader
        from jinja2.exceptions import TemplateNotFound

        loader = SmartAssetSpecLoader()

        self.assertRaises(TemplateNotFound,
                          loader.get_source, None, 'asset:foobar.jinja2')
        asset = 'asset:pyramid_jinja2.tests:templates/helloworld.jinja2'
        self.assertNotEqual(loader.get_source(None, asset), None)

        # make sure new non-prefixed asset spec based loading works
        asset = 'pyramid_jinja2.tests:templates/helloworld.jinja2'
        self.assertNotEqual(loader.get_source(None, asset), None)

        # make sure new non-prefixed asset spec based loading works
        # without the leading package name
        asset = 'templates/helloworld.jinja2'
        env = Mock(_default_package='pyramid_jinja2.tests')
        self.assertNotEqual(loader.get_source(env, asset), None)


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


class GetTextWrapperTests(unittest.TestCase):

    def test_it(self):
        from pyramid_jinja2 import GetTextWrapper

        class MyGetTextWrapper(GetTextWrapper):
            class localizer:
                @staticmethod
                def translate(s, domain):
                    return s

                @staticmethod
                def pluralize(s1, s2, n, domain):
                    return s2

            def __init__(self):
                GetTextWrapper.__init__(self, 'messages')

        self.assertEqual(MyGetTextWrapper().gettext('foo'), 'foo')
        self.assertEqual(MyGetTextWrapper().ngettext('foo', 'foos', 3), 'foos')


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
        self.assertEqual(pf.caller_package(), xml)


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


class MiscTests(Base, unittest.TestCase):

    def test_add_jinja2_extension(self):
        from pyramid_jinja2 import (add_jinja2_extension,
                                    _get_or_build_default_environment)
        self.config.include('pyramid_jinja2')
        env_before = _get_or_build_default_environment(self.config.registry)

        class MockExt(object):
            identifier = 'foobar'

            def __init__(self, x):
                self.x = x

        add_jinja2_extension(self.config, MockExt)

        env_after = _get_or_build_default_environment(self.config.registry)
        self.assertTrue('foobar' in env_after.extensions)
        self.assertTrue(env_before is env_after)


class UndefinedTests(Base, unittest.TestCase):

    def _assert_has_undefined(self, expected_undefined):
        from pyramid_jinja2 import IJinja2Environment
        self.config.include('pyramid_jinja2')
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.undefined, expected_undefined)

    def test_set_regular_undefined_when_unset(self):
        from jinja2 import Undefined
        self._assert_has_undefined(Undefined)

    def test_set_regular_undefined_by_default(self):
        from jinja2 import Undefined
        self.config.registry.settings['jinja2.undefined'] = ''
        from jinja2 import Undefined
        self._assert_has_undefined(Undefined)

    def test_set_strict_undefined(self):
        from jinja2 import StrictUndefined
        self.config.registry.settings['jinja2.undefined'] = 'strict'
        self._assert_has_undefined(StrictUndefined)

    def test_set_debug_undefined(self):
        from jinja2 import DebugUndefined
        self.config.registry.settings['jinja2.undefined'] = 'debug'
        self._assert_has_undefined(DebugUndefined)

def my_test_func(*args, **kwargs):
    """ Used as a fake filter/test function """
    return True
