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


class Test_parse_filters(unittest.TestCase):
    def _callFUT(self, value):
        from pyramid_jinja2 import parse_filters
        return parse_filters(value)

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

        def dummy_filter(value): return 'hoge'

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


class TemplateRenderingErrorTests(unittest.TestCase):

    def test_it(self):
        from pyramid_jinja2 import TemplateRenderingError
        error = TemplateRenderingError('foobar.jinja2', 'random message')
        self.assertEqual(str(error), 'foobar.jinja2: random message')


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
        config.registry.settings['jinja2.directories'] = 'foobar'
        includeme(config)
        utility = config.registry.getUtility(IJinja2Environment)
        self.assertEqual([x.split(os.sep)[-1]
                          for x in utility.loader.searchpath], ['foobar'])
        config.add_jinja2_search_path('grrr')
        self.assertEqual([x.split(os.sep)[-1]
                          for x in utility.loader.searchpath],
                         ['foobar', 'grrr'])

class Test_get_jinja2_environment(unittest.TestCase):
    def test_it(self):
        from jinja2.environment import Environment
        from pyramid_jinja2 import includeme
        config = testing.setUp()
        includeme(config)
        self.assertEqual(config.get_jinja2_environment().__class__,
                         Environment)


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
        from pyramid_jinja2 import FileInfo, TemplateRenderingError

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

        if not PY3:

            mi = MyFileInfo(bytes_('nothing good her\xe9, move along'))
            self.assertRaises(TemplateRenderingError, mi._delay_init)


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


class MiscTests(Base, unittest.TestCase):

    def test_add_jinja2_extension(self):
        from pyramid_jinja2 import (add_jinja2_extension,
                                    _get_or_build_default_environment)
        self.config.include('pyramid_jinja2')

        class MockExt(object):
            identifier = 'foobar'

            def __init__(self, x):
                self.x = x

        add_jinja2_extension(self.config, MockExt)

        u = _get_or_build_default_environment(self.config.registry)
        self.assertTrue('foobar' in u.extensions)
