.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   Jinja2
      A `templating system written by Armin Ronacher
      <http://jinja.pocoo.org/>`_.

   Pyramid
      A `web framework
      <https://docs.pylonsproject.org/projects/pyramid/en/latest/>`_.

   Configurator
      :py:class:`pyramid.config.Configurator`

   pyramid_jinja2
      A set of bindings that make templates written for the :term:`Jinja2`
      templating system work under the :term:`Pyramid` web framework.

   Template Inheritance
      Allows you to build a base “skeleton” template that contains all the
      common elements of your site and defines blocks that child templates
      can override. See :ref:`Template Inheritance 
      <jinja2:template-inheritance>` in the Jinja2 documentation.

   Asset Specification
       A string representing the path to a directory or file present in a
       Python module. See :ref:`Understanding Asset Specifications 
       <pyramid:asset_specifications>` in the Pyramid documentation for 
       more information.
