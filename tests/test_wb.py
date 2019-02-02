#!/usr/bin/env python3

import subprocess
import unittest

from os.path import abspath, dirname, join, basename

WB_DIR=abspath(join(dirname(__file__), ".."))
TESTDATA=join(WB_DIR, "tests", "testdata")
WB=join(WB_DIR, "wb")


def run(cmd, **kwargs):
    if not isinstance(cmd, str):
        raise ValueError("Expected command to be a string")
    replace = kwargs.pop("replace", {})
    wb_data = dict(td=TESTDATA, wb="bash {}".format(WB))
    wb_data.update(replace)
    cmd = cmd.format(**wb_data)
    run_args = dict(
        shell=True, cwd=WB_DIR, timeout=5,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    run_args.update(kwargs)
    cp = subprocess.run(cmd, **run_args)
    cp.stdout = cp.stdout.decode('utf-8')
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



# -----------------------------------------------------------------------------
#
#   Tests start here
#
# -----------------------------------------------------------------------------


class TestWb(unittest.TestCase):

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
        WorkBench must run fine if $HOME does not have a .workbenchrc
        """
        o = run("HOME={td}/rctest/emptyfolder {wb} -E")
        self.assertNotIn("WORKBENCH_TEST=", o.stdout.split('\n'))
        self.assertEqual(o.returncode, 0)

    def test_non_existent_workbench_rc_file_raises_error(self):
        filename = "this-file-does-not-exist.rc"
        o = run("WORKBENCH_RC={filename} {wb} -E",
                replace=dict(filename=filename))
        self.assertEqual(o.stdout, "")
        errmsg = "ERROR: Can't find WORKBENCH_RC: '{}'".format(filename)
        self.assertEqual(o.stderr.strip(), errmsg)
        self.assertEqual(o.returncode, 1)

    def test_list_workbench_env_vars(self):
        """
        wb -E must list env var entries ^WORKBENCH_*
        """
        o = run("HOME={td}/rctest/emptyfolder {wb} -E")
        for entry in o.stdout.strip().split('\n'):
            self.assertTrue(entry.startswith("WORKBENCH_"))
        self.assertEqual(o.returncode, 0)


    # LIST SHELVES AND BENCHES

    def test_list_simple_benches(self):
        o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} b")
        benches = set(o.stdout.strip().split('\n'))
        self.assertEqual(benches, set([
            "outer/inner/simple1",
            "outer/inner/simple2"
        ]))

    def test_list_simple_shelves(self):
        o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} s")
        benches = set(o.stdout.strip().split('\n'))
        self.assertEqual(benches, set([
            "/",
            "outer/",
            "outer/inner/"
        ]))

    # SHOW PATH TO SHELF AND BENCH FILES

    def _test_print_path_to_file(self, wb_cmd, name):
        get_filename = {
            "s": get_shelf_filename,
            "b": get_bench_filename
        }
        root_folder = join(TESTDATA, "wbhome", "simple")
        filename = get_filename[wb_cmd](root_folder, name)

        o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} {wb_cmd} {name}",
                replace=dict(wb_cmd=wb_cmd, name=name))
        self.assertEqual(filename, o.stdout.strip())

    def test_show_simple_bench_file(self):
        self._test_print_path_to_file("b", "outer/inner/simple1")
        self._test_print_path_to_file("b", "outer/inner/simple2")

    def test_show_simple_shelf_path(self):
        self._test_print_path_to_file("s", "/")
        self._test_print_path_to_file("s", "outer/")
        self._test_print_path_to_file("s", "outer/inner/")

    # RUN COMMAND ON A SHELF AND BENCH FILE

    def _test_command_on_file(self, wb_cmd, name):
        get_filename = {
            "s": get_shelf_filename,
            "b": get_bench_filename
        }
        root_folder = join(TESTDATA, "wbhome", "simple")
        filename = get_filename[wb_cmd](root_folder, name)

        cmd = "head -n 1"
        with open(filename) as f:
            lines = f.read().split('\n')
        self.assertTrue(len(lines) > 0)
        self.assertTrue(lines[0] != "")
        expected = lines[0]

        o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} {wb_cmd} {name} {cmd}",
                replace=dict(wb_cmd=wb_cmd, name=name, cmd=cmd))
        self.assertEqual(expected, o.stdout.strip())

    def test_run_command_on_bench_file(self):
        self._test_command_on_file("b", "outer/inner/simple1")

    def test_run_command_on_shelf_file(self):
        self._test_command_on_file("s", "outer/inner/")


    # EXIT 1 ON INVALID INPUTS

    def test_list_errors_on_bad_inputs(self):
        bad_inputs = [
            ("s", "invalid-shelf-missing-tailing-slash"),
            ("s", "valid/but/non/existent/shelf/"),
            ("b", "invalid-bench-having-tailing-slash/"),
            ("b", "valid/but/non/existent/bench"),
        ]
        for (wb_cmd, name) in bad_inputs:
            o = run("WORKBENCH_HOME={td}/wbhome/simple {wb} {wb_cmd} {name}",
                    replace=dict(wb_cmd=wb_cmd, name=name))
            self.assertEqual(o.returncode, 1)


# -----------------------------------------------------------------------------
#

if __name__ == "__main__":
    unittest.main()
