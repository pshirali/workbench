Exit Codes
==========


WorkBench exits with different exit-codes when it encounters errors. The table
below lists the error names, exit-codes and a description.

+----------------+-----------+------------------------------------+
| Error Name     | ExitCode  | Description                        |
+================+===========+====================================+
| ERR_FATAL      | 1         | General/fatal errors.              |
+----------------+-----------+------------------------------------+
| ERR_MISSING    | 3         | Resource does not exist.           |
+----------------+-----------+------------------------------------+
| ERR_INVALID    | 4         | Failed input validation.           |
+----------------+-----------+------------------------------------+
| ERR_DECLINED   | 5         | Opted `No` on confirmation prompt  |
+----------------+-----------+------------------------------------+
| ERR_EXISTS     | 6         | Resource already exists.           |
+----------------+-----------+------------------------------------+
