==============
pyramid_jinja2
==============

.. _overview:

Overview
========

:term:`pyramid_jinja2` is a set of bindings that make templates written for the
:term:`Jinja2` templating system work under the :term:`Pyramid` web framework.


.. _installation:

Installation
============

Install using ``pip``, where ``$VENV`` is the path to a virtual environment.

.. code-block:: bash

  $ $VENV/bin/pip install pyramid_jinja2


.. _setup:

Setup
=====

.. note::

  If you start a project from scratch, consider using the
  :ref:`project template <jinja2_starter_template>` which comes with a
  working setup and sensible defaults.

There are multiple ways to make sure that ``pyramid_jinja2`` is active.
All are completely equivalent:

#) Use the :py:func:`~pyramid_jinja2.includeme` function via
   :py:meth:`~pyramid.config.Configurator.include`.

   .. code-block:: python

        config = Configurator()
        config.include("pyramid_jinja2")

#) Add ``pyramid_jinja2`` to the list of your ``pyramid.includes`` in your
   :file:`.ini` settings file.

   .. code-block:: python

        pyramid.includes =
            pyramid_jinja2

#) If you use :ref:`pyramid_zcml:index` instead of imperative configuration,
   ensure that some ZCML file with an analogue of the following contents is
   executed by your Pyramid application:

   .. code-block:: xml

        <include package="pyramid_jinja2"/>

Once activated in any of these ways, the following happens:

#) Files with the :file:`.jinja2` extension are considered to be
   :term:`Jinja2` templates and a :class:`jinja2.Environment` is registered
   to handle this extension.

#) The :func:`pyramid_jinja2.add_jinja2_renderer` directive is added to the
   :term:`Configurator` instance.

#) The :func:`pyramid_jinja2.add_jinja2_search_path` directive is added to
   the :term:`Configurator` instance.

#) The :func:`pyramid_jinja2.add_jinja2_extension` directive is added to the
   :term:`Configurator` instance.

#) The :func:`pyramid_jinja2.get_jinja2_environment` directive is added to the
   :term:`Configurator` instance.


Preparing for distribution
--------------------------

If you want to make sure your :file:`.jinja2` template files are included in
your package's source distribution (e.g., when using ``python setup.py
sdist``), add ``*.jinja2`` to your :file:`MANIFEST.in`:

.. code-block:: text

    recursive-include yourapp *.ico *.png *.css *.gif *.jpg *.pt *.txt *.mak *.mako *.jinja2 *.js *.html *.xml


Usage
=====

Once ``pyramid_jinja2`` has been activated, :file:`.jinja2` templates can be
used by the Pyramid rendering system.

When used as the ``renderer`` argument of a view, the view must return a
Python ``dict`` which will be passed into the template as the set of available
variables.


Template Lookup Mechanisms
--------------------------

There are several ways to configure ``pyramid_jinja2`` to find your templates.


Asset Specifications
~~~~~~~~~~~~~~~~~~~~

Templates may always be defined using an :term:`asset specification`. These
are strings which define an absolute location of the template relative to
some Python package. For example ``myapp.views:templates/home.jinja2``. These
specifications are supported throughout Pyramid and provide a fool-proof way
to find any supporting assets bundled with your application.

Here's an example view configuration which uses an :term:`asset specification`:

.. code-block:: python
   :linenos:

   @view_config(renderer="mypackage:templates/foo.jinja2")
   def hello_world(request):
       return {"a": 1}

Asset specifications have some significant benefits in Pyramid, as they can be
fully overridden. An add-on package can ship with code that renders using
asset specifications. Later, another package can externally override the
templates without having to actually modify the add-on in any way. See
:ref:`pyramid:overriding_assets_section` for more information.


Caller-Relative Template Lookup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, templates are discovered relative to the caller's package. This
means that if you define a view in a Python module, the templates would
be found relative to the module's directory on the filesystem.

Let's look at an example:

.. code-block:: python
   :linenos:

   @view_config(renderer="templates/mytemplate.jinja2")
   def my_view(request):
       return {"foo": 1, "bar": 2}

Imagine that the above code is in a ``myapp.admin.views`` module. The template
would be relative to that module on the filesystem, as shown below:

