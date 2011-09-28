from pyramid_jinja2.compat import text_
from pyramid import testing


class DummyEnvironment(object):
    def get_template(self, path):
        self.path = path
        return self

    def render(self, values):
        self.values = values
        return text_('result')


class DummyRendererInfo(object):
    def __init__(self, kw):
        self.__dict__.update(kw)
        if 'registry' in self.__dict__:
            self.settings = self.registry.settings


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Base(object):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
        self.request.registry = self.config.registry
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'templates')

    def tearDown(self):
        testing.tearDown()
        del self.config
