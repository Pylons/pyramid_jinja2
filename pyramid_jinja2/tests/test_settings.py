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


class Test_settings(TestCase):
    """
    Test case for settings.
    """

    def setUp(self):
        # get test config
        self.config = testing.setUp()

    def tearDown(self):
        # tear the config down and delete it
        testing.tearDown()
        del self.config

    def _callFUT(self, info):
        # initialize renderer with dummy info containing our configs
        from pyramid_jinja2 import renderer_factory
        renderer_factory(info)

    def test_settings(self):
        from pyramid_jinja2 import IJinja2Environment

        # configure test settings
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

        # provide minimum amount of information to the renderer
        info = DummyRendererInfo(
            {'name': 'helloworld.jinja2',
             'package': None,
             'registry': self.config.registry,
             'settings': self.config.registry.settings
             })

        # call renderer so the Jinja2 environment is created
        self._callFUT(info)
        # get Jinja2 environment
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
