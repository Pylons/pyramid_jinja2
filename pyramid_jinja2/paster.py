from pyramid_jinja2.compat import PY3

if not PY3:
    from paste.util.template import paste_script_template_renderer
    try:
        from pyramid.scaffolds import PyramidTemplate # pyramid 1.1+
    except ImportError: # pragma: no cover
        from pyramid.paster import PyramidTemplate # pyramid 1.0


    class Jinja2ProjectTemplate(PyramidTemplate):
        _template_dir = 'paster_template'
        summary = 'pyramid jinja2 starter project'
        template_renderer = staticmethod(paste_script_template_renderer)
