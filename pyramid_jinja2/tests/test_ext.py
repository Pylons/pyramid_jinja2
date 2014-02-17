import unittest
from .base import Base


class TestExtensions(Base, unittest.TestCase):

    def test_custom_extension(self):
        from pyramid_jinja2 import create_environment_from_options
        from pyramid_jinja2.settings import parse_env_options_from_settings

        options = {
            'extensions': 'pyramid_jinja2.tests.extensions.TestExtension',
        }
        settings = parse_env_options_from_settings(options, '', None, None)
        env = create_environment_from_options(settings, {})
        ext = env.extensions[
            'pyramid_jinja2.tests.extensions.TestExtension']
        import pyramid_jinja2.tests.extensions
        self.assertEqual(ext.__class__,
                         pyramid_jinja2.tests.extensions.TestExtension)

    def test_i18n(self):
        from pyramid_jinja2 import create_environment_from_options
        from pyramid_jinja2.settings import parse_env_options_from_settings

        settings = parse_env_options_from_settings({}, '', None, None)
        env = create_environment_from_options(settings, {})

        self.assertTrue(hasattr(env, 'install_gettext_translations'))

        self.config.add_translation_dirs('pyramid_jinja2.tests:locale/')
        self.request.locale_name = 'en'
        template = env.get_template(
            'pyramid_jinja2.tests:templates/i18n.jinja2')
        self.assertEqual(template.render(),
                         'some untranslated text here\nyay it worked!')


class GetTextWrapperTests(unittest.TestCase):

    def test_it(self):
        from pyramid_jinja2.i18n import GetTextWrapper

        class MyGetTextWrapper(GetTextWrapper):
            class localizer:
                @staticmethod
                def translate(s, domain):
                    return s

                @staticmethod
                def pluralize(s1, s2, n, domain):
                    return s2

            def __init__(self):
                GetTextWrapper.__init__(self, 'messages')

        self.assertEqual(MyGetTextWrapper().gettext('foo'), 'foo')
        self.assertEqual(MyGetTextWrapper().ngettext('foo', 'foos', 3), 'foos')
