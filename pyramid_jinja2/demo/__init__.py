from pyramid.config import Configurator
from pyramid.i18n import (
    get_localizer,
    get_locale_name,
    TranslationStringFactory
    )


_ = TranslationStringFactory('messages')


def root_view(request):
    request.locale_name = 'fr'
    localizer = get_localizer(request)
    return {
        'pyramid_translated': localizer.translate(_('Hello World')),
        'locale_name': get_locale_name(request)
        }


def app(global_settings, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_route(name='root',
                     pattern='/',
                     view=root_view,
                     renderer='helloworld.jinja2')
    config.add_translation_dirs('pyramid_jinja2.demo:locale/')
    return config.make_wsgi_app()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    port = 8080
    httpd = make_server('', port, app({}, **{
                'DEBUG': True,
                'reload_templates': True,
                }))
    print 'Listening on at http://127.0.0.1:%i' % port
    # Serve until process is killed
    httpd.serve_forever()