.. code-block:: text

   myapp
   |- __init__.py
   `- admin
      |- views.py
      `- templates
         |- base.jinja2
         `- mytemplate.jinja2

Caller-relative lookup avoids naming collisions which can be common in a
search path-based approach.

A caller-relative template lookup is converted to a :term:`asset specification`
underneath the hood. This means that it's almost always possible to override
the actual template in an add-on package without having to fork the add-on
itself. For example, the full asset specification for the view above would be
``myapp.admin.views:templates/mytemplate.jinja2``. This template, or the
entire ``templates`` folder, may be overridden.

.. code-block:: python

   config.override_asset(
       to_override="myapp.admin.views:templates/mytemplate.jinja2",
       override_with="yourapp:templates/sometemplate.jinja2",
    )

See :ref:`pyramid:overriding_assets_section` for more information.


Search Path-Based Template Lookup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When used outside of Pyramid, Jinja2's default lookup mechanism is a search
path. To use a search path within Pyramid, simply define the
``jinja2.directories`` configuration setting, or use the
:func:`~pyramid_jinja2.add_jinja2_search_path` configurator directive.

Rendering :term:`Jinja2` templates with a search path is typically done as
follows:

.. code-block:: python

   @view_config(renderer="mytemplate.jinja2")
   def my_view(request):
       return {"foo": 1, "bar": 2}

If ``mytemplate.jinja2`` is not found in the same directory as the module,
then it will be searched for on the search path. We are now dependent on our
configuration settings to tell us where the template may be located. Commonly
a ``templates`` directory is created at the base of the package and the
configuration file will include the following directive:

.. code-block:: python

    jinja2.directories = mypkg:templates

.. warning::

   It is possible to specify a relative path to the templates folder, such
   as ``jinja2.directories = templates``. This folder will be found relative
   to the first package that includes ``pyramid_jinja2``, which will normally
   be the root of your application. It is always better to be explicit when
   in doubt.

.. note::

   The package that includes ``pyramid_jinja2`` will always be added
   to the search path (in most cases this is the top-level package in your
   application). This behavior may be deprecated or removed in the future.
   It is always better to specify your search path explicitly.


Templates Including Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:term:`Jinja2` allows :term:`template inheritance` as well as other mechanisms
for templates to load each other. The lookup mechanisms supported in these
cases include asset specifications, template-relative names, and normal
template names found on the search path. The search path will always be
consulted if a template cannot be found relative to the parent
template. For example, if you had a template named ``templates/child.jinja2``
that wanted to extend ``templates/base.jinja2``, then it could use
``{% extends "base.jinja2" %}`` and locate the file relative to itself.
Alternatively it could use ``{% extends "templates/base.jinja2" %}`` to find
the template in a ``templates`` sub-folder rooted on the search path. The
template-relative option will always override the search path.

An example:

.. code-block:: html+django
   :linenos:

   <!-- templates/layout.jinja2 -->
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="utf-8">
     <title>Hello World!</title>
     <link rel="stylesheet" href="style.css">
   </head>
   <body>
     <div id="content">{% block content %}{% endblock %}</div>
   </body>
   </html>

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


Adding or Overriding a Renderer
-------------------------------

By default, only templates ending in the ``.jinja2`` file extension are
supported. However, it is very easy to add support for alternative file
extensions using the :func:`pyramid_jinja2.add_jinja2_renderer` directive.

.. code-block:: python

   config.include("pyramid_jinja2")
   config.add_jinja2_renderer(".html")

It would now be possible to use templates named ``foo.html`` and
``foo.jinja2``. Each renderer extension will use its own
:class:`jinja2.Environment`. These alternative renderers can be extended at
runtime using the ``name`` parameter to the other directives such as
:func:`pyramid_jinja2.get_jinja2_environment`.

.. code-block:: python

   config.include("pyramid_jinja2")
   config.add_jinja2_renderer(".html")
   config.add_jinja2_search_path("myapp:templates", name=".html")

It is also possible to set up different renderers that use different search
paths, configuration settings, and environments if necessary. This technique
can come in handy when different defaults are required for rendering templates
with different content types. For example, a plain text email body versus
an HTML page. For this reason, :func:`pyramid_jinja2.add_jinja2_renderer`
accepts an optional parameter ``settings_prefix`` which can point a renderer
at a different group of settings.

.. code-block:: python

   settings = {
       "jinja2.directories": "myapp:html_templates",
       "mail.jinja2.directories": "myapp:email_templates",
   }

   config = Configurator(settings=settings)
   config.include("pyramid_jinja2")
   config.add_jinja2_renderer(".email", settings_prefix="mail.jinja2.")

Now ``foo.email`` will be rendered using the ``mail.jinja2.*`` settings.


Internalization (i18n)
----------------------

When :term:`pyramid_jinja2` is included in a Pyramid application, either
:ref:`jinja2.ext.i18n <jinja2:i18n-extension>` or the extension configured by
``jinja2.i18n_extension`` is automatically activated.

Be sure to configure ``jinja2.i18n.domain`` according to ``setup.cfg`` domain
settings. By default, ``jinja2.i18n.domain`` is set to the name of the
package that included ``pyramid_jinja2``. If no package was found, it will use
``messages``.


.. _settings:

Settings
========

:term:`Jinja2` derives additional settings to configure its template renderer.
Many of these settings are optional and only need to be set if they should be
different from the default.  The below values can be present in the
:file:`.ini` file used to configure the Pyramid application (in the ``app``
section representing your Pyramid app) or they can be passed directly within
the ``settings`` argument passed to a Pyramid Configurator.


Generic Settings
----------------

These settings correspond to the ones documented in Jinja2. Set them
accordingly.

For reference please see: http://jinja.pocoo.org/docs/api/#high-level-api

.. note::

   For the boolean settings, use ``true`` or ``false``.

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

.. warning::

   By default Jinja2 sets ``autoescape`` to ``False``.

   pyramid_jinja2 sets it to ``True`` as it is considered a good security
   practice in a web setting where we want to prevent XSS attacks from
   rendering unsanitized user-generated content. To turn off escaping
   on a case-by-case basis, you may use the ``safe`` filter such as
   ``{{ html_blob|safe }}``.


.. _setting_reload_templates:

pyramid.reload_templates
------------------------

For usage see :ref:`Pyramid: Automatically Reloading Templates
<pyramid:reload_templates_section>`.

``True`` or ``False`` represent whether Jinja2 templates should be reloaded
when they change on disk. In development, it is useful to set it to ``True``.
This setting sets the Jinja2 ``auto_reload`` setting.


reload_templates
----------------

.. warning::

   Deprecated as of version 1.5, use :ref:`setting_reload_templates` instead.


.. _setting_jinja2_autoreload:

jinja2.auto_reload
------------------

Use Pyramid :ref:`setting_reload_templates` setting.

.. _setting_jinja2_directories:


jinja2.directories
------------------

A list of directory names, or a newline-delimited string, where each line
represents a directory name.  These locations are where Jinja2 will search for
templates. Each can optionally be an absolute resource specification (e.g.,
``package:subdirectory/``).


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
(which raises an error, and is recommended for development). Setting it to
``debug`` will trigger :py:class:`~jinja2.DebugUndefined`, which outputs
debug information in some cases. See `Undefined Types
<http://jinja.pocoo.org/docs/api/#undefined-types>`_.


