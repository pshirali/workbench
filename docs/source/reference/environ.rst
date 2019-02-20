Environment Variables
=====================


The table below contains a list of environment variables which WorkBench
consumes in its configuration.


+---------------------------+------------------------+--------------------------------------------------------+
| Environment Variable Name | Default Value          | Description                                            |
+===========================+========================+========================================================+
| WORKBENCH_RC              | $HOME/.workbenchrc     | Auto-load location for the rcfile                      |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_HOME            | $HOME/.workbench       | Directory containg shelves and benches                 |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_GREPPER         | egrep                  | Grep tool used to list env. vars                       |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_AUTOCONFIRM     | <not-set>              | Skip confirmation prompt for `rm` if set               |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_SHELF_FILE      | wb.shelf               | Filename for the shelf file                            |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_BENCH_EXTN      | bench                  | File extension for the bench file                      |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_ACTIVATE_CMD    | /bin/bash --rcfile     | Command to invoke subshell in intereactive mode        |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_COMMAND_CMD     | /bin/bash -ic          | Command to invoke a script in non-interactive mode     |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_ACTIVATE_FUNC   | workbench_OnActivate   | Entrypoint function name for the on `activate` command |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_DEACTIVATE_FUNC | workbench_OnDeactivate | Exit-hook called when exiting a subshell               |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_COMMAND_FUNC    | workbench_OnCommand    | Entrypoint function name for the `command` command     |
+---------------------------+------------------------+--------------------------------------------------------+
| WORKBENCH_NEW_FUNC        | workbench_OnNew        | Entrypoint function name for the `new` command         |
+---------------------------+------------------------+--------------------------------------------------------+


The table below contains a list of environment variables which are injected as part of the
auto-generated `workbench`.


+---------------------------+---------------------------------------------------------+
| Environment Variable Name | Description                                             |
+===========================+=========================================================+
| WORKBENCH_ENV_NAME        | Name of the currently active `bench`                    |
+---------------------------+---------------------------------------------------------+
| WORKBENCH_CHAIN           | A ``:`` separated list of every sourced shelf and bench |
+---------------------------+---------------------------------------------------------+
| ORIG_PS1                  | Stores the existing ``PS1`` before redefining it        |
+---------------------------+---------------------------------------------------------+
