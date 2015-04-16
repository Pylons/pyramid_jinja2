from pyramid import i18n
from pyramid.threadlocal import get_current_request


class GetTextWrapper(object):
    """Implements `gettext` and `ngettext` functions for
    :meth:`jinja2.Environment.install_gettext_translations`
    """

    def __init__(self, domain):
        self.domain = domain

    @property
    def localizer(self):
        return i18n.get_localizer(get_current_request())

    def gettext(self, message):
        """Implements jinja.ext.i18n `gettext` function"""
        return self.localizer.translate(message,
                                        domain=self.domain)

    def ngettext(self, singular, plural, n):
        """Implements jinja.ext.i18n `ngettext` function"""
        return self.localizer.pluralize(singular, plural, n,
                                        domain=self.domain)
