2.9.1 (2022-03-12)
==================

- Fix package metadata. No changes from 2.9.

2.9 (2022-03-12)
================

- Drop Python 3.6 support.

- Add Python 3.9 and 3.10 support.

- Refactor project structure to make wheel distribution smaller.

- Blackify the codebase.

- Use the newer ``@jinja2.pass_context`` in favor of the deprecated
  ``@jinja2.contextfilter``.
  See https://github.com/Pylons/pyramid_jinja2/pull/159

2.8 (2019-01-25)
================

- Drop Python 3.3 support.

- Add Python 3.6 and 3.7 support.

- Support the ``mapping`` argument in the injected ``gettext`` function.
  See https://github.com/Pylons/pyramid_jinja2/pull/143

2.7 (2016-11-15)
================

- Drop Python 2.6 and 3.2 support.

- Add Python 3.5 support.

- #123: Switch to pytest and pip for testing and installation in the
  documentation and scaffold. nose and coverage are still used in the core
  pyramid_jinja2 package [stevepiercy].

- Prefer ``resource_url`` over deprecated ``model_url``. Pyramid has changed
  its vocabulary, so let's reflect the changes. [Mikko Ohtamaa]

- Support a dotted path to a gettext wrapper for the ``jinja2.i18n.gettext``
  setting. [mmerickel]

2.6.2 (2016-01-23)
==================

- Officially drop support for Python 3.2, test under Python 3.5 and pypy3
  [Domen Kozar]

2.6.1 (2016-01-20)
==================

- Don't include .pyc in wheel file [Domen Kozar]

2.6 (2016-01-20)
================

- #116: Update scaffold to be consistent with Pyramid's default scaffolds
  [stevepiercy]

2.5 (2015-04-16)
================

- #106: Allow specifying a custom pyramid_jinja.i18n.GetTextWrapper [dstufft]

2.4 (2015-03-27)
================

- #105: Support ``jinja2.finalize`` configuration setting. [dstufft]

- #94: Fix loading of templates with relative names on Windows [zart]

- Support Python 3.4 [mmerickel]

- Improve scaffold [marioidival]

- #98: Avoid get_current_request where possible [housleyjk]

- #99: Add resource_path filter [javex]

2.3.3 (2014-07-02)
==================

- #91: Fix a recursion error while attempting to include a template with the
  same name as one of the parents that was already loaded. [mmerickel]

2.3.2 (2014-06-13)
==================

- Fix 2.3.1 brownbag release. It had some erroneous didn't-mean-to-push
  changes that are now solved. Brought coverage back up to 100%.

2.3.1 (2014-06-13)
==================

- Improve the template-relative searchpath logic to search more possibilities
  in the include-chain built up from templates including or extending
  other templates. The logic for when the chain was longer than just one
  template including another template was broken.

2.3 (2014-05-30)
================

- Require ``pyramid_jinja2`` to be included even when using
  ``pyramid_jinja2.renderer_factory``. It is now a thin wrapper around the
  default renderer and can be used to share the same settings with another
  file extension. [mmerickel]

Backward Incompatible Changes
-----------------------------

- ``pyramid_jinja2`` **must** be included into the ``Configurator`` in order
  to use ``pyramid_jinja2.renderer_factory`` otherwise you may see the
  exception::

    ValueError: As of pyramid_jinja2 2.3, the use of the
    "pyramid_jinja2.renderer_factory" requires that pyramid_jinja2 be
    configured via config.include("pyramid_jinja2") or the equivalent
    "pyramid.includes" setting.

  The fix is to include ``pyramid_jinja2``::

    config.include("pyramid_jinja2")

2.2 (2014-05-30)
================

- #88: Formalize template loading order and allow all lookups to fallback to
  the search path. A template is now always searched for relative to its
  parent template. If not found, the lookup will fallback to the search path.
  [mmerickel]

- Add ``prepend`` option to ``config.add_jinja2_search_path`` to allow
  prepending of paths to the beginning of the search path if a path should
  override previously defined paths. [mmerickel]

2.1 (2014-05-16)
================

- The 2.0 series started adding the package that invoked
  ``config.add_jinja2_renderer`` to the template search path. This is
  being removed in favor of explicit search paths and will hopefully not
  affect many people as it has only been available for a couple weeks. The
  only automatic search path left is the one added by the default ``.jinja2``
  renderer created when including ``pyramid_jinja2``. [mmerickel]

- Adjust the ``config.include("pyramid_jinja2")`` to add any packages from
  ``jinja2.directories`` **before** the default search path at the base of
  the app. Previously there was no way to override that search path.
  [mmerickel]

2.0.2 (2014-05-06)
==================

