from jinja2 import nodes
from jinja2.ext import Extension

class TestExtension(Extension):
    tags = set(['test_ext'])
    def parse(self, parser): return nodes.Const("This is test extension")
