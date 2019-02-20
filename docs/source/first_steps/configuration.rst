Configuration
=============


WorkBench accepts its configuration from environment variables which
have the prefix ``WORKBENCH_``. WorkBench comes with sane defaults
and external configuration is optional.


Configuration using rcfile
~~~~~~~~~~~~~~~~~~~~~~~~~~

WorkBench can also source an `rcfile` on invocation. The default location
for the `rcfile` is ``$HOME/.workbenchrc``. If a file at the default
location exists, then it is automatically sourced.

A custom `rcfile` can be specified using the environment variable
``WORKBENCH_RC`` pointing to a file that already exists.

The `rcfile` can be used to define multiple configuration parameters
at once.

.. note::
    The rcfile overrides environment variables defined in the shell.

A full list of configurable parameters are available in subsequent chapters.


The WorkBench Home directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~


WorkBench operates on files inside a directory defined by ``WORKBENCH_HOME``.
If ``WORKBENCH_HOME`` is undefined, the default home directory
``$HOME/.workbench`` is used. WorkBench automatically creates the
necessary folder(s) on invocation.
