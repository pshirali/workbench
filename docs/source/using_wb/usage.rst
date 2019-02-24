Usage Guide
===========


WorkBench has a minimal set of commands. They are also short (usually one
character).

.. note::
    The following convention denotes ``OR``.
    Example: ``wb a|b|c`` means ``wb a`` OR ``wb b`` OR ``wb c``


View version and env -- [``wb -V``, ``wb -E``]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``wb -V`` prints the version of WorkBench being used.

``wb -E`` lists all environment variables starting with ``WORKBENCH_``.
These environment variables may be defined in your current shell, or
may be defined in a ``WORKBENCH_RC`` file.

If you use an `rcfile` with WorkBench, the values you set in the `rcfile`
will apply over everything else. The `rcfile` is sourced on every ``wb``
invocation regardless of the command.


Operating on Shelves and Benches -- [``wb s``, ``wb b``]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following operations can be performed on `shelves` and `benches`:.

List
----

WorkBenches can be listed using ``wb s|b``


Print path to the underlying file
---------------------------------

``wb s|b <name>``, where `<name>` is either a `<shelfName>` or `<benchName>`
prints the absolute path to the underlying resource file associated with
that shelf or bench.

The path is generated and displayed for non-existent shelves and benches as
well. A non-zero exit-code is returned if a shelf or bench doesn't exist.


Run a command against the underlying file
-----------------------------------------

``wb s|b [options] <name> <command> [[arg]..]``

Runs ``<command> [[arg]..] <path-to-underlying-file-for-name>``

Examples:

.. code::

    wb s <shelfName> cat      # view the file WORKBENCH_HOME/.../<shelf-file>
    wb b <benchName> vim      # edit the file WORKBENCH_HOME/.../<bench-file> in ViM


Commands execute only when a <shelfName> or <benchName> exist on disk.
It is possible to create a new `shelf` or `bench` inline, just before
running a command on it by adding the ``--new`` switch.

.. code::

    wb s --new <newShelfName> vim

WorkBench prompts for confirmation if the `<command>` is ``rm``. The
``--yes`` switch can be used to indicate `Yes` to skip the prompt. Alternatively,
``WORKBENCH_AUTOCONFIRM`` can be set to any non-empty value to disable
this prompt and assume `Yes` always.


Auto-generated `workbench` and Entrypoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


A `workbench` is the auto-generated code composed by WorkBench (the tool),
when the command ``wb a|c|n <benchName>`` is executed.

The switch ``--dump`` can be used to print the auto-generated code on `stdout`
instead of executing it. The ``--dump`` switch does not validate the presence
of a `<benchName>`. This switch can be used to review the generated code.

The auto-generated `workbench` has the following high-level sections:

.. code::

    ┌───────────────┐
    │      INIT     │   <---- Initial declarations are done here
    ├───────────────┤
    │     SOURCE    │   <---- Shelves and bench are `sourced` here
    ├───────────────┤
    │   ENTRYPOINT  │   <---- Entrypoint function is called with `args`
    └───────────────┘

The `INIT` section of the `workbench` contains basic/no-op implementations
for the default functions. `Shelves` and `Bench` are expected to define their
own functions with an actual implementation to override those in `INIT`.

The `INIT` section defines the following variables:

1. ``WORKBENCH_ENV_NAME``: Stores the `benchName` as the environment name
2. ``ORIG_PS1``: Stores the current ``PS1``, while ``PS1`` is reset to
   prefix the current `benchName`
3. ``WORKBENCH_CHAIN``: Stores a ``:`` separated list of each sourced `shelf`
   and `bench` in the order in which they were sourced.

An entrypoint is a shell functions invoked after sourcing all the `shelves`
and the `bench`. Each WorkBench execution command has a different
`entrypoint` function associated with it. Any trailing arguments passed
to the WorkBench's execution command are passed on to the `entrypoint`.

Entrypoint function names are configurable. The table below lists the
environment variables which define the `entrypoints` and the default
function names associated with each of them.

