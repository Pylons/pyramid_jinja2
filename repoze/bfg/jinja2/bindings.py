from os.path import getmtime

from webob import Response

from zope.component import queryUtility

from repoze.bfg.interfaces import ISettings
from repoze.bfg.path import caller_path

from jinja2.loaders import FunctionLoader
from jinja2 import Environment

def _auto_reload():
    settings = queryUtility(ISettings)
    auto_reload = (settings and settings.reload_templates) or False
    return auto_reload
    
def load_template(path):
    path = caller_path(path)
    try:
        data = open(path, 'rb').read()
        mtime = getmtime(path)
    except (OSError, IOError):
        return None
    def uptodate():
        try:
            return getmtime(path) == mtime
        except (OSError, IOError):
            return False
    return unicode(data, 'utf-8'), path, uptodate

class BfgLoader(FunctionLoader):
    """ 
    Extends jinja2.loaders.FunctionLoader with configurable auto-reloading.    
    """
    auto_reload = None
    def get_source(self, environment, template):
        if self.auto_reload is None:
            self.auto_reload = _auto_reload()
        environment.auto_reload = self.auto_reload
        return super(BfgLoader, self).get_source(environment, template)
        
env = Environment(loader=BfgLoader(load_template))

def get_template(path):
    """ Return a z3c.pt template object at the package-relative path
    (may also be absolute) """
    path = caller_path(path)
    return env.get_template(path)

def render_template(path, **kw):
    """ Render a z3c.pt (ZPT) template at the package-relative path
    (may also be absolute) using the kwargs in ``*kw`` as top-level
    names and return a string. """
    path = caller_path(path)
    template = get_template(path)
    return template.render(**kw)

def render_template_to_response(path, **kw):
    """ Render a z3c.pt (ZPT) template at the package-relative path
    (may also be absolute) using the kwargs in ``*kw`` as top-level
    names and return a Response object. """
    path = caller_path(path)
    result = render_template(path, **kw)
    return Response(result)

