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
        request = get_current_request()
        try:
            return request.localizer
        except AttributeError:  # pragma: nocover (pyramid < 1.5)
            return i18n.get_localizer(request)

    def gettext(self, message, mapping=None):
        """Implements jinja.ext.i18n `gettext` function"""
        return self.localizer.translate(message, domain=self.domain, mapping=mapping)

    def ngettext(self, singular, plural, n):
        """Implements jinja.ext.i18n `ngettext` function"""
        return self.localizer.pluralize(singular, plural, n, domain=self.domain)
