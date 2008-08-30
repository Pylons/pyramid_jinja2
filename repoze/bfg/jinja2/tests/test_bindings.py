import unittest

class TestBindings(unittest.TestCase):
    def test_load_template(self):
        from repoze.bfg.jinja2.bindings import load_template
        template = load_template('templates/helloworld.jinja2')
        self.assertEqual(template,
              u"{% set a, b = 'foo', 'f\xf6\xf6' %}\nHello {{ b }}\n")

    def test_get_template(self):
        from repoze.bfg.jinja2.bindings import get_template
        template = get_template('templates/helloworld.jinja2')
        self.assertEqual(template.module.a, 'foo')
        self.assertEqual(template.module.b, u'f\xf6\xf6')

    def test_render_template(self):
        from repoze.bfg.jinja2.bindings import render_template
        rendering = render_template('templates/helloworld.jinja2')
        self.assertEqual(rendering, u'\nHello f\xf6\xf6')
        
    def test_render_template_to_response(self):
        from repoze.bfg.jinja2.bindings import render_template_to_response
        response = render_template_to_response('templates/helloworld.jinja2')
        self.assertEqual(response.app_iter[0],
                         u'\nHello f\xf6\xf6'.encode('utf-8'))
        
        
