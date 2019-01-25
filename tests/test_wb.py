#!/usr/bin/env python3

import subprocess
import unittest

from os.path import abspath, dirname, join

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

    def _test_list(self, cmd_char, expected):
        o = run("WORKBENCH_HOME={td}/wbhome {wb} {cmd_char}",
                replace=dict(cmd_char=cmd_char))
        expected = set(expected)
        actual = set(o.stdout.strip().split('\n'))
        self.assertEqual(expected, actual)

    def _test_path(self, cmd_char, values):
        wbhome = join(TESTDATA, "wbhome")
        for value in values:
            o = run("WORKBENCH_HOME={td}/wbhome {wb} {cmd_char} {value}",
                    replace=dict(cmd_char=cmd_char, value=value))
            actual = o.stdout.strip()
            if cmd_char == "s":
                # os.path.join: if a value is an absolute path (root)
                # all previous values are discarded (in this case 'wbhome')
                if value == "/":
                    value = ""
                expected = join(wbhome, value, "wb.shelf")
            else:   #   == "b"
                expected = join(wbhome, "{}{}".format(value, ".bench"))
            self.assertEqual(expected, actual)

    def test_shelves(self):
        SHELVES = [
            "/", "A/", "A/A1/", "A/A2/"
        ]
        self._test_list("s", SHELVES)
        self._test_path("s", SHELVES)

    def test_benches(self):
        BENCHES = [
            "A/A1/a1_1",
            "A/A1/a1_2",
            "A/A2/a2_1",
            "A/A2/a2_2",
        ]
        self._test_list("b", BENCHES)
        self._test_path("b", BENCHES)


# -----------------------------------------------------------------------------
#

if __name__ == "__main__":
    unittest.main()
