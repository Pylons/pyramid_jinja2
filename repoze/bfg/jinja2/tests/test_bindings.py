import os.path
import unittest
from repoze.bfg import testing

class TestAutoReload(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()
        
    def _callFUT(self):
        from repoze.bfg.jinja2.bindings import _auto_reload
        return _auto_reload()

    def test_true(self):
        from repoze.bfg.interfaces import ISettings
        class Settings:
            reload_templates = True
        settings = Settings()
        testing.registerUtility(settings, ISettings)
        self.assertEqual(self._callFUT(), True)
        
    def test_false(self):
        from repoze.bfg.interfaces import ISettings
        class Settings:
            reload_templates = True
        settings = Settings()
        testing.registerUtility(settings, ISettings)
        self.assertEqual(self._callFUT(), True)

    def test_unregistered(self):
        self.assertEqual(self._callFUT(), False)

class TestLoadTemplate(unittest.TestCase):
    def _callFUT(self, path):
        from repoze.bfg.jinja2.bindings import load_template
        return load_template(path)
        
    def test_load_template(self):
        template = self._callFUT('templates/helloworld.jinja2')
        self.assertEqual(template[0], 
            u"{% set a, b = 'foo', 'f\xf6\xf6' %}\nHello {{ b }}\n")
        self.assert_(
            template[1].endswith('tests/templates/helloworld.jinja2')
            )
        uptodate = template[2]
        self.assertEqual(uptodate(), True)

    def test_load_template_deleted_template_uptodate(self):
        name = 'templates/to_delete.jinja2'
        path = os.path.join(os.path.dirname(__file__), name)
        f = open(path, 'w')
        f.write('')
        f.close()
        template = self._callFUT(name)
        uptodate = template[2]
        self.assertEqual(uptodate(), True)
        os.unlink(path)
        self.assertEqual(uptodate(), False)
        self.assertEqual(self._callFUT(name), None)

    def test_load_template_nonexistent_template(self):
        from repoze.bfg.jinja2.bindings import load_template
        name = 'templates/nonexistent.jinja2'
        path = os.path.join(os.path.dirname(__file__), name)
        self.assertEqual(load_template(name), None)

class TestBfgLoader(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.jinja2.bindings import BfgLoader
        return BfgLoader
    
    def _makeOne(self, load_func):
        return self._getTargetClass()(load_func)

    def test_get_source_autoreload_None_default(self):
        def load_func(path):
            return u'123'
        loader = self._makeOne(load_func)
        class Environment:
            auto_reload = False
        environ = Environment()
        result = loader.get_source(environ, 'whatever')
        self.assertEqual(loader.auto_reload, False)
        self.assertEqual(result, (u'123', None, None))
        self.assertEqual(environ.auto_reload, False)

    def test_get_source_autoreload_None_withisettings(self):
        def load_func(path):
            return u'123'
        loader = self._makeOne(load_func)
        class Environment:
            auto_reload = False
        environ = Environment()
        from repoze.bfg.interfaces import ISettings
        class Settings:
            reload_templates = True
        settings = Settings()
        testing.registerUtility(settings, ISettings)
        result = loader.get_source(environ, 'whatever')
        self.assertEqual(loader.auto_reload, True)
        self.assertEqual(result, (u'123', None, None))
        self.assertEqual(environ.auto_reload, True)

    def test_get_source_autoreload_true(self):
        def load_func(path):
            return u'123'
        loader = self._makeOne(load_func)
        loader.auto_reload = True
        class Environment:
            auto_reload = False
        environ = Environment()
        result = loader.get_source(environ, 'whatever')
        self.assertEqual(result, (u'123', None, None))
        self.assertEqual(environ.auto_reload, True)

class TestGetTemplate(unittest.TestCase):
    def _callFUT(self, path):
        from repoze.bfg.jinja2.bindings import get_template
        return get_template(path)
        
    def test_it(self):
        template = self._callFUT('templates/helloworld.jinja2')
        self.assertEqual(template.module.a, 'foo')
        self.assertEqual(template.module.b, u'f\xf6\xf6')

class TestRenderTemplate(unittest.TestCase):
    def _callFUT(self, path):
        from repoze.bfg.jinja2.bindings import render_template
        return render_template(path)

    def test_it(self):
        rendering = self._callFUT('templates/helloworld.jinja2')
        self.assertEqual(rendering, u'\nHello f\xf6\xf6')

class TestRenderTemplateToResponse(unittest.TestCase):
    def _callFUT(self, path):
        from repoze.bfg.jinja2.bindings import render_template_to_response
        return render_template_to_response(path)
        
    def test_it(self):
        response = self._callFUT('templates/helloworld.jinja2')
        self.assertEqual(response.app_iter[0],
                         u'\nHello f\xf6\xf6'.encode('utf-8'))
        
