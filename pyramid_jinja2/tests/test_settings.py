# -*- coding: utf-8 -*-

from unittest import TestCase


class DummyRendererInfo(object):

    def __init__(self, registry):
        self.name = 'helloworld.jinja2'
        self.package = None
        self.registry = registry
        self.settings = registry.settings


class DummyRegistry(object):

    def __init__(self, settings=None):
        self.settings = \
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
             'jinja2.autoescape': True,
             'jinja2.cache_size': 300
            }

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

    def test_settings(self):
        from pyramid_jinja2 import IJinja2Environment

        registry = DummyRegistry()
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
        self.assertEqual(environ.autoescape, True)
        self.assertEqual(environ.cache.capacity, 300)
