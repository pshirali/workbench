Welcome to WorkBench's documentation
====================================

|

.. image:: _static/logo-black.png
    :scale: 40%
    :align: center
    :alt: WorkBench Logo

|


WorkBench is a hierarchical environment manager for \*nix shells. It sources
shell-code distributed across multiple levels of a folder hierarchy and
invokes environments with the combination. Code could thus be implemented
to operate at different scopes, allowing clear overrides at each folder depth
and easy overall maintenance while managing several hundred environments.


WorkBench is a minimalistic framework. It is extendable and configurable,
and can adapt to a variety of use-cases. It is implemented as a single
bash script, and designed to work with minimal dependencies even on 
vanilla \*nix systems.


.. toctree::
   :maxdepth: 2
   :caption: Getting Started:

   first_steps/installation
   first_steps/configuration
   first_steps/completion


.. toctree::
   :maxdepth: 2
   :caption: Using WorkBench:

   using_wb/subshell
   using_wb/concepts
   using_wb/usage
   using_wb/environ
   using_wb/exitcodes
   using_wb/security


.. toctree::
   :maxdepth: 2
   :caption: Developer Notes:

   devnotes/contrib.rst
   devnotes/testing.rst
   devnotes/license.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
