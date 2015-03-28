import os.path
import unittest


class Test_parse_named_assetspecs(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from pyramid_jinja2.settings import parse_named_assetspecs
        return parse_named_assetspecs(*args, **kwargs)

    def test_it_with_strings(self):
        from pyramid.path import DottedNameResolver
        import pyramid_jinja2
        import pyramid_jinja2.tests
        resolver = DottedNameResolver()
        result = self._callFUT(
            '''
            foo = pyramid_jinja2
            bar= pyramid_jinja2.tests
            ''',
            resolver.maybe_resolve,
        )
        self.assertEqual(result['foo'], pyramid_jinja2)
        self.assertEqual(result['bar'], pyramid_jinja2.tests)

    def test_it_with_dict(self):
        from pyramid.path import DottedNameResolver
        import pyramid_jinja2
        import pyramid_jinja2.tests
        resolver = DottedNameResolver()
        result = self._callFUT(
            {
                'foo': 'pyramid_jinja2',
                'bar': pyramid_jinja2.tests,
            },
            resolver.maybe_resolve,
        )
        self.assertEqual(result['foo'], pyramid_jinja2)
        self.assertEqual(result['bar'], pyramid_jinja2.tests)


class Test_parse_loader_options_from_settings(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from pyramid_jinja2.settings import parse_loader_options_from_settings
        return parse_loader_options_from_settings(*args, **kwargs)

    def test_defaults(self):
        options = self._callFUT({}, 'p.', None, None)
        self.assertEqual(options['debug'], False)
        self.assertEqual(options['encoding'], 'utf-8')
        self.assertEqual(len(options['searchpath']), 0)

    def test_options(self):
        options = self._callFUT(
            {
                'debug_templates': 'false',
                'p.debug_templates': 'true',
                'p.input_encoding': 'ascii',
                'p.directories': 'pyramid_jinja2.tests:templates',
            },
            'p.', None, None,
        )
        self.assertEqual(options['debug'], True)
        self.assertEqual(options['encoding'], 'ascii')
        self.assertEqual(len(options['searchpath']), 1)
        self.assertTrue(
            options['searchpath'][0].endswith(
                os.path.join('pyramid_jinja2', 'tests', 'templates')))

    def test_options_with_spec(self):
        options = self._callFUT(
            {'p.directories': 'pyramid_jinja2:'}, 'p.', None, None)
        self.assertEqual(len(options['searchpath']), 1)
        self.assertTrue(options['searchpath'][0].endswith('pyramid_jinja2'))

    def test_options_with_abspath(self):
        import os.path
        here = os.path.dirname(os.path.abspath(__file__))
        options = self._callFUT({'p.directories': here}, 'p.', None, None)
        self.assertEqual(len(options['searchpath']), 1)
        self.assertEqual(options['searchpath'][0], here)

    def test_options_with_relpath(self):
        import os
        import pyramid_jinja2
        options = self._callFUT(
            {'p.directories': 'foo'}, 'p.', None, pyramid_jinja2)
        self.assertEqual(len(options['searchpath']), 1)
        self.assertEqual(options['searchpath'][0].split(os.sep)[-2:],
                         ['pyramid_jinja2', 'foo'])

    def test_debug_fallback(self):
        options = self._callFUT(
            {
                'debug_templates': 'true',
            },
            'p.', None, None,
        )
        self.assertEqual(options['debug'], True)


class Test_parse_env_options_from_settings(unittest.TestCase):

    def _callFUT(self, settings, prefix=''):
        import pyramid_jinja2
        from pyramid.path import DottedNameResolver
        from pyramid_jinja2.settings import parse_env_options_from_settings
        resolver = DottedNameResolver()
        return parse_env_options_from_settings(
            settings, prefix, resolver.maybe_resolve, pyramid_jinja2,
        )

    def test_most_settings(self):
        from pyramid_jinja2.i18n import GetTextWrapper
        settings = {
            'j2.block_start_string': '<<<',
            'j2.block_end_string': '>>>',
            'j2.variable_start_string': '<|<',
            'j2.variable_end_string': '>|>',
            'j2.comment_start_string': '<+<',
            'j2.comment_end_string': '>+>',
            'j2.line_statement_prefix': '>.>',
            'j2.line_comment_prefix': '^.^',
            'j2.trim_blocks': 'true',
            'j2.newline_sequence': '\r',
            'j2.optimized': 'true',
            'j2.autoescape': 'false',
            'j2.cache_size': '300',
        }
        opts = self._callFUT(settings, 'j2.')
        # test
        self.assertEqual(opts['block_start_string'], '<<<')
        self.assertEqual(opts['block_end_string'], '>>>')
        self.assertEqual(opts['variable_start_string'], '<|<')
        self.assertEqual(opts['variable_end_string'], '>|>')
        self.assertEqual(opts['comment_start_string'], '<+<')
        self.assertEqual(opts['comment_end_string'], '>+>')
        self.assertEqual(opts['line_statement_prefix'], '>.>')
        self.assertEqual(opts['line_comment_prefix'], '^.^')
        self.assertEqual(opts['trim_blocks'], True)
        self.assertEqual(opts['newline_sequence'], '\r')
        self.assertEqual(opts['optimized'], True)
        self.assertEqual(opts['autoescape'], False)
        self.assertEqual(opts['cache_size'], 300)
        self.assertEqual(opts['gettext'].domain, 'pyramid_jinja2')
        self.assertFalse('finalize' in opts)
        self.assertTrue(isinstance(opts['gettext'], GetTextWrapper))

    def test_finalize(self):
        settings = {
            'j2.finalize': 'pyramid_jinja2.tests.test_settings._fake_finalize',
        }
        opts = self._callFUT(settings, 'j2.')
        self.assertTrue(opts['finalize'] is _fake_finalize)

    def test_override_gettext(self):
        class FakeGettextWrapper(object):
            def __init__(self, domain):
                self.domain = domain

        settings = {
            'j2.i18n.gettext':  FakeGettextWrapper,
            'j2.i18n.domain': 'testdomain',
        }
        opts = self._callFUT(settings, 'j2.')
        self.assertTrue(isinstance(opts['gettext'], FakeGettextWrapper))
        self.assertEqual(opts['gettext'].domain, 'testdomain')

    def test_strict_undefined(self):
        from jinja2 import StrictUndefined
        settings = {'j2.undefined': 'strict'}
        opts = self._callFUT(settings, 'j2.')
        self.assertEqual(opts['undefined'], StrictUndefined)

    def test_debug_undefined(self):
        from jinja2 import DebugUndefined
        settings = {'j2.undefined': 'debug'}
        opts = self._callFUT(settings, 'j2.')
        self.assertEqual(opts['undefined'], DebugUndefined)

    def test_default_undefined(self):
        from jinja2 import Undefined
        settings = {'j2.undefined': ''}
        opts = self._callFUT(settings, 'j2.')
        self.assertEqual(opts['undefined'], Undefined)


# This is just a fake top level name that we can pass into maybe_dotted that
# will resolve.
_fake_finalize = object()
