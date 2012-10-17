==============
pyramid_jinja2
==============

Overview
========

:term:`pyramid_jinja2` is a set of bindings that make templates written for the
:term:`Jinja2` templating system work under the :term:`Pyramid` web framework.

Installation
============

Install using setuptools, e.g. (within a virtualenv)::

  $ $myvenv/bin/easy_install pyramid_jinja2

Setup
=====

There are two ways to make sure that ``pyramid_jinja2`` is active.  Both
are completely equivalent:

#) Use the ``includeme`` function via ``config.include``::

    config.include('pyramid_jinja2')

#) If you're using ``pyramid_zcml`` instead of imperative configuration,
   ensure that some ZCML file with an analogue of the following contents is
   executed by your Pyramid application::

    <include package="pyramid_jinja2"/>

Once activated either of these says, the following happens:

#) Files with the ``.jinja2`` extension are considered to be
   :term:`Jinja2` templates.

#) The :func:`pyramid_jinja2.add_jinja2_search_path` directive is added to
   the :term:`configurator` instance.

#) The :func:`pyramid_jinja2.add_jinja2_extension` directive is added to the
   :term:`configurator` instance.

#) The :func:`pyramid_jinja2.get_jinja2_environment` directive is added to the
   :term:`configurator` instance.

#) `jinja2.Environment` is constructed and registered globally.
   
To setup the jinja2 search path either one of the following steps must be taken:

#) Add ``jinja2.directories`` to your ``.ini`` settings file using the pyramid
   asset spec::
  
     jinja2.directories = yourapp:templates

#) Or Alternatively by using the ``add_jinja2_search_path`` directive
   attached to your application's :term:`configurator` instance also using
   the pyramid asset spec::

     config.add_jinja2_search_path("yourapp:templates")

.. warning::

    If you do not explicitly configure your jinja2 search path it will
    default to the root of your application. If the specified template
    is not found in the root of your application and you did not specify
    a package on the template path it will then try to load the template
    path relative to the module's caller package. For example:

    Without the search path configured:

    .. code-block:: text

        @view_config(renderer='templates/mytemplate.jinja2')
    
    With the search path configured:
    
    .. code-block:: text
    
       @view_config(renderer='mytemplate.jinja2')
    
    If you view module is in app.module.view and your template is
    under app/module/templates/mytemplate.jinja2 you can access
    that asset in a few different ways.
    
    Using the full path:
    
    .. code-block:: text
    
      @view_config(renderer="module/templates/mytemplate.jinja2")
    
    Using the package:
    
    .. code-block:: text
    
      @view_config(renderer="app.module:templates/mytemplate.jinja2")
    
    Using the relative path to current package:
    
    .. code-block:: text
    
      @view_config(renderer="templates/mytemplate.jinja2")
    
    You need to be careful when using relative paths though, if
    there is an app/templates/mytemplate.jinja2 this will be
    used instead as jinja2 lookup will first try the path relative
    to the root of the app and then it will try the path relative
    to the current package.

Usage
=====

Once :term:`pyramid_jinja2` been activated ``.jinja2`` templates
can be loaded either by looking up names that would be found on
the :term:`Jinja2` search path or by looking up asset specifications.

Template Lookups
----------------

The default lookup mechanism for templates uses the :term:`Jinja2`
search path. (specified with ``jinja2.directories`` or by using the 
add_jinja2_search_path directive on the :term:`configurator` instance.)

Rendering :term:`Jinja2` templates with a view like this is typically
done as follows (where the ``templates`` directory is expected to
live in the search path):

.. code-block:: python
 :linenos:

 from pyramid.view import view_config
 
 @view_config(renderer='mytemplate.jinja2')
 def myview(request):
     return {'foo':1, 'bar':2}

Rendering templates outside of a view (and without a request) can be
done using the renderer api:

.. code-block:: python
 :linenos:

 from pyramid.renderers import render_to_response
 render_to_response('mytemplate.jinja2', {'foo':1, 'bar':2})

:term:`Template Inheritance`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:term:`Template inheritance` can use asset specs in the same manner as regular
template lookups.  An example:

.. code-block:: html+django
 :linenos:

 <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
 <!-- templates/layout.jinja2 -->

 <html lang="en">
 <html xmlns="http://www.w3.org/1999/xhtml">
 <head>
   <link rel="stylesheet" href="style.css" />
 </head>
 <body>
   <div id="content">{% block content %}{% endblock %}</div>
 </body>

.. code-block:: html+django
 :linenos:

 <!-- templates/root.jinja2 -->
 {% extends "templates/layout.jinja2" %}
 {% block content %}
 <h1>Yes</h1>
 <p>
   Some random paragraph.
 </p>
 {% endblock %}

For further information on :term:`template inheritance` in Jinja2
templates please see http://jinja.pocoo.org/docs/templates/#template-inheritance.

Asset Specification Lookups
---------------------------

