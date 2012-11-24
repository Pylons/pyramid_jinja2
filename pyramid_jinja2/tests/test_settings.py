# -*- coding: utf-8 -*-

# TODO: add a test for defaults once we decouple get and build of
#       _get_or_build_default_environment function

from unittest import TestCase


class DummyRendererInfo(object):

    def __init__(self, registry):
        self.name = 'helloworld.jinja2'
        self.package = None
        self.registry = registry
        self.settings = registry.settings


class DummyRegistry(object):

    def __init__(self, settings=None):

        # do the mutable default
        self.settings = settings
        if self.settings is None:
            self.settings = {}

        self.impl = None

    def queryUtility(self, iface):
        return self.impl

    def registerUtility(self, impl, iface):
        self.impl = impl


class Test_settings(TestCase):

    def _callFUT(self, info):
        # initialize renderer with dummy info containing our configs
        from pyramid_jinja2 import renderer_factory
        return renderer_factory(info)

    def test_settings_defaults(self):
        from pyramid_jinja2 import IJinja2Environment
        from pyramid_jinja2 import _JINJA2_ENVIRONMENT_DEFAULTS

        # do not setup the registry with any settings so we get the defaults
        registry = DummyRegistry()
        # provide minimum amount of information to the renderer
        info = DummyRendererInfo(registry)
        # call renderer so the Jinja2 environment is created
        self._callFUT(info)
        # get Jinja2 environment
        environ = registry.queryUtility(IJinja2Environment)
        # iterate over the defaults and test them
        # (fyi, this will not work for cache_size)
        for key_name in _JINJA2_ENVIRONMENT_DEFAULTS:
            self.assertEqual(getattr(environ, key_name),
                             _JINJA2_ENVIRONMENT_DEFAULTS[key_name])

    def test_most_settings(self):
        from pyramid_jinja2 import IJinja2Environment

        registry = DummyRegistry(
            {'jinja2.block_start_string': '<<<',
             'jinja2.block_end_string': '>>>',
             'jinja2.variable_start_string': '<|<',
             'jinja2.variable_end_string': '>|>',
             'jinja2.comment_start_string': '<+<',
             'jinja2.comment_end_string': '>+>',
             'jinja2.line_statement_prefix': '>.>',
             'jinja2.line_comment_prefix': '^.^',
             'jinja2.trim_blocks': True,
             'jinja2.newline_sequence': '\r',
             'jinja2.optimized': False,
             'jinja2.autoescape': False,
             'jinja2.cache_size': 300
            })

        # provide minimum amount of information to the renderer
        info = DummyRendererInfo(registry)
        # call renderer so the Jinja2 environment is created
        self._callFUT(info)
        # get Jinja2 environment
        environ = registry.queryUtility(IJinja2Environment)

        # test
        self.assertEqual(environ.block_start_string, '<<<')
        self.assertEqual(environ.block_end_string, '>>>')
        self.assertEqual(environ.variable_start_string, '<|<')
        self.assertEqual(environ.variable_end_string, '>|>')
        self.assertEqual(environ.comment_start_string, '<+<')
        self.assertEqual(environ.comment_end_string, '>+>')
        self.assertEqual(environ.line_statement_prefix, '>.>')
        self.assertEqual(environ.line_comment_prefix, '^.^')
        self.assertEqual(environ.trim_blocks, True)
        self.assertEqual(environ.newline_sequence, '\r')
        self.assertEqual(environ.optimized, False)
        self.assertEqual(environ.autoescape, False)
        # this is where cache_size gets set in Jinja2
        self.assertEqual(environ.cache.capacity, 300)