+------------+---------------------------+------------------------+---------+
| Type       | Environment Variable Name | Default Function Name  | Command |
+============+===========================+========================+=========+
| entrypoint | WORKBENCH_ACTIVATE_FUNC   | workbench_OnActivate   | a       |
+------------+---------------------------+------------------------+---------+
| entrypoint | WORKBENCH_COMMAND_FUNC    | workbench_OnCommand    | c       |
+------------+---------------------------+------------------------+---------+
| entrypoint | WORKBENCH_NEW_FUNC        | workbench_OnNew        | n       |
+------------+---------------------------+------------------------+---------+

The `entrypoint` is invoked by calling the entrypoint environment variable.
Thus the value of the entrypoint environment variable can be redefined in
the `shelf` or the `bench` to point to a non-default function as well.

Entrypoint Example
------------------

When ``wb c <benchName> arg1 arg2`` is executed, then the function that
maps to ``WORKBENCH_COMMAND_FUNC`` becomes the actual entrypoint.
The default entrypoint function name is ``workbench_OnCommand`` and the
`INIT` section has an implemetation for it.

A `shelf` or `bench` could redeclare ``workbench_OnCommand`` multiple times;
in files at different depths. The last declared implementation will be the one
that executes with arguments ``arg`` ``arg2``

It is also possible that ``WORKBENCH_COMMAND_FUNC`` could be assigned a new
value like ``my_custom_func`` anywhere in the `shelves` or the `bench`.
The last declared value of ``WORKBENCH_COMMAND_FUNC`` is now the new
entrypoint function, and the last declared implementation of the
function ``my_custom_func`` is the one that executes with
arguments ``arg1`` ``arg2``


Executing `workbench` environments -- [``wb a``, ``wb c``, ``wb n``]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Activate -- [``wb a``]
----------------------

The `activate` command is equivalent of ``bash --rcfile <workbench>``. It
spawns a subshell with the auto-generated `workbench`, with
``WORKBENCH_ACTIVATE_FUNC`` as the entrypoint.

Nested `activations` are prevented by checking if ``WORKBENCH_ENV_NAME`` has
already been set.

Deactivating a `workbench` is done by simply running `exit`.

Occasionally, there may be cases where some code needs to be executed when
an `exit` is issued. This can be achieved by redeclaring the `exit` function,
calling user-defined code, followed by calling `builtin exit`.

**Example:**

.. code::

    exit () {
        <your-deactivation-code-goes-here>
        builtin exit $? 2> /dev/null
    }


Command -- [``wb c``]
---------------------

The `command` command is the equivalent of ``bash -c <workbench>``. It
executes the `workbench` non-interactively, with ``WORKBENCH_COMMAND_FUNC``
as the entrypoint.

The `command` command is used to invoke one-off commands which may be defined
in the `workbench`, but don't necessarily require an interactive subshell.

For example, a `workbench` could declare subcommands like ``start``, ``stop``,
``build``, ``deploy`` etc, as independent functions. The entrypoint function
defined by ``WORKBENCH_COMMAND_FUNC`` could parse arguments and dispatch them
to respective subcommands.

Thus, for the same `workbench`, the `Activate` and `Command` commands could be
used to trigger different functionality.


New -- [``wb n``]
-----------------

The `new` command is a variant of the `command` command. It's execution is
similar to that of the `command` command (non-interactive), but with
``WORKBENCH_NEW_FUNC`` as the entrypoint.

The `new` command makes it easy to create new environments. When the command
``wb n <newBenchName>`` is invoked, WorkBench creates all intermediate
`shelf` files (if they don't already exist) followed by the `bench`.

The last declared function as defined by ``WORKBENCH_NEW_FUNC`` is then
called, which could interactively setup contents for the new `bench`.

A good example for this would be virtual-environments for programming
languages. For a given programming language, it is possible that the
procedure to setup a `bench` for a new project/repo would involve a
common set of steps; where only a few pieces of information (like
`projectName`, `path`, `URL` etc) might be required from the user.

The `shelf` for a language could implement a ``WORKBENCH_NEW_FUNC`` which
requests this information for a new project, and auto-generates a `bench`
with all necessary info.
