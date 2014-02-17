import unittest
import pyramid.testing


class DemoTests(unittest.TestCase):
    def test_root_view(self):
        from pyramid_jinja2.demo import root_view
        m = pyramid.testing.DummyRequest()
        root_view(m)
        self.assertEqual(m.locale_name, 'fr')

    def test_app(self):
        from pyramid_jinja2.demo import app
        webapp = app({})
        self.assertTrue(callable(webapp))

    def test_main(self):
        from pyramid_jinja2.demo import Mainer

        class MyMainer(Mainer):
            def serve_forever(self):
                self.serving = True

            def make_server(self, *args, **kwargs):
                return Mock(args=args,
                            kwargs=kwargs,
                            serve_forever=self.serve_forever)

        mainer = MyMainer()
        mainer.main()
        self.assertTrue(getattr(mainer, 'serving', False))

class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
