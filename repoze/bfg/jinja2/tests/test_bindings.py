import unittest
from repoze.bfg import testing

class Base(object):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'templates', name)

    def _registerUtility(self, utility, iface, name=''):
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerUtility(utility, iface, name=name)
        return sm
        
class Jinja2TemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.jinja2.bindings import Jinja2TemplateRenderer
        return Jinja2TemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITemplateRenderer
        path = self._getTemplatePath('helloworld.jinja2')
        verifyObject(ITemplateRenderer, self._makeOne(path))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_call(self):
        minimal = self._getTemplatePath('helloworld.jinja2')
        instance = self._makeOne(minimal)
        result = instance({}, {'system':1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'\nHello f\xf6\xf6')

    def test_call_autoreload(self):
        testing.registerSettings(reload_templates=True)
        minimal = self._getTemplatePath('helloworld.jinja2')
        instance = self._makeOne(minimal)
        result = instance({}, {'system':1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'\nHello f\xf6\xf6')

    def test_call_with_nondict_value(self):
        minimal = self._getTemplatePath('helloworld.jinja2')
        instance = self._makeOne(minimal)
        self.assertRaises(ValueError, instance, None, {})

    def test_implementation(self):
        minimal = self._getTemplatePath('helloworld.jinja2')
        instance = self._makeOne(minimal)
        result = instance.implementation().render()
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'\nHello f\xf6\xf6')
        
    def test_implementation_autoreload(self):
        testing.registerSettings(reload_templates=True)
        minimal = self._getTemplatePath('helloworld.jinja2')
        instance = self._makeOne(minimal)
        result = instance.implementation().render()
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'\nHello f\xf6\xf6')

    def test_extends(self):
        minimal = self._getTemplatePath('extends.jinja2')
        instance = self._makeOne(minimal)
        result = instance({}, {'system':1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'\nHello f\xf6\xf6Yo!')
        

class RenderTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from repoze.bfg.jinja2 import render_template
        return render_template(name, **kw)

    def test_it(self):
        minimal = self._getTemplatePath('helloworld.jinja2')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'\nHello f\xf6\xf6')

class RenderTemplateToResponseTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from repoze.bfg.jinja2 import render_template_to_response
        return render_template_to_response(name, **kw)

    def test_it(self):
        minimal = self._getTemplatePath('helloworld.jinja2')
        result = self._callFUT(minimal)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter, ['\nHello f\xc3\xb6\xc3\xb6'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)

    def test_iresponsefactory_override(self):
        from webob import Response
        class Response2(Response):
            pass
        from repoze.bfg.interfaces import IResponseFactory
        self._registerUtility(Response2, IResponseFactory)
        minimal = self._getTemplatePath('helloworld.jinja2')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, Response2))

class GetRendererTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.jinja2 import get_renderer
        return get_renderer(name)

    def test_nonabs_registered(self):
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('helloworld.jinja2')
        utility = ZPTTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result, utility)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('helloworld.jinja2')
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), None)
        utility = ZPTTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result, utility)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)

    def test_explicit_registration(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        class Dummy:
            template = object()
        utility = Dummy()
        self._registerUtility(utility, ITemplateRenderer, name='foo')
        result = self._callFUT('foo')
        self.failUnless(result is utility)

class GetTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.jinja2 import get_template
        return get_template(name)

    def test_nonabs_registered(self):
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('helloworld.jinja2')
        utility = ZPTTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result.filename, minimal)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('helloworld.jinja2')
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), None)
        utility = ZPTTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result.filename, minimal)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)

    def test_explicit_registration(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        class Dummy:
            template = object()
            def implementation(self):
                return self.template
        utility = Dummy()
        self._registerUtility(utility, ITemplateRenderer, name='foo')
        result = self._callFUT('foo')
        self.failUnless(result is utility.template)