- The path of the child template is always considered when inheriting from
  a base template. Therefore when doing ``render("templates/foo.jinja2")``
  and ``foo.jinja2`` has an ``{% extends "base.jinja2" %}``, the template
  will be searched for as ``"templates/base.jinja2"`` on the search path.
  Previously the path of the child template was ignored when doing the
  lookup for the base, causing some very subtle and unrecoverable lookup
  errors when the child template was found relative to the caller instead
  of being found on the search path. [mmerickel]

- This release restores the default search path behaviors from the 1.x series
  that were inadvertently removed in the 2.x. The project's root package is
  added to the search path by default. [mmerickel]

2.0.1 (2014-04-23)
==================

- #86: Fix a regression caused by the new support for extending a template
  relative to itself. Using ``{% extends "some_asset:spec.jinja2" %}`` was
  no longer working and is now fixed. [mmerickel]


2.0 (2014-04-21)
================

- Claim Python 3.4 support
  [mmerickel]

- #75: Fix the missing piece of relative template loading by allowing a
  template to inherit from a template relative to itself, instead of
  forcing the parent to be on the search path.
  [mmerickel]

- #73: Added a new ``config.add_jinja2_renderer`` API that can create and
  override multiple Jinja2 renderers, each loaded using potentially different
  settings and extensions.

  The other APIs are now keyed on the renderer extension, as each extension
  may have different settings. Thus ``config.add_jinja2_search_path``,
  ``config.add_jinja2_extension``, and ``config.get_jinja2_environment``
  accept a ``name`` argument, which defaults to ``.jinja2``.

  This deprecates the old ``pyramid_jinja2.renderer_factory`` mechanism
  for adding renderers with alternate extensions.

  Configuration of the renderers has been updated to follow Pyramid's
  standard mechanisms for conflict detection. This means that if two modules
  both try to add a renderer for the ``.jinja2`` extension, they may raise a
  conflict or the modifications made by the invocation closest to the
  ``Configurator`` in the call-stack will win. This behavior can be affected
  by calling ``config.commit`` at appropriate times to force a configuration
  to take effect immediately. As such, configuration is deferred until
  commit-time, meaning that it is now possible
  ``config.get_jinja2_environment`` will return ``None`` because the changes
  have not yet been committed.
  [mmerickel]

Backward Incompatible Changes
-----------------------------

- The creation and configuration of the Jinja2 ``Environment`` is now deferred
  until commit-type in the Pyramid ``Configurator``. This means that
  ``config.get_jinja2_environment`` may return ``None``. To resolve this,
  invoke ``config.commit()`` before attempting to get the environment.

1.10 (2014-01-11)
=================

- #77: Change semantics of ``jinja2.bytecode_caching`` setting.  The new
  default is false (no bytecode caching) -- ``bytecode_caching`` must
  explicitly be set to true to enable a filesystem bytecode cache.
  In addition, an atexit callback to clean the cache is no longer
  registered (as this seemed to defeat most of the purpose of having
  a bytecode cache.)  Finally, a more complex bytecode cache may be
  configured by setting ``jinja2.bytecode_caching`` directly to a
  ``jinja2.BytecodeCache`` instance.  (This can not be done in a
  paste .ini file, it must be done programatically.)
  [dairiki]

- prevent error when using `python setup.py bdist_wheel`
  [msabramo]


1.9 (2013-11-08)
================

- fix indentation level for Jinja2ProjectTemplate in scaffolds/__init__.py
  [Bruno Binet]

- Remove unnecessary dependency on ``pyramid.interfaces.ITemplateRenderer``
  which was deprecated in Pyramid 1.5.
  [mmerickel]

- #68: Added `model_path_filter`, `route_path_filter` and `static_path_filter` filters
  [Remco]

- #74: Fixed issue with route being converted as_const by jinja2 engine when using btyecode cache
  [Remco]


1.8 (2013-10-03)
================

- #70: Do not pin for py3.2 compatibility unless running under py3.2
  [dairiki]


1.7 (2013-08-07)
================

- #56: python3.3: Non-ASCII characters in changelog breaks pip installation
  [Domen Kozar]

