#!/usr/bin/env python3

import subprocess
import unittest

from os.path import abspath, dirname, join

WB_DIR=abspath(join(dirname(__file__), ".."))
TESTDATA=join(WB_DIR, "tests", "testdata")
WB=join(WB_DIR, "wb")
WB_DATA=dict(td=TESTDATA, wb=WB)


def run(cmd, **kwargs):
    if not isinstance(cmd, str):
        raise ValueError("Expected command to be a string")
    cmd = cmd.format(**WB_DATA)
    run_args = dict(
        shell=True, cwd=WB_DIR, timeout=5,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    run_args.update(kwargs)
    return subprocess.run(cmd, **run_args)


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
        stdout = o.stdout.decode('utf-8').split('\n')
        self.assertIn("WORKBENCH_TEST=___default___", stdout)
        self.assertEqual(o.returncode, 0)

    def test_consume_from_user_supplied_rc(self):
        """
        If a WORKBENCH_RC is defined, then source only supplied file.
        """
        o = run("WORKBENCH_RC={td}/rctest/custom.rc {wb} -E")
        stdout = o.stdout.decode('utf-8').split('\n')
        self.assertIn("WORKBENCH_TEST=___custom___", stdout)
        self.assertEqual(o.returncode, 0)

    def test_workbench_on_home_folder_with_no_workbenchrc(self):
        """
        WorkBench must run fine if $HOME does not have a .workbenchrc
        """
        o = run("HOME={td}/rctest/emptyfolder {wb} -E")
        stdout = o.stdout.decode('utf-8').split('\n')
        self.assertNotIn("WORKBENCH_TEST=", stdout)
        self.assertEqual(o.returncode, 0)

    def test_workbench_minus_E_lists_workbench_env_vars(self):
        """
        wb -E must list env var entries ^WORKBENCH_*
        """
        o = run("HOME={td}/rctest/emptyfolder {wb} -E")
        stdout = o.stdout.decode('utf-8').split('\n')
        for entry in stdout:
            if entry:
                self.assertTrue(entry.startswith("WORKBENCH_"))
        self.assertEqual(o.returncode, 0)


# -----------------------------------------------------------------------------
#

if __name__ == "__main__":
    unittest.main()
