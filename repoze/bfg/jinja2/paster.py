from paste.script.templates import Template
from paste.util.template import paste_script_template_renderer

class Jinja2ProjectTemplate(Template):
    _template_dir = 'paster_template'
    summary = 'repoze.bfg jinja2 starter project'
    template_renderer = staticmethod(paste_script_template_renderer)