.. _setting_jinja2_extensions:

jinja2.extensions
-----------------

A list of extension objects, or a newline-delimited set of dotted import
locations, where each line represents an extension. Either :ref:`jinja2.ext.i18n
<jinja2:i18n-extension>` or the i18n extension configured using
``jinja2.i18n_extension`` is automatically activated.


.. _setting_jinja2_i18n_extension:

jinja2.i18n_extension
---------------------

The name of the i18n extension to activate. Defaults to
:ref:`jinja2.ext.i18n <jinja2:i18n-extension>`.


.. _setting_jinja2_i18n_domain:

jinja2.i18n.domain
------------------

Pyramid domain for translations. See :term:`pyramid:Translation Domain` in the
Pyramid documentation. Defaults to the name of the package that activated
`pyramid_jinja2` or if that fails it will use ``messages`` as the domain.


.. _setting_jinja2_i18n_gettext:

jinja2.i18n.gettext
-------------------

A subclass of :class:`pyramid_jinja2.i18n.GetTextWrapper` to override
``gettext`` and ``ngettext`` methods in Jinja i18n extension. The Subclass can
be either a dotted name or the subclass itself.


.. _setting_jinja2_filers:

jinja2.filters
--------------

A dictionary mapping a filter name to a filter object, or a newline-delimited
string with each line in the format:

