from pyramid import testing


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


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
