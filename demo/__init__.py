from pyramid.config import Configurator
from pyramid.i18n import TranslationStringFactory, get_locale_name, get_localizer

_ = TranslationStringFactory("messages")


def root_view(request):
    request.locale_name = "fr"
    localizer = get_localizer(request)
    return {
        "pyramid_translated": localizer.translate(_("Hello World")),
        "locale_name": get_locale_name(request),
    }


def app(global_settings, **settings):
    config = Configurator(settings=settings)
    config.include("pyramid_jinja2")
    config.add_route(name="root", pattern="/")
    config.add_view(root_view, renderer="helloworld.jinja2")
    config.add_translation_dirs("demo:locale/")
    return config.make_wsgi_app()


class Mainer(object):
    import wsgiref.simple_server

    make_server = wsgiref.simple_server.make_server

    def main(self):
        port = 8080
        app_config = {"DEBUG": True, "reload_templates": True}
        pyramid_app = app({}, **app_config)
        httpd = self.make_server("", port, pyramid_app)
        # Serve until process is killed
        httpd.serve_forever()


main = Mainer().main

if __name__ == "__main__":
    main()  # pragma: nocover
