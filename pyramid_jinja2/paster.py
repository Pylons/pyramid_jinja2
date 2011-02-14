from paste.util.template import paste_script_template_renderer
from pyramid import paster


class Jinja2ProjectTemplate(paster.PyramidTemplate):
    _template_dir = 'paster_template'
    summary = 'pyramid jinja2 starter project'
    template_renderer = staticmethod(paste_script_template_renderer)
