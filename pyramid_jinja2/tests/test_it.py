## come on python gimme some of that sweet, sweet -*- coding: utf-8 -*-

import unittest
from pyramid import testing


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


class Base(object):
    def setUp(self):
        self.config = testing.setUp()
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'templates')

    def tearDown(self):
        testing.tearDown()
        del self.config


class Test_renderer_factory(Base, unittest.TestCase):
    def _callFUT(self, info):
        from pyramid_jinja2 import renderer_factory
        return renderer_factory(info)

    def test_no_directories(self):
        from pyramid.exceptions import ConfigurationError
        info = DummyRendererInfo({
            'name': 'helloworld.jinja2',
            'package': None,
            'registry': self.config.registry,
            })
        renderer = self._callFUT(info)
        self.assertRaises(ConfigurationError, lambda: renderer({}, {}))

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

    def test_with_extension(self):
        from pyramid_jinja2 import IJinja2Environment
        self.config.registry.settings.update(
            {'jinja2.directories': self.templates_dir,
             'jinja2.extensions': """
                    pyramid_jinja2.tests.extensions.TestExtension
                    """})
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
        import pyramid_jinja2.tests.extensions
        ext = environ.extensions[
            'pyramid_jinja2.tests.extensions.TestExtension']
        self.assertEqual(ext.__class__,
                         pyramid_jinja2.tests.extensions.TestExtension)


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
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'result')

    def test_call_with_system_context(self):
        environ = DummyEnvironment()
        info = DummyRendererInfo({
            'name': 'name',
            })
        instance = self._makeOne(info, environ)
        result = instance({}, {'context': 1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'result')
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
        self.assertEqual(result, u'result')


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
        self.assertEqual(result, u'\nHello föö')


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
        self.assertEqual(testapp.get('/').body, 'foo')

        app2 = config2.make_wsgi_app()
        testapp = TestApp(app2)
        self.assertEqual(testapp.get('/').body, 'bar')


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


class DummyEnvironment(object):
    def get_template(self, path):
        self.path = path
        return self

    def render(self, values):
        self.values = values
        return u'result'


class DummyRendererInfo(object):
    def __init__(self, kw):
        self.__dict__.update(kw)
        if 'registry' in self.__dict__:
            self.settings = self.registry.settings


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