.. code-block:: python

    name = dotted.name.to.filter

representing :ref:`Jinja2 filters <jinja2:writing-filters>`.


.. _setting_jinja2_globals:

jinja2.globals
--------------

A dictionary mapping a global name to a global template object, or a
newline-delimited string with each line in the format:

.. code-block:: python

    name = dotted.name.to.globals

representing :ref:`Jinja2 globals <jinja2:global-namespace>`


.. _setting_jinja2_tests:

jinja2.tests
------------

A dictionary mapping a test name to a test object, or a newline-delimited
string with each line in the format:

.. code-block:: python

    name = dotted.name.to.test

representing :ref:`Jinja2 tests <jinja2:writing-tests>`.


.. _setting_jinja2_byte_cache:

jinja2.bytecode_caching
-----------------------

If set to ``true``, a file system bytecode cache will be configured in a
directory determined by :ref:`setting_jinja2_byte_cache_dir`. To configure
other types of bytecode caching, ``jinja2.bytecode_caching`` may also be set
directly to an instance of :class:`jinja2.BytecodeCache`. However doing so
cannot be done in a paste ``.ini`` file and it must be done programmatically.
By default, no bytecode cache is configured.

.. versionchanged:: 1.10

   Previously, ``jinja2.bytecode_caching`` defaulted to ``true``.

Note that configuring a filesystem bytecode cache will (not surprisingly)
generate files in the cache directory.  As templates are changed, some of these
will become stale, pointless wastes of disk space. You are advised to consider
a clean up strategy (such as a cron job) to check for and remove such files.

See the :ref:`Jinja2 Documentation <jinja2:bytecode-cache>` for more
information on bytecode caching.

.. versionchanged:: 1.10

   Previously, an ``atexit`` callback which called
   :py:meth:`jinja2.BytecodeCache.clear` was registered in an effort
   to delete the cache files.  This is no longer done.


.. _setting_jinja2_byte_cache_dir:

jinja2.bytecode_caching_directory
---------------------------------

Absolute path to directory to store bytecode cache files. Defaults to the
system temporary directory. This is only used if ``jinja2.bytecode_caching`` is
set to ``true``.


.. _setting_jinja2_newstyle:

jinja2.newstyle
---------------

``true`` or ``false`` to enable the use of ``newstyle`` ``gettext`` calls.
Defaults to ``false``.

See :ref:`jinja2:newstyle-gettext`.


.. _setting_jinja2_finalize:

jinja2.finalize
---------------

A callable or a dotted-import string.


.. _jinja2_filters:

Jinja2 Filters
==============

``pyramid_jinja2`` comes with Pyramid routing specific filters. All Jinja2
built-in filters are enabled in templates. Read how :ref:`jinja2:filters` work
in Jinja2.


Installing filters
------------------

To use these filters, configure the settings of ``jinja2.filters``:

.. code-block:: ini
   :linenos:

   [app:yourapp]
   # ... other stuff ...
   jinja2.filters =
       model_url = pyramid_jinja2.filters:model_url_filter
       route_url = pyramid_jinja2.filters:route_url_filter
       static_url = pyramid_jinja2.filters:static_url_filter


Filter reference
----------------

.. currentmodule:: pyramid_jinja2.filters
.. autofunction:: resource_url_filter
.. autofunction:: model_url_filter
.. autofunction:: route_url_filter
.. autofunction:: static_url_filter
.. autofunction:: model_path_filter
.. autofunction:: route_path_filter
.. autofunction:: static_path_filter


.. _jinja2_starter_template:

Creating a Jinja2 Pyramid project
=================================

After you have installed ``pyramid_jinja2``, you can invoke the following
command to create a Jinja2-based Pyramid project from its included scaffold.

.. code-block:: bash

  $ $VENV/bin/pcreate -s pyramid_jinja2_starter myproject

After it's created, you can visit the ``myproject`` directory and install the
project in development mode.

.. code-block:: bash

   $ cd myproject
   $ $VENV/bin/pip install -e .

At this point you can start the application like any other Pyramid application.

.. code-block:: bash

   $ $VENV/bin/pserve development.ini