- #57: Remove useless warning: `DeprecationWarning: reload_templates setting
  is deprecated, use pyramid.reload_templates instead.`
  [Marc Abramowitz]


1.6 (2013-01-23)
================

- Set `jinja2.i18n.domain` default to the package name
  of the pyramid application.
  [Domen Kozar]

- Add `jinja2.globals` setting to add global objects into
  the template context
  [Eugene Fominykh]

- Add `jinja2.newstyle` setting to enable newstyle gettext calls
  [Thomas Schussler]

1.5 (2012-11-24)
================

- Add `pyramid.reload_templates` to set `jinja2.auto_reload` instead of
  using `reload_templates`. Deprecate the latter.
  [Domen Kozar]

- Clear bytecode cache on atexit
  [Domen Kozar]

- Add support for more Jinja2 options. Note support for jinja2.autoescape is
  limited to boolean only.

  * jinja2.block_start_string
  * jinja2.block_end_string
  * jinja2.variable_start_string
  * jinja2.variable_end_string
  * jinja2.comment_start_string
  * jinja2.comment_end_string
  * jinja2.line_statement_prefix
  * jinja2.line_comment_prefix
  * jinja2.trim_blocks
  * jinja2.newline_sequence
  * jinja2.optimized
  * jinja2.cache_size
  * jinja2.autoescape

  [Michael Ryabushkin]

1.4.2 (2012-10-17)
==================

- Add `jinja2.undefined` setting to change handling of undefined types.
  [Robert Buchholz]

- Remove redundant decoding error handling
  [Domen Kozar]

- Configure bytecode caching by default. Introduce `jinja2.bytecode_caching`
  and `jinja2.bytecode_caching_directory` settings.
  [Domen Kozar]

- Allow to add custom Jinja2 tests in `jinja2.tests` setting.
  [Sebastian Kalinowski]

1.4.1 (2012-09-12)
==================

- Fix brown-bag release
  [Domen Kozar]


1.4 (2012-09-12)
================

- Correctly resolve relative search paths passed to ``add_jinja2_search_path``
  and ``jinja2.directories``
  [Domen Kozar]

- #34: Don't recreate ``jinja2.Environment`` for ``add_jinja2_extension``
  [Domen Kozar]

- Drop Python 2.5 compatibility
  [Domen Kozar]

- Addition of ``static_url`` filter.

- Add ``dev`` and ``docs`` setup.py aliases (ala Pyramid).

- Changed template loading relative to package calling the renderer so
  it works like the Chameleon template loader.

1.3 (2011-12-14)
================

- Make scaffolding compatible with Pyramid 1.3a2+.

1.2 (2011-09-27)
================

- Make tests pass on Pyramid 1.2dev.

- Make compatible with Python 3.2 (requires Pyramid 1.3dev+).

1.1 (2011-07-24)
================

- Add ``get_jinja2_environment`` directive.

- Add all configurator directives to documentation.

1.0 (2011-05-12)
================

- Message domain can now be specified with *jinja2.i18n.domain* for i18n

- Paster template now sets up starter locale pot/po/mo files

- pyramid_jinja2 now depends on Jinja2 >= 2.5.0 due to
  ``jinja2.Environment.install_gettext_callables`` use
  https://github.com/Pylons/pyramid_jinja2/pull/21

- Added demo app just to visualize i18n work

0.6.2 (2011-04-06)
==================

- ``jinja2.ext.i18n`` is now added by default, see ``i18n.rst``
  for details

- Added ``add_jinja2_extension`` directive to the Configurator

- Updated jinja2.extensions parsing mechanism

- Fixed docs to indicate using asset: prefix is no longer necessary

0.6.1 (2011-03-03)
==================

- Asset-based loading now takes precedance and does not require
  "asset:" prefix

- Fixed the "current" package mechanism of asset: loading so that
  it more accurately finds the current package

- Dependency on ``pyramid_zcml`` removed.

0.6 (2011-02-15)
================

- Documentation overhauled.

- Templates can now be looked up by asset spec completely bypassing
  the search path by specifying a prefix of ``asset:``.

- Updated paster template to more closely relate to changes made
  to paster templmates in Pyramid core.

- Add new directive ``add_jinja2_search_path`` to the configurator
  when ``includeme`` is used.

0.5 (2011-01-18)
================

- Add ``includeme`` function (meant to be used via ``config.include``).

- Fix documentation bug related to ``paster create`` reported at
  https://github.com/Pylons/pyramid_jinja2/issues/12

- Depend upon Pyramid 1.0a10 + (to make ZCML work).

0.4 (2010-12-16)
================

Paster Template
---------------

- Changes to normalize with default templates shipping with Pyramid core:
  remove calls to ``config.begin()`` and ``config.end()`` from
  ``__init__.main``, entry point name changed to ``main``, entry
  ``__init__.py`` function name changed to ``main``, depend on WebError, use
  ``paster_plugins`` argument to setup function in setup.py, depend on
  Pyramid 1.0a6+ (use ``config`` rather than ``configurator``).

Tests
-----

- Use ``testing.setUp`` and ``testing.tearDown`` rather than constructing a
  Configurator (better fwd compat).

Features
--------

- Add ``model_url`` and ``route_url`` filter implementations (and
  documented).

Documentation
-------------

- Use Makefile which pulls in Pylons theme automagically.

0.3 (2010-11-26)
================

- Add ``jinja2.filters`` and ``jinja2.extensions`` settings (thanks to
  aodag).

- Document all known settings.

0.2 (2010-11-06)
================

- Template autoreloading did not function, even if ``reload_templates`` was
  set to ``True``.

0.1 (2010-11-05)
================

- First release.  *Not* backwards compatible with ``repoze.bfg.jinja2``: we
  use a filesystem loader (the directories to load from come from the
  ``jinja2.directories`` setting).  No attention is paid to the current
  package when resolving a renderer= line.