Looking up templates via asset specification is a feature specific
to :term:`Pyramid`.  For further info please see `Understanding
Asset Specifications
<http://docs.pylonsproject.org/projects/pyramid/1.0/narr/assets.html#understanding-asset-specifications>`_.
Overriding templates in this style uses the standard
`pyramid asset overriding technique
<http://docs.pylonsproject.org/projects/pyramid/1.0/narr/assets.html#overriding-assets>`_.

Settings
========

Jinja2 derives additional settings to configure its template renderer. Many
of these settings are optional and only need to be set if they should be
different from the default.  The below values can be present in the ``.ini``
file used to configure the Pyramid application (in the ``app`` section
representing your Pyramid app) or they can be passed directly within the
``settings`` argument passed to a Pyramid Configurator.

reload_templates

  ``true`` or ``false`` representing whether Jinja2 templates should be
  reloaded when they change on disk.  Useful for development to be ``true``.

jinja2.directories

  A list of directory names or a newline-delimited string with each line
  representing a directory name.  These locations are where Jinja2 will
  search for templates.  Each can optionally be an absolute resource
  specification (e.g. ``package:subdirectory/``).

jinja2.input_encoding

  The input encoding of templates.  Defaults to ``utf-8``.

jinja2.autoescape

  ``true`` or ``false`` representing whether Jinja2 will autoescape rendered
  blocks. Defaults to ``true``.

jinja2.undefined

  Changes the undefined types that are used when a variable name lookup
  fails. If unset, defaults to ``Undefined`` (silent ignore). Setting it to
  ``strict`` will trigger ``StrictUndefined`` behavior (raising an error,
  this is recommended for development). Setting it to ``debug`` will trigger
  ``DebugUndefined``, which outputs debug information in some cases.
  See http://jinja.pocoo.org/docs/api/#undefined-types

jinja2.extensions

  A list of extension objects or a newline-delimited set of dotted import
  locations where each line represents an extension. `jinja2.ext.i18n` is
  automatically activated.
 
jinja2.i18n.domain

  Pyramid domain for translations. See
  http://pyramid.readthedocs.org/en/latest/glossary.html#term-translation-domain 

jinja2.filters

  A dictionary mapping filter name to filter object, or a newline-delimted
  string with each line in the format ``name = dotted.name.to.filter``
  representing Jinja2 filters.

jinja2.bytecode_caching
  
  ``true`` or ``false`` to enable filesystem bytecode caching. Defaults to ``true``.
  See http://jinja.pocoo.org/docs/api/#bytecode-cache

jinja2.bytecode_caching_directory

  Absolute path to directory to store bytecode caching files. Defaults to
  temporary directory. See
  http://jinja.pocoo.org/docs/api/#jinja2.FileSystemBytecodeCache


Jinja2 Filters
==============

``pyramid_jinja2`` provides two filters.


.. currentmodule:: pyramid_jinja2.filters
.. autofunction:: model_url_filter
.. autofunction:: route_url_filter
.. autofunction:: static_url_filter

To use these filters, configure the settings of ``jinja2.filters``:

.. code-block:: ini
 :linenos:

 [app:yourapp]
 # ... other stuff ...
 jinja2.filters =
     model_url = pyramid_jinja2.filters:model_url_filter
     route_url = pyramid_jinja2.filters:route_url_filter
     static_url = pyramid_jinja2.filters:static_url_filter

And use the filters in template.

.. code-block:: html

 <a href="{{context|model_url('edit')}}">Edit</a>

 <a href="{{'top'|route_url}}">Top</a>

 <link rel="stylesheet" href="{{'yourapp:static/css/style.css'|static_url}}" />

Creating a Jinja2 ``Pyramid`` Project
=====================================

After you've got ``pyramid_jinja2`` installed, you can invoke one of the
following commands to create a Jinja2-based Pyramid project.

On Pyramid 1.0, 1.1, or 1.2::

  $ $myvenv/bin/paster create -t pyramid_jinja2_starter myproject

On Pyramid 1.3::

  $ $myenv/bin/pcreate -s pyramid_jinja2_starter myproject

After it's created, you can visit the ``myproject`` directory and run
``setup.py develop``.  At that point you can start the application like any
other Pyramid application.

This is a good way to see a working Pyramid application that uses Jinja2, even
if you wind up not using the result.

Paster Template I18N
--------------------

The paster template automatically sets up pot/po/mo locale files for use
with the generated project.  

The usual pattern for working with i18n in pyramid_jinja2 is as follows:

.. code-block:: text
 :linenos:

 # make sure Babel is installed
 easy_install Babel 

 # extract translatable strings from *.jinja2 / *.py
 python setup.py extract_messages
 python setup.py update_catalog

 # Translate strings in <mypackage>/locale/<mylocale>/LC_MESSAGES/<myproject>.po
 # and re-compile *.po files
 python setup.py compile_catalog

More Information
================

.. toctree::
 :maxdepth: 1

 glossary.rst
 api.rst

Reporting Bugs / Development Versions
=====================================

Visit http://github.com/Pylons/pyramid_jinja2 to download development or tagged
versions.

Visit http://github.com/Pylons/pyramid_jinja2/issues to report bugs.

Indices and tables
------------------

* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
