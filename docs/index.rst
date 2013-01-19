==============
pyramid_jinja2
==============

.. _overview:

Overview
========

:term:`pyramid_jinja2` is a set of bindings that make templates written for the
:term:`Jinja2` templating system work under the :term:`Pyramid` web framework.

.. _instalation:

Installation
============

Install using setuptools, e.g. (within a virtualenv)::

  $ $myvenv/bin/easy_install pyramid_jinja2

.. _setup:

Setup
=====

There are two ways to make sure that ``pyramid_jinja2`` is active.  Both
are completely equivalent:

#) Use the :py:func:`~pyramid_jinja2.includeme` function via :py:meth:`~pyramid.config.Configurator.include`::

    config = Configurator()
    config.include('pyramid_jinja2')


#) If you're using `pyramid_zcml
   <http://docs.pylonsproject.org/projects/pyramid_zcml/en/latest/>`_
   instead of imperative configuration, ensure that some ZCML file with an
   analogue of the following contents is executed by your Pyramid
   application:

   .. code-block:: xml

        <include package="pyramid_jinja2"/>

Once activated either of these says, the following happens:

#) Files with the :file:`.jinja2` extension are considered to be
   :term:`Jinja2` templates.

#) The :func:`pyramid_jinja2.add_jinja2_search_path` directive is added to
   the :term:`Configurator` instance.

#) The :func:`pyramid_jinja2.add_jinja2_extension` directive is added to the
   :term:`Configurator` instance.

#) The :func:`pyramid_jinja2.get_jinja2_environment` directive is added to the
   :term:`Configurator` instance.

#) :py:class:`jinja2.Environment` is constructed and registered globally.

To setup the Jinja2 search path either one of the following steps must be taken:

#) Add :ref:`setting_jinja2_directories` to your :file:`.ini` settings file using the pyramid asset spec::

     jinja2.directories = yourapp:templates

#) Or Alternatively by using the :func:`~pyramid_jinja2.add_jinja2_search_path`
   directive attached to your application's :term:`Configurator` instance also
   using the pyramid asset spec::

     config.add_jinja2_search_path("yourapp:templates")

.. warning::

    If you do not explicitly configure your Jinja2 search path it will
    default to the root of your application. If the specified template
    is not found in the root of your application and you did not specify
    a package on the template path it will then try to load the template
    path relative to the module's caller package. For example:

    Without the search path configured:

    .. code-block:: python

        @view_config(renderer='templates/mytemplate.jinja2')

    With the search path configured:

    .. code-block:: python

       @view_config(renderer='mytemplate.jinja2')

    If you view module is in app.module.view and your template is
    under :file:`app/module/templates/mytemplate.jinja2` you can access
    that asset in a few different ways.

    Using the full path:

    .. code-block:: python

      @view_config(renderer="module/templates/mytemplate.jinja2")

    Using the package:

    .. code-block:: python

      @view_config(renderer="app.module:templates/mytemplate.jinja2")

    Using the relative path to current package:

    .. code-block:: python

      @view_config(renderer="templates/mytemplate.jinja2")

    You need to be careful when using relative paths though, if
    there is an :file:`app/templates/mytemplate.jinja2` this will be
    used instead as Jinja2 lookup will first try the path relative
    to the root of the app and then it will try the path relative
    to the current package.

.. _usage:

Usage
=====

Once :term:`pyramid_jinja2` been activated :file:`.jinja2` templates
can be loaded either by looking up names that would be found on
the :term:`Jinja2` search path or by looking up asset specifications.

.. _template_lookups:

Template Lookups
----------------

The default lookup mechanism for templates uses the :term:`Jinja2`
search path (specified with :ref:`setting_jinja2_directories` or by using
the :func:`~pyramid_jinja2.add_jinja2_search_path` directive on the
:term:`Configurator` instance).

