# -*- coding: utf-8 -*-

"""
Tests for jinja2 settings.
"""

from unittest import TestCase
from pyramid import testing


class DummyRendererInfo(object):
    """
    RendererInfo fixture.
    """
    def __init__(self, kw):
        self.__dict__.update(kw)
        if 'registry' in self.__dict__:
            self.settings = self.registry.settings


class Test_settings(TestCase):
    """
    Test case for settings.
    """

    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
        self.request.registry = self.config.registry

    def tearDown(self):
        testing.tearDown()
        del self.config

    def _callFUT(self, info):
        from pyramid_jinja2 import renderer_factory
        return renderer_factory(info)

    def test_settings(self):
        from pyramid_jinja2 import IJinja2Environment
        from pyramid_jinja2.tests.base import DummyRendererInfo
        self.config.registry.settings.update(
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
            })

        info = DummyRendererInfo(
            {'name': 'helloworld.jinja2',
             'package': None,
             'registry': self.config.registry
             })

        # call renderer so the Jinja2 environment is created
        self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)

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
