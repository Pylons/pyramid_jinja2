``repoze.bfg`` bindings for `Jinja2 <http:http://jinja.pocoo.org>`_
===================================================================

These are bindings for the `Jinja2
<http://jinja.pocoo.org/2/documentation>`_ templating system for
``repoze.bfg``.

High-Level API
--------------

The API follows the pattern of the "default" template API for
``repoze.bfg``, which includes three functions: ``get_template``,
``render_template``, and ``render_template_to_response``.  From within
a repoze.bfg view function, you might do::

  from webob import Response

  from repoze.bfg.jinja2 import get_template
  template = get_template('templates/foo.jinja2')
  return Response(template.render(foo=1))

Or::

  from repoze.bfg.jinja2 import render_template
  s = render_template('templates/foo.jinja2')
  return Response(s)

Or::

  from repoze.bfg.jinja2 import render_template_to_response
  return render_template_to_response('templates/foo.jinja2')

All of these examples are equivalent.  The string passed in to each of
them can be either a full system file path, or can be a file path
relative to the package in which the view function is defined (as
shown above).

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

  $ easy_install -i http://dist.repoze.org/lemonade/dev/simple repoze.bfg.jinja2

Reporting Bugs / Development Versions
-------------------------------------

Visit http://bugs.repoze.org to report bugs.  Visit
http://svn.repoze.org to download development or tagged versions.


