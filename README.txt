`Jinja2 <http:http://jinja.pocoo.org>`_ bindings for Pyramid
============================================================

These are bindings for the `Jinja2 templating system`_ for the `Pyramid
<http://pylonshq.com/pyramid>`_ web framework.

Ensuring the Jinja2 Renderer Extension is Active
------------------------------------------------

There are two ways to make sure that the ``pyramid_jinja2`` extension is
active.  Both are completely equivalent.

#) Ensure that some ZCML file with an analogue of the following
   contents is executed::

    <include package="pyramid_jinja2"/>

#) Call the ``add_renderer`` method of a Configurator in your
   application:

   from pyramid_jinja2 import renderer_factory
   config.add_renderer(.'jinja2', renderer_factory)

In either case, files with the ``.jinja2`` extension are now considered to be
Jinja2 templates.

High-Level API
--------------

Once the extension is configured, to use the Jinja2 package for Pyramid, use
any of the three Pyramid renderer-related functions : ``get_renderer``,
``render``, and ``render_to_response``.

From within a Pyramid view function, you might do::

  from webob import Response

  from pyramid.renderers import get_renderer
  template = get_renderer('templates/foo.jinja2')
  return Response(template.render(foo=1))

Or::

  from pyramid.renderers import render
  s = render_template('templates/foo.jinja2', {'foo':1})
  return Response(s)

Or::

  from Pyramid.jinja2 import render_to_response
  return render_to_response('templates/foo.jinja2', {'foo':1})

All of these examples are equivalent.  The first argument passed in to each of
``get_renderer``, ``render_template``, or ``render_to_response`` represents the
template location.  It can be either a full system file path, or can be a file
path relative to the package in which the view function is defined (as shown
above).

``pyramid_jinja2`` can also act as a "renderer" for a view when its
``configure.zcml`` file is included within the Pyramid application you're
developing::

  from pyramid.view import view_config

  @view_config(renderer='templates/foo.jinja2')
  def aview(request):
      return {'foo':1}

See the generated ``pyramid_jinja2_starter`` paster template for an
example of using the renderer facility.

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

  $ easy_install pyramid_jinja2

Creating a Jinja2 ``Pyramid`` Project
----------------------------------------

After you've got ``pyramid_jinja2`` installed, you can invoke the following
command to create a Jinja2-based Pyramid project::

  $ paster create -t bin/paster create -t pyramid_jinja2_starter

Reporting Bugs / Development Versions
-------------------------------------

Visit http://bugs.repoze.org to report bugs.  Visit
http://svn.repoze.org to download development or tagged versions.