Rendering :term:`Jinja2` templates with a view like this is typically
done as follows (where the :file:`templates` directory is expected to
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

For further information on :term:`Template Inheritance` in Jinja2
templates please see :ref:`Template Inheritance <jinja2:template-inheritance>`
in Jinja2 documentation.

.. _assets_spec_lookups:

Asset Specification Lookups
---------------------------

Looking up templates via asset specification is a feature specific
to :term:`Pyramid`.  For further info please see :ref:`Understanding
Asset Specifications <pyramid:asset_specifications>`.
Overriding templates in this style uses the standard
:ref:`pyramid asset overriding technique <pyramid:overriding_assets_section>`.

.. _settings:

Internalization (i18n)
----------------------

When :term:`pyramid_jinja2` is included as pyramid application,
:ref:`jinja2.ext.i18n <jinja2:i18n-extension>` is automatically activated.

Be sure to configure `jinja2.i18n.domain` according to `setup.cfg` domain
settings. By default, `jinja2.i18n.domain` is set to the package name of
the pyramid application.


Settings
========

:term:`Jinja2` derives additional settings to configure its template renderer. Many
of these settings are optional and only need to be set if they should be
different from the default.  The below values can be present in the
:file:`.ini` file used to configure the Pyramid application (in the ``app``
section representing your Pyramid app) or they can be passed directly within
the ``settings`` argument passed to a Pyramid Configurator.

Generic Settings
----------------

These setttings correspond to the ones documented in Jinja2.
Set them accordingly.

For reference please see: http://jinja.pocoo.org/docs/api/#high-level-api

.. note ::

    For the boolean settings please use ``true`` or ``false``

jinja2.block_start_string

jinja2.block_end_string

jinja2.variable_start_string

jinja2.variable_end_string

jinja2.comment_start_string

jinja2.comment_end_string

jinja2.line_statement_prefix

jinja2.line_comment_prefix

jinja2.trim_blocks

jinja2.newline_sequence

jinja2.optimized

jinja2.cache_size

jinja2.autoescape
-----------------

Jinja2 autoescape setting.

Possible values: ``true`` or ``false``.

.. warning ::

    By default Jinja2 sets autoescaping to False.

    pyramid_jinja2 sets it to true as it is considered a good security
    practice.


.. _setting_reload_templates:

pyramid.reload_templates
------------------------

This is a Pyramid setting (not a pyramid_jinja2 one)

For usage see :ref:`Pyramid: Automatically Reloading Templates
<pyramid:reload_templates_section>`.

``true`` or ``false`` representing whether Jinja2 templates should be
reloaded when they change on disk.  Useful for development to be ``true``.
This setting sets to Jinja2 ``auto_reload`` setting.

The rationale for using is a differently named setting is: this setting existed
when Pyramid only supported Chameleon and Mako templates and acts uniformly
across the template renderers.

reload_templates
------------------------

.. warning::

   Deprecated as of version 1.5, use :ref:`setting_reload_templates` instead

.. _setting_jinja2_autoreload:

jinja2.auto_reload
------------------

Use Pyramid :ref:`setting_reload_templates` setting.

.. _setting_jinja2_directories:

jinja2.directories
------------------

A list of directory names or a newline-delimited string with each line
representing a directory name.  These locations are where Jinja2 will
search for templates.  Each can optionally be an absolute resource
specification (e.g. ``package:subdirectory/``).

.. _setting_jinja2_input_encoding:

jinja2.input_encoding
---------------------

The input encoding of templates.  Defaults to ``utf-8``.

.. _setting_jinja2_undefined:

jinja2.undefined
----------------

Changes the undefined types that are used when a variable name lookup fails.
If unset, defaults to :py:class:`~jinja2.Undefined` (silent ignore). Setting
it to ``strict`` will trigger :py:class:`~jinja2.StrictUndefined` behavior
(raising an error, this is recommended for development). Setting it to
``debug`` will trigger :py:class:`~jinja2.DebugUndefined`, which outputs
debug information in some cases.  See `Undefined Types <http://jinja.pocoo.org/docs/api/#undefined-types>`_

.. _setting_jinja2_extensions:

jinja2.extensions
-----------------
A list of extension objects or a newline-delimited set of dotted import
locations where each line represents an extension. :ref:`jinja2.ext.i18n
<jinja2:i18n-extension>` is automatically activated.

.. _setting_jinja2_i18n_domain:

jinja2.i18n.domain
------------------
Pyramid domain for translations. See :term:`Translation Domain` in Pyramid
documentation. Defaults to the package name of the pyramid application.

.. _setting_jinja2_filers:

jinja2.filters
--------------

A dictionary mapping filter name to filter object, or a newline-delimted
string with each line in the format::

    name = dotted.name.to.filter

representing :ref:`Jinja2 filters <jinja2:writing-filters>`.

.. _setting_jinja2_globals:

jinja2.globals
---------------

A dictionary mapping global name to global template object,
or a newline-delimited string with each line in the format::

    name = dotted.name.to.globals

representing :ref:`Jinja2 globals <jinja2:the-global-namespace>`

.. _setting_jinja2_tests:

jinja2.tests
------------

A dictionary mapping test name to test object, or a newline-delimted
string with each line in the format::

    name = dotted.name.to.test

representing :ref:`Jinja2 tests <jinja2:writing-tests>`.

.. _setting_jinja2_byte_cache:

jinja2.bytecode_caching
-----------------------

``true`` or ``false`` to enable filesystem bytecode caching. Defaults to
``true``. See :ref:`Bytecode Cache <jinja2:bytecode-cache>` in Jinja2
documentation.

.. _setting_jinja2_byte_cache_dir:

jinja2.bytecode_caching_directory
---------------------------------

Absolute path to directory to store bytecode caching files. Defaults to
temporary directory. See :py:class:`jinja2.FileSystemBytecodeCache`.

.. note::

   :term:`pyramid_jinja2` will attempt to delete the cached files by
   calling :py:func:`jinja2.BytecodeCache.clear` from function
   registered by :py:func:`atexit.register`.

   .. warning ::

      As noted by the `atexit documentation
      <http://docs.python.org/2/library/atexit.html>`__
      the functions registered by the module will only be called
      **upon normal termination**. In case of abnormal program
      termination the files may remain, littering your file system
      (and eating up inodes).

      You are **strongly advised** to consider an additional clean up
      strategy (such as cron) to check and remove such files.


.. _setting_jinja2_newstyle:

jinja2.newstyle
-----------------------

``true`` or ``false`` to enable the use of newstyle gettext calls. Defaults to
``false``.

See `Newstyle Gettext http://jinja.pocoo.org/docs/extensions/#newstyle-gettext`

.. _jinja2_filters:

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
