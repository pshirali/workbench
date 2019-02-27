Security
========


WorkBench is a bash script capable of executing shell code from your system.
This page discloses some of the inner-workings of WorkBench for user
awareness. It also covers guidelines and best-practices that you should
follow to securely use WorkBench.

It is vital that you understand the contents of this page before you use
WorkBench. A discerning user might find the contents here a tad verbose.
However, it is in the best interest of a potential user.

This document assumes that you are already operate a secure system where the
statements below (but not limited to) are true:

1. You trust the OS binaries that are installed.
2. Only you have access to the contents of your `user` directory. (`$HOME`)
3. You own and understand the contents of your shell's rcfiles. (like `.bashrc`).

The rest of the this page discusses how WorkBench fits in, and the baggage
that it brings with it.


Single User Context
~~~~~~~~~~~~~~~~~~~


WorkBench is designed for a single-user. You should use WorkBench on systems
where you (as a \*nix user), and ONLY YOU own and are in are in
complete control of:

1. WorkBench (the tool), and the location where it is deployed.
2. The location(s) and contents of all `WORKBENCH_RC` files
3. The location(s) and contents of all `WORKBENCH_HOME` folders (the entire tree)

Every time you run `wb`, you are not only executing the code in `wb`, but
also the contents of the `rcfile`. The default location ``$HOME/.workbenchrc``
is tried if `WORKBENCH_RC` is not defined. The `rcfile` here is a shell
script. The code within it will execute even without the `execute` permission
set on the file (similar to your `.bashrc`, `.bash_profile`)

Depending on values defined against `WORKBENCH_SHELF_FILE` and
`WORKBENCH_BENCH_EXTN`, all files matching the filename and extension
respectively within your `WORKBENCH_HOME` are assumed to be shell scripts.
Code from these files will be sourced when you invoke `wb a`, `wb r` or `wb n`
commands. As above, they too don't require the `execute` permission to be
set on them.

WorkBench is not in control of any files or commands that may be sourced or
executed within `shelves` or `benches`. It is possible that code
(content within the `shelf` or `bench`) might source files outside of 
`WORKBENCH_HOME`, or outside of your `user` directory too.

The name of the `entrypoint` function that WorkBench executes can be
redefined using `WORKBENCH_ACTIVATE_FUNC`, `WORKBENCH_RUN_FUNC` and
`WORKBENCH_NEW_FUNC` respectively. Depending on the command invoked, the
control will land on one of these functions.

The values for these variables can be replaced by any executable binary or
an existing definition in your current shell (parent shell).

**Example:**

.. code::

    WORKBENCH_RUN_FUNC=echo wb r <benchName> Hello World

    Will print "Hello World" in the last line of the command's output.


Guidelines
----------

1. Ensure/change the ownership of ``wb``, `rcfiles` and all contents of
   `WORKBENCH_HOME` to you (as a user). Ensure that `write` and `execute`
   permissions are not available for `group` and `all`.

   **Ideal permissions:**

    .. code-block:: none

        chmod 0700 <wb>
        chmod 0600 <rcfiles>
        chomd 0600 <WORKBENCH_HOME and all its files>

2. Do not introduce new content into `WORKBENCH_HOME` that you haven't
   personally written or reviewed.
   
   **For example:**
   
   (a) Do not extract archives inside `WORKBENCH_HOME`.
   (b) Do not ``git clone`` repositories into your `WORKBENCH_HOME`.

   You must treat the contents of `WORKBENCH_HOME` in the same light as
   your `rcfiles`, `dotfiles` etc.


Detecting changes in your WORKBENCH_HOME
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WorkBench provides a function ``workbench_pre_execute_hook`` which allows
you to implement your own `pre` checks before executing a `workbench`. This
is an ideal place to implement checks to track change to `WORKBENCH_HOME`.

You can implement ``workbench_pre_execute_hook`` as a function inside your
`WORKBENCH_RC`. If the function returns with a non-zero return code,
WorkBench will exit with that code.

Perhaps the easiest way to achieve this would be to turn your `WORKBENCH_HOME`
into a Git repo and let Git track your changes. (Example: ``git status -s``)


Canonical paths and directory traversal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


WorkBench uses the ``realpath`` (GNU) utility to convert all relative paths to
absolute paths before operating on them. WorkBench ensures that every `shelf`
and `bench` that gets sourced as part of building a `workbench`, also reside
within ``WORKBENCH_HOME``.

.. important::

    1. ``WORKBENCH_RC`` and ``WORKBENCH_HOME`` are excluded from checks.
       It is highly recommended that they reside inside your ``HOME``
       directory, but this is not enforced.
    2. WorkBench does not detect `source` statements inside the code residing
       in a `shelf` or `bench`. Placing such `source` statements is discouraged.
       If you do, then you should ensure that you `source` it from locations
       within ``WORKBENCH_HOME``.

It is possible that ``realpath`` might not be present on every OS, and you
might have to install it before using WorkBench.

WorkBench also provides a way to disable this feature. You can do so by
setting ``WORKBENCH_ALLOW_INSECURE_PATH`` to any value to disable directory
traversal checks.


What is a directory traversal attack? How is it harmful?
--------------------------------------------------------


Directory traversal attack is a way by which software is made to expose
or operate on files outside a directory boundary. It takes the form of an
`attack` when it is used with malicious intent. WorkBench implements checks
largely to prevent inadvertent sourcing of content.

A directory traversal attack involves a `path` derived from user input which
includes ``../``. This indicates the parent of the intended directory.
With directory traversal checks disabled, one could supply a command like:
``wb r ../benchName`` to access a `shelf` and a `bench` that is located at
the parent directory of ``WORKBENCH_HOME``. The input could include multiple
``../`` to craft a `path` that points to any other file on your drive.

.. note::

    WorkBench strips preceeding ``/`` from `shelf` and `bench` names,
    and makes them relative to `WORKBENCH_HOME`. This handles the
    case of input `shelf` or `bench` names supplied as absolute paths.


Temp files
~~~~~~~~~~


WorkBench creates temp files with the auto-generated `workbench` contents
when the commands ``wb a``, ``wb r``, ``wb n`` are executed without the
``--dump`` switch. The temp files are created using ``mktemp`` utility.
This creates a file within ``/tmp`` with the content that you see in the
``--dump`` switch. The temp files have a default permission `0600` which
makes them accessible to only you, the user. WorkBench deletes the temp
file after the command completes execution.
