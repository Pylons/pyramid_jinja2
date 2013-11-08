# -*- coding: utf-8 -*-

import unittest
from pyramid import testing
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

class Test_route_path_filter(unittest.TestCase):
    def setUp(self):
        self.environment = Environment()
        from pyramid_jinja2.filters import route_path_filter
        self.environment.filters['route_path'] = route_path_filter
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
        rendered = self._callFUT({}, "{{'dummy_route1' | route_path }}")
        self.assertEqual(rendered, '/dummy/')

    def test_filter_with_arguments(self):
        rendered = self._callFUT({}, "{{'dummy_route2' | route_path('x', name='test') }}")
        self.assertEqual(rendered, '/dummy/test/x')

class Test_static_url_filter(unittest.TestCase):
    def setUp(self):
        self.environment = Environment()
        from pyramid_jinja2.filters import static_url_filter
        self.environment.filters['static_url'] = static_url_filter
        from pyramid.config import Configurator
        self.config = Configurator(autocommit=True)
        self.config.begin(request=DummyRequest())
        self.config.add_static_view('myfiles', 'dummy1:static')
        self.config.add_static_view('otherfiles/{owner}', 'dummy2:files')
       
    def tearDown(self):
        self.config.end()

    def _callFUT(self, context, tmpl):
        tmpl = self.environment.from_string(tmpl)
        return tmpl.render(**context)

    def test_filter(self):
        rendered = self._callFUT({}, "{{'dummy1:static/the/quick/brown/fox.svg' | static_url }}")
        self.assertEqual(rendered, 'http://example.com/myfiles/the/quick/brown/fox.svg')

    def test_filter_with_arguments(self):
        rendered = self._callFUT({}, "{{'dummy2:files/report.txt' | static_url(owner='foo') }}")
        self.assertEqual(rendered, 'http://example.com/otherfiles/foo/report.txt')

class Test_static_path_filter(unittest.TestCase):
    def setUp(self):
        self.environment = Environment()
        from pyramid_jinja2.filters import static_path_filter
        self.environment.filters['static_path'] = static_path_filter
        from pyramid.config import Configurator
        self.config = Configurator(autocommit=True)
        self.config.begin(request=DummyRequest())
        self.config.add_static_view('myfiles', 'dummy1:static')
        self.config.add_static_view('otherfiles/{owner}', 'dummy2:files')
       
    def tearDown(self):
        self.config.end()

    def _callFUT(self, context, tmpl):
        tmpl = self.environment.from_string(tmpl)
        return tmpl.render(**context)

    def test_filter(self):
        rendered = self._callFUT({}, "{{'dummy1:static/the/quick/brown/fox.svg' | static_path }}")
        self.assertEqual(rendered, '/myfiles/the/quick/brown/fox.svg')

    def test_filter_with_arguments(self):
        rendered = self._callFUT({}, "{{'dummy2:files/report.txt' | static_path(owner='foo') }}")
        self.assertEqual(rendered, '/otherfiles/foo/report.txt')

class Test_filters_not_caching(unittest.TestCase):
    def setUp(self):
        from pyramid_jinja2 import includeme
        import jinja2.bccache
        config = testing.setUp()
        config.registry.settings = {}
        includeme(config)
        self.environment = config.get_jinja2_environment()
        from pyramid_jinja2.filters import route_url_filter
        self.environment.filters['route_url'] = route_url_filter
        from pyramid.config import Configurator
        self.config = Configurator(autocommit=True)

    def tearDown(self):
        self.config.end()

    def _callFUT(self, context, tmpl):
        tmpl = self.environment.from_string(tmpl)
        return tmpl.render(**context)

    def test_filter(self):
        self.config.begin(request=DummyRequest(application_url='http://example.com', host='example.com:80'))
        self.config.add_route('dummy_route1', '/dummy/')
        self.config.add_route('dummy_route2', '/dummy/:name/')

        rendered = self._callFUT({}, "{{'dummy_route1' | route_url }}")
        self.assertEqual(rendered, 'http://example.com/dummy/')
       
        self.config.begin(request=DummyRequest(application_url='http://sub.example.com', host='sub.example.com:80'))
        rendered = self._callFUT({}, "{{'dummy_route1' | route_url }}")
        self.assertEqual(rendered, 'http://sub.example.com/dummy/')

    def test_filter_with_arguments(self):
        self.config.begin(request=DummyRequest(application_url='http://example.com', host='example.com:80'))
        self.config.add_route('dummy_route1', '/dummy/')
        self.config.add_route('dummy_route2', '/dummy/:name/')

        rendered = self._callFUT({}, "{{'dummy_route2' | route_url('x', name='test') }}")
        self.assertEqual(rendered, 'http://example.com/dummy/test/x')

        self.config.begin(request=DummyRequest(application_url='http://sub.example.com', host='sub.example.com:80'))
        rendered = self._callFUT({}, "{{'dummy_route2' | route_url('x', name='test') }}")
        self.assertEqual(rendered, 'http://sub.example.com/dummy/test/x')


