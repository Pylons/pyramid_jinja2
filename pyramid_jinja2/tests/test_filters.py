import unittest
from pyramid import testing

class DummyRoot(object):
    __name__ = __parent__ = None

class DummyModel(object):
    __name__ = 'dummy'
    __parent__ = DummyRoot()

class Base(object):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
        self.request.registry = self.config.registry

        from pyramid_jinja2 import Environment
        self.environment = Environment()

        self._addFilters()

    def tearDown(self):
        testing.tearDown()

    def _addFilters(self): pass

    def _callFUT(self, context, tmpl):
        tmpl = self.environment.from_string(tmpl)
        return tmpl.render(**context)

class Test_model_url_filter(Base, unittest.TestCase):

    def _addFilters(self):
        from pyramid_jinja2.filters import model_url_filter
        self.environment.filters['model_url'] = model_url_filter

    def test_filter(self):
        model = DummyModel()
        rendered = self._callFUT({'model': model}, '{{model|model_url}}')
        self.assertEqual(rendered, 'http://example.com/dummy/')

    def test_filter_with_elements(self):
        model = DummyModel()
        rendered = self._callFUT({'model': model}, "{{model|model_url('edit')}}")
        self.assertEqual(rendered, 'http://example.com/dummy/edit')

class Test_model__filter(Base, unittest.TestCase):

    def _addFilters(self):
        from pyramid_jinja2.filters import model_path_filter
        self.environment.filters['model_path'] = model_path_filter

    def test_filter(self):
        model = DummyModel()
        rendered = self._callFUT({'model': model}, '{{model|model_path}}')
        self.assertEqual(rendered, '/dummy/')

    def test_filter_with_elements(self):
        model = DummyModel()
        rendered = self._callFUT({'model': model}, "{{model|model_path('edit')}}")
        self.assertEqual(rendered, '/dummy/edit')

class Test_route_url_filter(Base, unittest.TestCase):
    def _addFilters(self):
        from pyramid_jinja2.filters import route_url_filter
        self.environment.filters['route_url'] = route_url_filter

        self.config.add_route('dummy_route1', '/dummy/')
        self.config.add_route('dummy_route2', '/dummy/:name/')

    def test_filter(self):
        rendered = self._callFUT({}, "{{'dummy_route1' | route_url }}")
        self.assertEqual(rendered, 'http://example.com/dummy/')

    def test_filter_with_arguments(self):
        rendered = self._callFUT({}, "{{'dummy_route2' | route_url('x', name='test') }}")
        self.assertEqual(rendered, 'http://example.com/dummy/test/x')

class Test_route_path_filter(Base, unittest.TestCase):
    def _addFilters(self):
        from pyramid_jinja2.filters import route_path_filter
        self.environment.filters['route_path'] = route_path_filter

        self.config.add_route('dummy_route1', '/dummy/')
        self.config.add_route('dummy_route2', '/dummy/:name/')

    def test_filter(self):
        rendered = self._callFUT({}, "{{'dummy_route1' | route_path }}")
        self.assertEqual(rendered, '/dummy/')

    def test_filter_with_arguments(self):
        rendered = self._callFUT({}, "{{'dummy_route2' | route_path('x', name='test') }}")
        self.assertEqual(rendered, '/dummy/test/x')

class Test_static_url_filter(Base, unittest.TestCase):
    def _addFilters(self):
        from pyramid_jinja2.filters import static_url_filter
        self.environment.filters['static_url'] = static_url_filter

        self.config.add_static_view('myfiles', 'dummy1:static')
        self.config.add_static_view('otherfiles/{owner}', 'dummy2:files')

    def test_filter(self):
        rendered = self._callFUT({}, "{{'dummy1:static/the/quick/brown/fox.svg' | static_url }}")
        self.assertEqual(rendered, 'http://example.com/myfiles/the/quick/brown/fox.svg')

    def test_filter_with_arguments(self):
        rendered = self._callFUT({}, "{{'dummy2:files/report.txt' | static_url(owner='foo') }}")
        self.assertEqual(rendered, 'http://example.com/otherfiles/foo/report.txt')

class Test_static_path_filter(Base, unittest.TestCase):
    def _addFilters(self):
        from pyramid_jinja2.filters import static_path_filter
        self.environment.filters['static_path'] = static_path_filter

        self.config.add_static_view('myfiles', 'dummy1:static')
        self.config.add_static_view('otherfiles/{owner}', 'dummy2:files')

    def test_filter(self):
        rendered = self._callFUT({}, "{{'dummy1:static/the/quick/brown/fox.svg' | static_path }}")
        self.assertEqual(rendered, '/myfiles/the/quick/brown/fox.svg')

    def test_filter_with_arguments(self):
        rendered = self._callFUT({}, "{{'dummy2:files/report.txt' | static_path(owner='foo') }}")
        self.assertEqual(rendered, '/otherfiles/foo/report.txt')

class Test_filters_not_caching(Base, unittest.TestCase):
    def _addFilters(self):
        from pyramid_jinja2.filters import route_url_filter
        self.environment.filters['route_url'] = route_url_filter

        self.config.add_route('dummy_route1', '/dummy/')
        self.config.add_route('dummy_route2', '/dummy/:name/')

    def test_filter(self):
        self.request.application_url = 'http://example.com'
        self.request.host = 'example.com:80'
        rendered = self._callFUT({}, "{{'dummy_route1' | route_url }}")
        self.assertEqual(rendered, 'http://example.com/dummy/')

        self.request.application_url = 'http://sub.example.com'
        self.request.host = 'sub.example.com:80'
        rendered = self._callFUT({}, "{{'dummy_route1' | route_url }}")
        self.assertEqual(rendered, 'http://sub.example.com/dummy/')

    def test_filter_with_arguments(self):
        self.request.application_url = 'http://example.com'
        self.request.host = 'example.com:80'
        rendered = self._callFUT({}, "{{'dummy_route2' | route_url('x', name='test') }}")
        self.assertEqual(rendered, 'http://example.com/dummy/test/x')

        self.request.application_url = 'http://sub.example.com'
        self.request.host = 'sub.example.com:80'
        rendered = self._callFUT({}, "{{'dummy_route2' | route_url('x', name='test') }}")
        self.assertEqual(rendered, 'http://sub.example.com/dummy/test/x')


