#!/usr/bin/env python3

import subprocess
import unittest
import shutil

from os import makedirs
from os.path import abspath, dirname, join, basename, exists, isdir

WB_DIR=abspath(join(dirname(__file__), ".."))
TESTDATA=join(WB_DIR, "tests", "testdata")
WB=join(WB_DIR, "wb")

ERR_FATAL=1
ERR_MISSING=3
ERR_INVALID=4
ERR_DECLINED=5
ERR_EXISTS=6

EXECUTOR="bash"
EXECUTOR_VERSION_FLAG=" --version"


def run(cmd, **kwargs):
    if not isinstance(cmd, str):
        raise ValueError("Expected command to be a string")
    replace = kwargs.pop("replace", {})
    wb_data = dict(td=TESTDATA, wb="{} {}".format(EXECUTOR, WB))
    wb_data.update(replace)
    cmd = cmd.format(**wb_data)
    run_args = dict(
        shell=True, cwd=WB_DIR, timeout=5,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    run_args.update(kwargs)
    cp = subprocess.run(cmd, **run_args)
    if not isinstance(cp.stdout, str):
        cp.stdout = cp.stdout.decode('utf-8')
    if not isinstance(cp.stderr, str):
        cp.stderr = cp.stderr.decode('utf-8')
    return cp


def get_shelf_filename(home, shelf_name):
    # https://docs.python.org/3.7/library/os.path.html#os.path.join
    # If a component is an absolute path, all previous components are thrown
    # away and joining continues from the absolute path component.
    if shelf_name == "/":
        shelf_name = ""
    return join(home, shelf_name, "wb.shelf")


def get_bench_filename(home, bench_name):
    return join(home, "{}{}".format(bench_name, ".bench"))


GET_FILENAME = {
    "s": get_shelf_filename,
    "b": get_bench_filename,
}


def show_meta():
    print("----- [ meta ] -----")
    print(run("{}{}".format(EXECUTOR, EXECUTOR_VERSION_FLAG)).stdout)
    print("-----")


show_meta()


# -----------------------------------------------------------------------------
#
#   Tests start here
#
# -----------------------------------------------------------------------------


class TestWbRCFile(unittest.TestCase):

    def test_consume_from_workbenchrc_default(self):
        """
        If WORKBENCH_RC is not defined, and a file $HOME/.workbenchrc
        exists, then source it automatically
        """
        o = run("HOME={td}/rctest {wb} -E")
        self.assertIn("WORKBENCH_TEST=___default___", o.stdout.split('\n'))
        self.assertEqual(o.returncode, 0)

    def test_consume_from_user_supplied_rc(self):
        """
        If a WORKBENCH_RC is defined, then source only supplied file.
        """
        o = run("WORKBENCH_RC={td}/rctest/custom.rc {wb} -E")
        self.assertIn("WORKBENCH_TEST=___custom___", o.stdout.split('\n'))
        self.assertEqual(o.returncode, 0)

    def test_workbench_on_home_folder_with_no_workbenchrc(self):
        """
        WorkBench must not error if $HOME does not have a .workbenchrc
        """
        o = run("HOME={td}/rctest/emptyfolder {wb} -E")
        self.assertNotIn("WORKBENCH_TEST=", o.stdout.split('\n'))
        self.assertEqual(o.returncode, 0)

    def test_non_existent_workbench_rc_file_raises_error(self):
        """
        WorkBench must error if WORKBENCH_RC points to a file that
        doesn't exist.
        """
        filename = "this-file-does-not-exist.rc"
        o = run("WORKBENCH_RC={filename} {wb} -E",
                replace=dict(filename=filename))
        self.assertEqual(o.stdout, "")
        # errmsg = "ERROR: Can't find WORKBENCH_RC: '{}'".format(filename)
        # self.assertEqual(o.stderr.strip(), errmsg)
        self.assertEqual(o.returncode, ERR_MISSING)

    def test_list_workbench_env_vars(self):
        """
        wb -E must only list env var entries ^WORKBENCH_*
        """
        o = run("HOME={td}/rctest/emptyfolder {wb} -E")
        for entry in o.stdout.strip().split('\n'):
            self.assertTrue(entry.startswith("WORKBENCH_"))
        self.assertEqual(o.returncode, 0)


class TestWbShelfAndBenchOps(unittest.TestCase):

    # LIST SHELVES AND BENCHES

    def test_list_simple_benches(self):
        """
        'wb b' lists all benches in WORKBENCH_HOME
        """
        o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} b")
        benches = set(o.stdout.strip().split('\n'))
        self.assertEqual(benches, set([
            "outer/inner/simple1",
            "outer/inner/simple2"
        ]))
        self.assertEqual(o.returncode, 0)

    def test_list_simple_shelves(self):
        """
        'wb s' lists all shelves in WORKBENCH_HOME
        """
        o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} s")
        shelves = set(o.stdout.strip().split('\n'))
        self.assertEqual(shelves, set([
            "/",
            "outer/",
            "outer/inner/"
        ]))
        self.assertEqual(o.returncode, 0)

    # SHOW PATH TO SHELF AND BENCH FILES

    def _test_print_path_to_file(self, wb_cmd, name, missing=False):
        """
        wb s shelfName
        wb b benchName
        Prints absolute path to the underlying shelf/bench file
        """
        root_folder = join(TESTDATA, "wbhome", "simple")
        filename = GET_FILENAME[wb_cmd](root_folder, name)

        o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} {wb_cmd} {name}",
                replace=dict(wb_cmd=wb_cmd, name=name))
        if missing is False:
            self.assertEqual(o.stdout.strip(), filename)
            self.assertEqual(o.stderr.strip(), "")
            self.assertEqual(o.returncode, 0)
        else:
            self.assertEqual(o.stdout.strip(), "")
            self.assertEqual(o.stderr.strip(), filename)
            self.assertEqual(o.returncode, ERR_MISSING)

    def test_show_simple_bench_file(self):
        self._test_print_path_to_file("b", "outer/inner/simple1")
        self._test_print_path_to_file("b", "outer/inner/simple2")
        self._test_print_path_to_file("b", "valid/but/missing/bench",
                                      missing=True)

    def test_show_simple_shelf_path(self):
        self._test_print_path_to_file("s", "/")
        self._test_print_path_to_file("s", "outer/")
        self._test_print_path_to_file("s", "outer/inner/")
        self._test_print_path_to_file("s", "valid/but/missing/shelf/",
                                      missing=True)

    # RUN COMMAND ON A SHELF AND BENCH FILE

    def _test_command_on_file(self, wb_cmd, name):
        root_folder = join(TESTDATA, "wbhome", "simple")
        filename = GET_FILENAME[wb_cmd](root_folder, name)

        cmd = "head -n 1"
        with open(filename) as f:
            lines = f.read().split('\n')
        self.assertTrue(len(lines) > 0)
        self.assertTrue(lines[0] != "")
        expected = lines[0]

        o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} {wb_cmd} {name} {cmd}",
                replace=dict(wb_cmd=wb_cmd, name=name, cmd=cmd))
        self.assertEqual(expected, o.stdout.strip())
        self.assertEqual(o.returncode, 0)

    def test_run_command_on_bench_file(self):
        self._test_command_on_file("b", "outer/inner/simple1")

    def test_run_command_on_shelf_file(self):
        self._test_command_on_file("s", "outer/inner/")

    def test_list_errors_on_bad_inputs(self):
        bad_inputs = [
            ("s", "invalid-shelf-missing-tailing-slash", ERR_INVALID),
            ("b", "invalid-bench-having-tailing-slash/", ERR_INVALID),
        ]
        for (wb_cmd, name, errCode) in bad_inputs:
            o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} {wb_cmd} {name}",
                    replace=dict(wb_cmd=wb_cmd, name=name))
            self.assertEqual(o.returncode, errCode)

    # CONFIRMATION

    def _cleanup_before_test(self, rm_test_dir):
        if exists(rm_test_dir) and isdir(rm_test_dir):
            shutil.rmtree(rm_test_dir)

    def _cleanup_after_test(self, rm_test_dir):
        shutil.rmtree(rm_test_dir)

    def _create_new_through_testcode(self, filename):
        """
        wb s|b has a switch -n|--new which creates new shelf/bench if
        one doesn't exist. When -n is not passed, we need our testcode
        to create these dirs & files for tests to be performed on them
        """
        makedirs(dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write("some-dummy-data")

    def _rm_kwargs(self, prefix, wb_cmd, name, stdin=""):
        kw = dict(
            replace=dict(prefix=prefix, wb_cmd=wb_cmd, name=name)
        )
        if stdin:
            kw["encoding"] = "ascii"
            kw["input"] = "{}\n".format(stdin)
        return kw

    def _test_rm_confirmation(self, prefix, wb_cmd, name, new_flag=False):
        """
        Test wb s|b <name> rm
        When the command is 'rm', an interactive prompt is presented.
        Removal occurs only when confirmed.
        """
        rm_test_dir = join(TESTDATA, "wbhome/rm_test")
        try:
            self._cleanup_before_test(rm_test_dir)
            filename = GET_FILENAME[wb_cmd[0]](rm_test_dir, name)

            if new_flag is False:
                self._create_new_through_testcode(filename)

            # --- Test with "n" (No) on prompt ----------------------------
            # Expect ERR_DECLINED. Expect file to remain
            kw = self._rm_kwargs(prefix, wb_cmd, name, stdin="n")

            o = run("WORKBENCH_HOME={td}/wbhome/rm_test "
                    "{prefix} {wb} {wb_cmd} {name} rm",
                    **kw)
            self.assertEqual(o.returncode, ERR_DECLINED)
            self.assertTrue(exists(filename))

            # --- Test with "y" (Yes) on prompt ---------------------------
            # Expect succcess. Expect file to get deleted
            kw = self._rm_kwargs(prefix, wb_cmd, name, stdin="y")
            o = run("WORKBENCH_HOME={td}/wbhome/rm_test "
                    "{prefix} {wb} {wb_cmd} {name} rm",
                    **kw)

            self.assertEqual(o.returncode, 0)
            self.assertTrue(not exists(filename))

        finally:
            self._cleanup_after_test(rm_test_dir)

    def _test_rm_auto_confirmation(self, prefix, wb_cmd, name, new_flag=False):
        """
        wb s|b -y <name> rm
        OR
        WORKBENCH_AUTOCONFIRM=1 wb s|b <name> rm

        Will assume Yes always and will not provide an interactive prompt
        """
        rm_test_dir = join(TESTDATA, "wbhome/rm_test")
        try:
            self._cleanup_before_test(rm_test_dir)
            filename = GET_FILENAME[wb_cmd[0]](rm_test_dir, name)

            if new_flag is False:
                self._create_new_through_testcode(filename)

            kw = self._rm_kwargs(prefix, wb_cmd, name)
            o = run("WORKBENCH_HOME={td}/wbhome/rm_test "
                    "{prefix} {wb} {wb_cmd} {name} rm",
                    **kw)

            self.assertEqual(o.returncode, 0)
            self.assertTrue(not exists(filename))

        finally:
            self._cleanup_after_test(rm_test_dir)

    def test_confirmation_prompt_on_rm(self):
        inputs = [
            ("WORKBENCH_AUTOCONFIRM=", "s", "remove_me/"),
            ("WORKBENCH_AUTOCONFIRM=", "b", "remove_me/bench"),
            # Get WorkBench to create new resources if they don't exist
            ("WORKBENCH_AUTOCONFIRM=", "s -n", "remove_me/"),
            ("WORKBENCH_AUTOCONFIRM=", "b -n", "remove_me/bench"),
        ]
        for (prefix, wb_cmd, name) in inputs:
            new_flag = True if "-n" in wb_cmd else False
            self._test_rm_confirmation(prefix, wb_cmd, name, new_flag=new_flag)

    def test_autoconfirmation_on_rm(self):
        inputs = [
            ("WORKBENCH_AUTOCONFIRM=", "s -y", "remove_me/"),
            ("WORKBENCH_AUTOCONFIRM=", "b -y", "remove_me/bench"),

            # set confirmation via WORKBENCH_AUTOCONFIRM=1
            ("WORKBENCH_AUTOCONFIRM=1", "s", "remove_me/"),
            ("WORKBENCH_AUTOCONFIRM=1", "b", "remove_me/bench"),

            # Get WorkBench to create new resources if they don't exist
            ("WORKBENCH_AUTOCONFIRM=", "s -n -y", "remove_me/"),
            ("WORKBENCH_AUTOCONFIRM=", "b -n -y", "remove_me/bench"),
        ]
        for (prefix, wb_cmd, name) in inputs:
            new_flag = True if "-n" in wb_cmd else False
            self._test_rm_auto_confirmation(prefix, wb_cmd, name,
                                            new_flag=new_flag)


class TestWbExecute(unittest.TestCase):

    def _test_list_benches(self, c):
        o = run("WORKBENCH_ENV_NAME= "
                "WORKBENCH_HOME={td}/wbhome/simple {wb} {c}",
                replace=dict(c=c))
        benches = set(o.stdout.strip().split('\n'))
        self.assertEqual(benches, set([
            "outer/inner/simple1",
            "outer/inner/simple2"
        ]))
        self.assertEqual(o.returncode, 0)

    def test_wb_execute_commands_without_args_list_workbenches(self):
        """
        wb w|r|n
        Lists benches
        """
        for c in ["w", "r", "n"]:
            self._test_list_benches(c)

    def test_cant_create_new_bench_when_one_already_exists(self):
        """
        wb n <benchName> when <benchName> already exists raises error
        """
        o = run("WORKBENCH_ENV_NAME= WORKBENCH_HOME={td}/wbhome/simple "
                "{wb} n outer/inner/simple1")
        self.assertEqual(o.returncode, ERR_EXISTS)

    def _test_dump_verify_magic_string(self):
        """
        wb w|r|n --dump <benchName>
        Expect 'Auto-generated by WorkBench' in output
        """
        o = run("WORKBENCH_ENV_NAME= WORKBENCH_HOME={td}/wbhome/simple "
                "{wb} {c} outer/inner/simple1", replace=dict(c=c))
        lines = o.stdout.strip().split('\n')
        for line in lines:
            if "Auto-generated by WorkBench" in line:
                break
            self.fail("\"Auto-generated by WorkBench\" not found in dump")

    def _test_dump_works_on_all_execute_commands(self):
        """
        wb w|r|n --dump <benchName>
        """
        for c in ["w", "r", "n"]:
            self._test_dump_verify_magic_string(c)

    def test_dump_contents(self):
        mandatory = [
            "workbench_new () {",
            "workbench_activate () {",
            "workbench_deactivate () {",
            "workbench_command () {",
            "exit () {",
            "export WORKBENCH_ENV_NAME=",
            "export ORIG_PS1=",
            "export PS1=",
            "export WORKBENCH_ACTIVATE_FUNC=",
            "export WORKBENCH_COMMAND_FUNC=",
            "export WORKBENCH_NEW_FUNC=",
            "export WORKBENCH_DEACTIVATE_FUNC=",
        ]
        o = run("WORKBENCH_ENV_NAME= WORKBENCH_HOME={td}/wbhome/simple "
                "{wb} r --dump outer/inner/simple1")
        lines = o.stdout.strip().split('\n')

        for m in mandatory:
            found = False
            for line in lines:
                if line.startswith(m):
                    found = True
                    break
            if not found:
                self.fail("Did not find '{}' in dump".format(m))

    def test_invoke_run_on_bench(self):
        """
        wb r <benchName>
        """
        o = run("WORKBENCH_ENV_NAME= WORKBENCH_HOME={td}/wbhome/simple "
                "{wb} r outer/inner/simple1")
        stdout = [s.strip() for s in o.stdout.split('\n') if s.strip()]
        self.assertEqual(stdout, ["ROOT", "OUTER", "INNER", "SIMPLE1"])

    def test_invoke_activate_on_bench(self):
        """
        wb w <benchName>
        Activate -> exit

        NOTE: This test can hang if exit fails. TODO: Implement a failsafe
        """
        o = run("WORKBENCH_ENV_NAME= WORKBENCH_HOME={td}/wbhome/simple "
                "{wb} w outer/inner/simple1",
                input="exit\n", encoding="ascii")

    # -------- TODO ---------
    # The tests below work fine on Bash5 (tested on OSX)
    # They hang on bash 4.3.(48). Tested with Ubuntu:16.04 via docker.
    # Hence, they also hang on CircleCI and TravisCI.
    # Investigate further ...

    # def test_workbench_command_override_and_deactivate_on_exit(self):
    #     """
    #     Test with wb r <benchName>
    #     WORKBENCH_DEACTIVATE must get called on 'exit'

    #     Specifically designed for contents of outer/inner/simple1
    #     workbench_activate -> exit -> workbench_deactivate
    #     """
    #     o = run("WORKBENCH_ENV_NAME= "
    #             "WORKBENCH_COMMAND_FUNC=workbench_activate "
    #             "WORKBENCH_HOME={td}/wbhome/simple "
    #             "{wb} r outer/inner/simple1 1 2 3")
    #     stdout = [s.strip() for s in o.stdout.split('\n') if s.strip()]
    #     self.assertEqual(
    #         stdout,
    #         ["ROOT", "OUTER", "INNER", "SIMPLE1",
    #          "Default-Activated 1 2 3", "Default-Deactivated"]
    #     )

    # def test_workbench_new_get_invoked(self):
    #     """
    #     wb n <newBench>
    #     Creates a new bench and calls 'workbench_new' as the entrypoint

    #     'workbench_new' is written to 'wbhome/rm_test_new/wb.bench'
    #     The bench that is executed is 'wbhome/rm_test_new/nested/new_one.bench'
    #     The 'workbench_new' from the last sourced file (rm_test_new) will
    #     take effect.
    #     """
    #     rm_test_dir = join(TESTDATA, "wbhome/rm_test_new")
    #     try:
    #         if exists(rm_test_dir) and isdir(rm_test_dir):
    #             shutil.rmtree(rm_test_dir)
    #         shelf_file = get_shelf_filename(rm_test_dir, "")
    #         makedirs(rm_test_dir, exist_ok=True)
    #         with open(shelf_file, "w") as f:
    #             f.write("workbench_new () { echo \"Default-New\" $@; }\n")

    #         o = run("WORKBENCH_ENV_NAME= "
    #                 "WORKBENCH_HOME={td}/wbhome/rm_test_new "
    #                 "{wb} n nested/new_one 1 2 3")
    #         self.assertEqual(o.stdout.strip(), "Default-New 1 2 3")
    #     finally:
    #         shutil.rmtree(rm_test_dir)



# -----------------------------------------------------------------------------
#

if __name__ == "__main__":
    unittest.main()
