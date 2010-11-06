pyramid_jinja2
==============

``pyramid_jinja2`` is a set of bindings that make templates written for the
:term:`Jinja2` templating system work under the :term:`Pyramid` web framework.

Activating the Extension
------------------------

There are two ways to make sure that the ``pyramid_jinja2`` extension is
active.  Both are completely equivalent.

#) Ensure that some ZCML file with an analogue of the following
   contents is executed by your Pyramid application::

    <include package="pyramid_jinja2"/>

#) Call the ``add_renderer`` method of a Configurator in your
   application during configuration::

    from pyramid_jinja2 import renderer_factory
    config.add_renderer('.jinja2', renderer_factory)
 
In either case, files with the ``.jinja2`` extension are now considered to be
Jinja2 templates.

Once the extension is active, add the following to the application section of
your Pyramid application's ``.ini`` file:

.. code-block:: ini
   :linenos:

   [app:yourapp]
   # ... other stuff ...
   jinja2.directories = myapp:templates
                        anotherpackage:templates

This configures the set of directories searched by Jinja.  The portion of each
directory argument before the colon is a package name.  The remainder is a
subpath within the package which houses Jinja2 templates.  Adding more than one
directory forms a search path.

High-Level API
--------------

Once the extension is configured, to use Jinja2 templates, use any of the three
Pyramid renderer-related functions : ``pyramid.renderers.get_renderer``,
``pyramid.renderers.render``, or ``pyramid.renderers.render_to_response``.

From within a Pyramid view function, you might do::

  from webob import Response

  from pyramid.renderers import get_renderer
  template = get_renderer('foo.jinja2')
  return Response(template.render(foo=1))

Or::

  from pyramid.renderers import render
  s = render_template('foo.jinja2', {'foo':1})
  return Response(s)

Or::

  from pyramid.jinja2 import render_to_response
  return render_to_response('foo.jinja2', {'foo':1})

All of these examples are equivalent.  The first argument passed in to each of
``get_renderer``, ``render_template``, or ``render_to_response`` represents the
template location.  It can be either a full system file path, or can be a file
path relative to one of the directories named by ``jinja2.directories``.

``pyramid_jinja2`` can also act as a "renderer" for a view when its
``configure.zcml`` file is included within the Pyramid application you're
developing::

  from pyramid.view import view_config

  @view_config(renderer='foo.jinja2')
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

  $ paster create -t bin/paster pyramid_jinja2_starter

This is a good way to see a working Pyramid application that uses Jinja2, even
if you wind up not using the result.

Reporting Bugs / Development Versions
-------------------------------------

Visit http://github.com/Pylons/pyramid_jinja2 to download development or tagged
versions.

Visit http://github.com/Pylons/pyramid_jinja2/issues to report bugs.

Indices and tables
------------------

* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