This is a good way to see a working Pyramid application that uses Jinja2, even
if you do not end up using the result.

.. seealso:: See also :ref:`pyramid:project_narr`.


Running tests for your application
----------------------------------

The scaffold provides a convenience for the developer to install ``pytest`` and
``pytest-cov`` as the test runner and test coverage. To run unit tests for your
application, you must first install the testing dependencies.

.. code-block:: bash

   $ $VENV/bin/pip install -e ".[testing]"

Once the testing requirements are installed, then you can run the tests using
the ``py.test`` command that was just installed in the ``bin`` directory of
your virtual environment. The ``-q`` option means "quiet" output, and the
``--cov`` option includes test coverage.

.. code-block:: bash

   $ $VENV/bin/py.test -q --cov

The scaffold includes configuration defaults for ``py.test`` and test coverage.
These configuration files are ``pytest.ini`` and ``.coveragerc``, located at
the root of your package. Without these defaults, we would need to specify the
path to the module on which we want to run tests and coverage.

.. code-block:: bash

   $ $VENV/bin/py.test -q --cov=myproject myproject/tests.py

.. seealso:: See py.test's documentation for :ref:`pytest:usage` or invoke
   ``py.test -h`` to see its full set of options.


pcreate template i18n
---------------------

The pcreate template automatically sets up pot/po/mo locale files for use with
the generated project.

The usual pattern for working with i18n in pyramid_jinja2 is as follows:

.. code-block:: bash

   # make sure Babel is installed
   $ $VENV/bin/pip install Babel

   # extract translatable strings from *.jinja2 / *.py
   $ $VENV/bin/python setup.py extract_messages
   $ $VENV/bin/python setup.py update_catalog

   # Translate strings in <mypackage>/locale/<mylocale>/LC_MESSAGES/<myproject>.po
   # and re-compile *.po files
   $ $VENV/bin/python setup.py compile_catalog

If you see the following output:

.. code-block:: text

   running compile_catalog
   1 of 1 messages (100%) translated in myproject/locale/de/LC_MESSAGES/myproject.po
   catalog myproject/locale/de/LC_MESSAGES/myproject.po is marked as fuzzy, skipping
   1 of 1 messages (100%) translated in myproject/locale/fr/LC_MESSAGES/myproject.po
   catalog myproject/locale/fr/LC_MESSAGES/myproject.po is marked as fuzzy, skipping

When an item is marked as fuzzy, then you should review your `.po` files to
make sure translations are correct. Fuzzy is not exact matching, but matches
most of a word (its root) or phrase.

When you are satisfied that the translations are good, you can either remove
the line marked with `#, fuzzy` immediately above its related `msgid` line
(preferred) or force Babel to compile the message catalog with the `-f` flag.

.. code-block:: bash

   $ $VENV/bin/python setup.py compile_catalog -f

Assuming you have already created a project following the instructions under
:ref:`jinja2_starter_template`, and started your application with ``pserve``,
then you should be able to view the various translations. Simply append a GET
parameter, such as http://localhost:6543/?_LOCALE_=de for German,
http://localhost:6543/?_LOCALE_=fr for French, or
http://localhost:6543/?_LOCALE_=en for English. The default language does not
require GET parameter.

The application could set the user's language preference with a cookie based on
request parameters sent on the first request. Alternatively, and usually as a
fallback, the application could read the web browser's `Accept-Language` header
sent with each request and set the appropriate language. For example:

.. code-block:: python

    @subscriber(NewRequest)
    def prepare_env(event):
        request = event.request
        # set locale depending on browser settings
        settings = request.registry.settings
        locale = settings.get("pyramid.default_locale_name", "en")
        available = [loc["code"] for loc in AVAILABLE_LOCALES]
        if request.accept_language:
            accepted = request.accept_language
            locale = accepted.best_match(available, locale)
        request._LOCALE_ = locale


More Information
================

.. toctree::
   :maxdepth: 1

   api.rst
   changes.rst
   glossary.rst


Reporting Bugs / Development Versions
=====================================

Visit https://github.com/Pylons/pyramid_jinja2 to download development or tagged
versions.

Visit https://github.com/Pylons/pyramid_jinja2/issues to report bugs.


Indices and tables
------------------

* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
