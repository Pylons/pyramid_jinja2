try:  # pragma: no cover (pyramid 1.0.X)
    # "pyramid.paster.paste_script_template_renderer" doesn't exist past 1.0.X
    from pyramid.paster import PyramidTemplate, paste_script_template_renderer
except ImportError:  # pragma: no cover
    try:  # pragma: no cover (pyramid 1.1.X, 1.2.X)
        # trying to import "paste_script_template_renderer" fails on 1.3.X
        from pyramid.scaffolds import PyramidTemplate, paste_script_template_renderer
    except ImportError:  # pragma: no cover (pyramid >=1.3a2)
        paste_script_template_renderer = None
        from pyramid.scaffolds import PyramidTemplate


class Jinja2ProjectTemplate(PyramidTemplate):
    _template_dir = "jinja2_starter"
    summary = "Pyramid Jinja2 starter project"
    template_renderer = staticmethod(paste_script_template_renderer)
