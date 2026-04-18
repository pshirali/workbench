Release History
===============

This page tracks released versions of WorkBench along with the notable changes
in each release. Dates follow the ``YYYY-MM-DD`` format.


0.1.1 (unreleased)
~~~~~~~~~~~~~~~~~~

Bug fixes
---------

- Fixes Issue-15_: The default auto-generated ``workbench_OnNew`` was
  creating the bench file at a path relative to the current working directory
  instead of inside ``WORKBENCH_HOME``. ``_wb_compose_code`` was passing
  ``resourceName`` as both arguments to ``_wb_compose_initcode``; the second
  argument must be the absolute ``resourceFile`` path, which is what the
  generated ``workbench_OnNew`` uses to build ``mkdir -p`` and ``touch``.
  ``wb n <benchName>`` now correctly creates
  ``$WORKBENCH_HOME/<benchName>.bench`` when no overriding ``workbench_OnNew``
  is defined in a shelf or rcfile.
- Fixes Issue-11_: When ``WORKBENCH_HOME`` sits underneath the current
  directory, the root shelf is no longer sourced twice during the hierarchical
  sourcing of shelves.

.. _Issue-11: https://github.com/pshirali/workbench/issues/11
.. _Issue-15: https://github.com/pshirali/workbench/issues/15

Enhancements
------------

- Resolves Issue-13_: The logic for creating a new bench has been moved into
  the default ``workbench_OnNew`` function. This allows the behaviour of
  ``wb n`` to be overridden from a shelf or rcfile, so users can attach their
  own bench-creation workflow (e.g., templated starter files) without having
  to bypass ``wb``.

.. _Issue-13: https://github.com/pshirali/workbench/issues/13

Tests
-----

- Added a regression test for Issue-15_ that asserts ``wb n`` with the default
  ``workbench_OnNew`` creates the bench file under ``WORKBENCH_HOME`` and does
  not leak a relative path into the current working directory.


0.1.0 (2019-02-28)
~~~~~~~~~~~~~~~~~~

Initial public release of WorkBench. Highlights:

- Hierarchical environment manager for \*nix shells. A workbench is composed
  by layering shell code from shelves found at each directory level within
  ``WORKBENCH_HOME``, followed by a bench file that overrides all shelves.
- Three execution modes exposed through the CLI:

  - ``wb a`` — activate a workbench in a new interactive subshell via
    ``WORKBENCH_ACTIVATE_FUNC`` (default: ``workbench_OnActivate``).
  - ``wb r`` — run a command from a workbench in the current shell via
    ``WORKBENCH_RUN_FUNC`` (default: ``workbench_OnRun``).
  - ``wb n`` — create a new bench via ``WORKBENCH_NEW_FUNC``
    (default: ``workbench_OnNew``).

- Shelf and bench file operations through ``wb s`` and ``wb b`` (list, show
  path, run a command on the underlying file, with ``-n``/``--new`` and
  ``-y``/``--yes`` switches).
- ``WORKBENCH_RC`` support, with ``$HOME/.workbenchrc`` auto-sourced when
  present.
- ``workbench_pre_execute_hook`` for user-defined checks run before every
  workbench execution (resolves Issue-7_).
- Security: paths are validated with ``realpath`` to prevent directory
  traversal outside of ``WORKBENCH_HOME`` (resolves Issue-3_).
  ``WORKBENCH_ALLOW_INSECURE_PATH`` disables this check for environments
  without GNU Coreutils.
- ``WORKBENCH_CHAIN`` is exported to each workbench and lists the chain of
  sourced files (shelves followed by the bench).
- ``WORKBENCH_EXEC_MODE`` is exported and carries the invoking command
  (``a`` | ``r`` | ``n``).
- ``WORKBENCH_SHELF_FILE`` and ``WORKBENCH_BENCH_EXTN`` are injected into
  each workbench.
- Removed deactivation as a built-in feature (resolves Issue-5_). Exit hooks
  can be installed by overriding ``exit`` inside the bench if required.
- Bash completion script included under ``completion/``.
- Demo scripts under ``demo/`` (Go workspaces example) and an asciinema
  intro.

.. _Issue-3: https://github.com/pshirali/workbench/issues/3
.. _Issue-5: https://github.com/pshirali/workbench/issues/5
.. _Issue-7: https://github.com/pshirali/workbench/issues/7
.. _Issue-9: https://github.com/pshirali/workbench/issues/9
