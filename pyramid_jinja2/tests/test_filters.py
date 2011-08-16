# -*- coding: utf-8 -*-

import unittest
from jinja2 import Environment
from pyramid.testing import DummyRequest

class DummyRoot(object):
    __name__ = __parent__ = None

class DummyModel(object):
    __name__ = 'dummy'
    __parent__ = DummyRoot()

class Test_model_url_filter(unittest.TestCase):
    def setUp(self):
        self.environment = Environment()
        from pyramid_jinja2.filters import model_url_filter
        self.environment.filters['model_url'] = model_url_filter
        from pyramid.config import Configurator
        self.config = Configurator(autocommit=True)
        self.config.begin(request=DummyRequest())

    def tearDown(self):
        self.config.end()

    def _callFUT(self, context, tmpl):
        tmpl = self.environment.from_string(tmpl)
        return tmpl.render(**context)


    def test_filter(self):
        model = DummyModel()
        rendered = self._callFUT({'model':model}, '{{model|model_url}}')
        self.assertEqual(rendered, 'http://example.com/dummy/')

    def test_filter_with_elements(self):
        model = DummyModel()
        rendered = self._callFUT({'model':model}, "{{model|model_url('edit')}}")
        self.assertEqual(rendered, 'http://example.com/dummy/edit')

class Test_route_url_filter(unittest.TestCase):
    def setUp(self):
        self.environment = Environment()
        from pyramid_jinja2.filters import route_url_filter
        self.environment.filters['route_url'] = route_url_filter
        from pyramid.config import Configurator
        self.config = Configurator(autocommit=True)
        self.config.begin(request=DummyRequest())
        self.config.add_route('dummy_route1', '/dummy/')
        self.config.add_route('dummy_route2', '/dummy/:name/')

    def tearDown(self):
        self.config.end()

    def _callFUT(self, context, tmpl):
        tmpl = self.environment.from_string(tmpl)
        return tmpl.render(**context)

    def test_filter(self):
        rendered = self._callFUT({}, "{{'dummy_route1' | route_url }}")
        self.assertEqual(rendered, 'http://example.com/dummy/')

    def test_filter_with_arguments(self):
        rendered = self._callFUT({}, "{{'dummy_route2' | route_url('x', name='test') }}")
        self.assertEqual(rendered, 'http://example.com/dummy/test/x')
