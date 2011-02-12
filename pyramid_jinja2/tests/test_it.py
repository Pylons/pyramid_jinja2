## come on python gimme some of that sweet, sweet -*- coding: utf-8 -*-

import unittest
from pyramid import testing

def dummy_filter(value): return 'hoge'

class Test_asbool(unittest.TestCase):
    def _callFUT(self, value):
        from pyramid_jinja2 import asbool
        return asbool(value)

    def test_str_true(self):
        self.assertEqual(self._callFUT('true'), True)
        
    def test_str_false(self):
        self.assertEqual(self._callFUT('false'), False)

    def test_str_unrecognized(self):
        self.assertRaises(ValueError, self._callFUT, '123')
        
class Test_parse_filters(unittest.TestCase):
    def _callFUT(self, value):
        from pyramid_jinja2 import parse_filters
        return parse_filters(value)

    def test_parse_singile_line(self):
        import pyramid_jinja2
        self.assertEqual(self._callFUT('dummy=pyramid_jinja2'),
                         {'dummy':pyramid_jinja2})
        
    def test_parse_multi_line(self):
        import pyramid_jinja2
        self.assertEqual(self._callFUT("""\
            dummy =  pyramid_jinja2
            dummy2 =pyramid_jinja2"""), 
        {'dummy':pyramid_jinja2, 'dummy2':pyramid_jinja2})

    def test_parse_dict_stringvals(self):
        import pyramid_jinja2
        self.assertEqual(self._callFUT(
            {'dummy': 'pyramid_jinja2',
             'dummy2': 'pyramid_jinja2'}), 
        {'dummy':pyramid_jinja2, 'dummy2':pyramid_jinja2})

    def test_parse_dict_objvals(self):
        import pyramid_jinja2
        self.assertEqual(self._callFUT(
            {'dummy': pyramid_jinja2,
             'dummy2': pyramid_jinja2}), 
        {'dummy':pyramid_jinja2, 'dummy2':pyramid_jinja2})

class Base(object):
    def setUp(self):
        self.config = testing.setUp()
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'templates')

    def tearDown(self):
        testing.tearDown()

class Test_renderer_factory(Base, unittest.TestCase):
    def _callFUT(self, info):
        from pyramid_jinja2 import renderer_factory
        return renderer_factory(info)

    def test_no_directories(self):
        from pyramid.exceptions import ConfigurationError
        info = DummyRendererInfo({
            'name':'helloworld.jinja2',
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            })
        self.assertRaises(ConfigurationError, self._callFUT, info)

    def test_no_environment(self):
        from pyramid_jinja2 import IJinja2Environment
        settings = {'jinja2.directories':self.templates_dir}
        info = DummyRendererInfo({
            'name':'helloworld.jinja2',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        renderer = self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.loader.searchpath, [self.templates_dir])
        self.assertEqual(renderer.info, info)
        self.assertEqual(renderer.environment, environ)

    def test_composite_directories_path(self):
        from pyramid_jinja2 import IJinja2Environment
        twice = self.templates_dir + '\n' + self.templates_dir
        settings = {'jinja2.directories':twice}
        info = DummyRendererInfo({
            'name':'helloworld.jinja2',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.loader.searchpath, [self.templates_dir]*2)

    def test_with_environ(self):
        from pyramid_jinja2 import IJinja2Environment
        environ = dict()
        self.config.registry.registerUtility(environ, IJinja2Environment)
        info = DummyRendererInfo({
            'name':'helloworld.jinja2',
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            })
        renderer = self._callFUT(info)
        self.assertEqual(renderer.environment, environ)
        self.assertEqual(renderer.info, info)

    def test_with_filters_object(self):
        from pyramid_jinja2 import IJinja2Environment

        def dummy_filter(value): return 'hoge'

        settings = {'jinja2.directories':self.templates_dir,
            'jinja2.filters':{'dummy':dummy_filter}}
        info = DummyRendererInfo({
            'name':'helloworld.jinja2',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.filters['dummy'], dummy_filter)

    def test_with_filters_string(self):
        from pyramid_jinja2 import IJinja2Environment


        settings = {'jinja2.directories':self.templates_dir,
            'jinja2.filters':'dummy=pyramid_jinja2.tests.test_it:dummy_filter'}
        info = DummyRendererInfo({
            'name':'helloworld.jinja2',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.filters['dummy'], dummy_filter)

    def test_with_extension(self):
        from pyramid_jinja2 import IJinja2Environment
        settings = {'jinja2.directories':self.templates_dir,
                    'jinja2.extensions':"""
                    pyramid_jinja2.tests.extensions.TestExtension
                    """}
        info = DummyRendererInfo({
            'name':'helloworld.jinja2',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        renderer = self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.loader.searchpath, [self.templates_dir])
        self.assertEqual(renderer.info, info)
        self.assertEqual(renderer.environment, environ)
        import pyramid_jinja2.tests.extensions
        ext=environ.extensions['pyramid_jinja2.tests.extensions.TestExtension']
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
            'name':'name',
            })
        instance = self._makeOne(info, environ)
        result = instance({}, {'system':1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'result')

    def test_call_with_system_context(self):
        environ = DummyEnvironment()
        info = DummyRendererInfo({
            'name':'name',
            })
        instance = self._makeOne(info, environ)
        result = instance({}, {'context':1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'result')
        self.assertEqual(environ.values, {'context':1})

    def test_call_with_nondict_value(self):
        environ = DummyEnvironment()
        info = DummyRendererInfo({
            'name':'name',
            })
        instance = self._makeOne(info, environ)
        self.assertRaises(ValueError, instance, None, {'context':1})

    def test_implementation(self):
        environ = DummyEnvironment()
        info = DummyRendererInfo({
            'name':'name',
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
        result = render('helloworld.jinja2', {'a':1})
        self.assertEqual(result, u'\nHello föö')

class Test_includeme(unittest.TestCase):
    def test_it(self):
        from pyramid.interfaces import IRendererFactory
        from pyramid_jinja2 import includeme
        from pyramid_jinja2 import renderer_factory
        config = testing.setUp()
        config.registry.settings['jinja2.directories'] = 'foobar'
        includeme(config)
        utility = config.registry.getUtility(IRendererFactory, name='.jinja2')
        self.assertEqual(utility, renderer_factory)

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
        
