WorkBench Basics
================


Introduction
~~~~~~~~~~~~


WorkBench makes it easy to work with a large number of custom shell
environment scripts, each of which could be tailor-made for a project or task.

WorkBench sources shell code spread across different depths of a directory
tree to construct an environment automatically. Code could thus be implemented
in parts, residing in files at different directory depths, and without
any hardcoded references.

WorkBench operates only on files present inside a directory as defined by
``WORKBENCH_HOME``. It uses two abstract terms to refer to
parts of a to-be-assembled environment; namely ``Shelf`` and ``Bench``.


Shelves and Benches
~~~~~~~~~~~~~~~~~~~

**EXAMPLE**: Consider a ``WORKBENCH_HOME`` with the following structure:

.. code::

    WORKBENCH_HOME
        ├── ash.bench               # BENCH
        ├── bar/
        │   ├── baz/
        │   │   ├── maple.bench     # BENCH
        │   │   └── wb.shelf                        # SHELF
        │   └── birch.bench         # BENCH
        ├── foo/
        │   ├── pine.bench          # BENCH
        │   └── wb.shelf                            # SHELF
        └── wb.shelf                                # SHELF

Shelf
-----

A ``shelf`` is ``WORKBENCH_HOME``, or any subdirectory inside it,
which contains the file as defined by ``WORKBENCH_SHELF_FILE``. The default
value for ``WORKBENCH_SHELF_FILE`` is ``wb.shelf``. A ``shelf`` is always a 
path relative to ``WORKBENCH_HOME``. Shelf names end with a trailing ``/``
as they represent the directory containing ``WORKBENCH_SHELF_FILE`` and not
the file itself.

In the example above, the file ``wb.shelf`` is present at three locations.
Hence, there are three shelves here.

.. code::

    /
    foo/
    bar/baz/


The table below maps the name of the `shelf` to the underlying resource file:

    +---------------+-----------------------------------------------+
    | Shelf Name    | Underlying resource filename                  |
    +===============+===============================================+
    | /             | WORKBENCH_HOME/wb.shelf                       |
    +---------------+-----------------------------------------------+
    | foo/          | WORKBENCH_HOME/foo/wb.shelf                   |
    +---------------+-----------------------------------------------+
    | bar/baz/      | WORKBENCH_HOME/bar/baz/wb.shelf               |
    +---------------+-----------------------------------------------+

The sub-directory ``bar/`` is not a `shelf` because it doesn't
contain ``wb.shelf``.


Bench
-----

A ``bench`` is a file anywhere inside ``WORKBENCH_HOME`` with the
extension as defined by ``WORKBENCH_BENCH_EXTN``. The default value for
``WORKBENCH_BENCH_EXTN`` is ``bench``. The extension separator ``.`` is
assumed automatically and is not part of the value. Bench names are
representative of files. They do not include the trailing
``.<WORKBENCH_BENCH_EXTN>``

In the example above, there are four files with a ``.bench`` extension.
Hence, four benches.

.. code::

    ash
    bar/baz/maple
    bar/birch
    foo/pine


The table below maps the name of the `bench` to the underlying resource file:

    +---------------+-----------------------------------------------+
    | Bench Name    | Underlying resource filename                  |
    +===============+===============================================+
    | ash           | WORKBENCH_HOME/ash.bench                      |
    +---------------+-----------------------------------------------+
    | bar/baz/maple | WORKBENCH_HOME/bar/baz/maple.bench            |
    +---------------+-----------------------------------------------+
    | bar/birch     | WORKBENCH_HOME/bar/birch.bench                |
    +---------------+-----------------------------------------------+
    | foo/pine      | WORKBENCH_HOME/foo/pine.bench                 |
    +---------------+-----------------------------------------------+


Analogy
~~~~~~~

Analogous to a real workbench, the top of a `bench` is where the work
gets done. A discerning artisan might place minimal tools required for the
task at hand on the `bench`, while rest of the tools might be placed in
`shelves`, each of which ordered based on the frequency in which they get
used; frequently used tools being closer than infrequent ones.

The abstract `shelf` (a place to stow tools) may also be imagined as a
pegboard where tools are hung for easy access. An artisan can locate any
tool quickly, use it and put it back.

In WorkBench, the `shelf` hierarchy is provided by the possible presence
of the ``WORKBENCH_SHELF_FILE`` at different directory depths leading upto
the ``Bench``.

Code that is declared in a ``Shelf`` at the root; that is ``WORKBENCH_HOME``
will be sourced by every `workbench`. Code that is applicable only to a
specific set of environments could be defined in ``Shelves`` in a subdirectory
at the appropriate depth. Thus declarations & implementations common
to multiple environments get organised into ``Shelves``, while declarations
which uniquely associate with one environment get placed in a ``Bench``.

A pegboard approach could also be implemented by declaring functions in
various ``Shelves`` but not calling them. The ``Bench`` would call those
functions with various parameters for the task at hand.


Benefits
~~~~~~~~


1. Overall there is less code to maintain.
2. It is easy influence control on a whole class of environments by moving
   code to a ``Shelf`` at the appropriate subdirectory
3. Redeclaration results in overriding. Code in `shelf` at a deeper depths 
   overrides those at lower depths (closer to ``WORKBENCH_HOME``). Code in
   a `bench` overrides all `shelves`. The workbench `tree` could be designed
   to be shallow, or deeply nested to cater to the amount of overriding
   required.
4. The hierarchical structure lends itself to organising and managing a tree
   of hundreds of `benches` easily.
