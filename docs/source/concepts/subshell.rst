Introduction to subshells
=========================


.. note::
    Skip this section if you are already familiar with bash subshells


Consider a file ``abcd`` with the contents below:

.. code:: bash

    export ABCD=10
    show_abcd () {
        echo "The value of ABCD is ${ABCD}"
    }
    alias c=clear


A bash subshell could be invoked using:

.. code:: bash

    bash --rcfile ./abcd


While the prompt remains the same, a new interactive shell is now active.
In this state, the following behavior can be observed:

.. code:: bash

    >> echo $ABCD          # value from the environemnt variable is printed
    10

    >> show_abcd           # a bash function is invoked
    The value of ABCD is 10

    >> c                   # alias for `clear`. Clears the screen.

    >> exit                # exits the subshell


On `exit` all context from the subshell is lost. It may be observed
that executing the same commands in the parent shell does not result
in the same behavior as what was seen in the subshell.


An environment is a subshell initialised with environment variables,
functions or aliases which caters specifically to a project or a task
at hand.


By using environments:

1. The parent shell's namespace remains free of project-specific declarations
2. Declarations are local to each environment. Commands and variables by the
   same name could be declared in each environment, which perform operations
   unique to that environment.
3. It is easy to exit from the subshell and unload the entire environment
   at once.

