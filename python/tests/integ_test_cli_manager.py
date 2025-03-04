import unittest
import os
import logging
import sys
import shlex

# python 3 support
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import ccdb.cmd.colorama
from ccdb.errors import ObjectIsNotFoundInDbError
import ccdb.path_utils
import ccdb.cmd.themes
from ccdb.cmd.cli_manager import CliManager, CCDB_EXCEPTIONS_THROW
from ccdb import testing as helper


logger = logging.getLogger("ccdb")


def test_rm():
    """rm. General test... But rm is tested in other tests"""
    pass


class CliManagerTests(unittest.TestCase):
    """
    Tests of ccdb.ConsoleContext and all utilities
    """

    def setUp(self):
        # We need only sqlite tests. We test that we work with all databases in the provider fixture
        self.sqlite_connection_str = helper.sqlite_test_connection_str

        # DON'T USE COLORAMA IN TESTS. PyCharm test runner FAILS BECAUSE OF IT
        # DON'T - ccdb.cmd.colorama.init(autoreset=True)
        # DON'T - ccdb.cmd.colorama.deinit()
        # Copy the DB
        helper.copy_test_sqlite_db()

        # create console context
        self.cli = CliManager()
        self.cli.exception_handling = CCDB_EXCEPTIONS_THROW
        self.cli.force_exceptions = True
        self.cli.theme = ccdb.cmd.themes.NoColorTheme()
        self.cli.connection_string = self.sqlite_connection_str
        self.cli.context.user_name = "test_user"
        self.cli.register_utilities()

        # save stdout
        self.output = StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.output

        # logger
        ch = logging.StreamHandler()
        ch.stream = self.output
        logger.addHandler(ch)
        logger.setLevel(logging.INFO)

    def tearDown(self):
        # delete test file
        helper.clean_test_sqlite_db()

        # restore stdout
        sys.stdout = self.saved_stdout

    def clear_output(self):
        # Reset output
        self.output.seek(0)
        self.output.truncate()

    def test_context(self):
        """Test utils are loaded"""
        self.assertTrue(len(self.cli.utils) > 0)

    def test_cat(self):
        """cat. Return constants"""
        self.cli.process_command_line("cat /test/test_vars/test_table")
        self.assertIn("2.3", self.output.getvalue())

    def test_cat_interactive(self):
        """cat. Return constants"""
        # in interactive mode it should also work if the path is absolute
        self.cli.context.is_interactive = True
        self.cli.context.current_path = 'test/test_vars/'
        self.cli.process_command_line("cat test_table")
        self.assertIn("2.3", self.output.getvalue())

    def test_cat_by_id(self):
        """cat. Return """
        self.cli.process_command_line("cat -a 2")
        self.assertIn("6.0", self.output.getvalue())

        self.clear_output()

        # Same but full flag
        self.cli.process_command_line("cat --id=2")
        self.assertIn("6.0", self.output.getvalue())

    def test_cat_time(self):
        """cat. Test specifying time to get particular constants"""

        # Test data has next records for test_table:
        # /test/test_vars/test_table
        # (ID)   (Created)              (Modified)              (variation)     (run range)      (comments)
        #  5      2012-10-30 23-48-43    2012-10-30 23-48-43     subtest         0-inf           Test assignment for
        #  4      2012-10-30 23-48-42    2012-10-30 23-48-42     default         0-inf           Test assignment for
        #  2      2012-08-30 23-48-42    2012-08-30 23-48-42     test            500-3000        Test assignment for
        #  1      2012-07-30 23-48-42    2012-07-30 23-48-42     default         0-inf           Test assignment for

        # It should return assignment with --id=1
        self.cli.process_command_line('cat -t 2012-08 /test/test_vars/test_table')
        self.assertIn("1.11", self.output.getvalue())

    def test_cat_run_variation(self):
        """cat. If user sets ccdb -r <run> -v <variation> <command> ... it goes to context.current_run and context.current_variation.
           They should be used as a fallback by command if no run or variation is given to command
         """

        # Test DB has a test data assignment for:
        # variation: test
        # runs: 500-2000
        # it has data: 1.0|2.0|3.0|4.0|5.0|6.0
        self.cli.context.current_variation = "default"  # <= should not be used as cat overwrites variation
        self.cli.context.current_run = 0                # <= should not be used as cat overwrites run
        self.cli.process_command_line("cat -v test -r 600 /test/test_vars/test_table")
        self.assertIn("6.0", self.output.getvalue())

    def test_cat_default_run_variation(self):
        """If user sets ccdb -r <run> -v <variation> <command> ... it goes to context.current_run and context.current_variation.
           They should be used as a fallback by command if no run or variation is given to command
         """

        # Test DB has a test data assignment for:
        # variation: test
        # runs: 500-2000
        # it has data: 1.0|2.0|3.0|4.0|5.0|6.0
        self.cli.context.current_variation = "test"
        self.cli.context.current_run = 600
        self.cli.process_command_line("cat /test/test_vars/test_table")
        self.assertIn("6.0", self.output.getvalue())

    def test_cat_request_overwrite(self):
        """cat. If user sets ccdb -r <run> -v <variation> cat <request> ... But the requests sets different run and
           and variation, then request has the top priority
         """

        # Test DB has a test data assignment for:
        # variation: test
        # runs: 500-2000
        # it has data: 1.0|2.0|3.0|4.0|5.0|6.0
        self.cli.context.current_variation = "default"  # <= should not be used as cat overwrites variation
        self.cli.context.current_run = 0                # <= should not be used as cat overwrites run
        self.cli.process_command_line("cat -v default -r 0 /test/test_vars/test_table:600:test")
        self.assertIn("6.0", self.output.getvalue())

    def test_cat_not_abs_path(self):
        """In non-interactive mode, cat should handle path without leading / as absolute anyway"""
        self.cli.process_command_line("cat test/test_vars/test_table")
        self.assertIn("2.3", self.output.getvalue())

        # in interactive mode it should also work if the path is absolute
        self.cli.context.is_interactive = True
        self.cli.process_command_line("cat test/test_vars/test_table")
        self.assertIn("2.3", self.output.getvalue())

    def test_variation_backup(self):
        """Test Backup of """

        self.cli.process_command_line("cat /test/test_vars/test_table:100:test")
        self.assertIn("2.2", self.output.getvalue())

    def test_cd(self):
        """cd. General test"""
        self.cli.process_command_line("cd test")

    def test_help(self):
        """help. Help command test"""
        self.cli.process_command_line("help")
        self.assertIn("ls", self.output.getvalue())

    def test_howto(self):
        """How-to. General test"""
        self.cli.process_command_line("howto")

    def test_dump(self):
        """dump. General and output tests"""
        self.cli.theme = ccdb.cmd.themes.ColoredTheme()
        self.cli.process_command_line("dump /test/test_vars/test_table")
        text = self.output.getvalue()
        self.assertNotIn("[", text, "Check that dump disabled color output")

        # cleanup
        self.cli.theme = ccdb.cmd.themes.NoColorTheme()
        self.output.truncate(0)

    def test_info(self):
        """info. General test"""
        self.cli.process_command_line("info /test/test_vars/test_table")
        out_str = self.output.getvalue()
        self.assertIn("test_table", out_str)
        self.assertIn("Test type", out_str)
        self.assertIn("z", out_str)

    def test_ls(self):
        """ls. General test"""
        self.cli.process_command_line("ls")
        self.assertIn("test", self.output.getvalue())

    def test_ls_table(self):
        """ls. General test"""
        self.cli.process_command_line("ls /test/test_vars/test_table")
        self.assertIn("test", self.output.getvalue())

    def test_mk_rm_dir(self):
        """mkdir, rm. Create directory and delete it"""
        self.cli.process_command_line("mkdir /test/auto_testing_dir #Comment for the dir\n something at new line")

        # TODO check test table internals are right
        self.cli.process_command_line("rm --force -d /test/auto_testing_dir")

    def test_mktbl_from_file(self):
        """mkdir infer table structure from file"""
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(tests_dir, "test_table.txt")
        self.cli.process_command_line("mktbl -f " + test_file)
        out_str = self.output.getvalue()
        self.assertIn("mktbl <name> -r 2 X Y Z #<comments>", out_str)

        # now lets check more complex example, where we set table name and comment
        self.output.truncate(0)
        self.cli.process_command_line("mktbl /test/haha -f " + test_file + " #harasho")
        out_str = str(self.output.getvalue())
        self.assertIn("mktbl /test/haha -r 2 X Y Z #harasho", out_str)

    def test_mk_rm_table(self):
        """mktbl, rm. Create table and delete it"""
        self.cli.process_command_line("mktbl /test/auto_testing_table -r 2 x y z #This is comment for my table")
        # TODO check test table internals are right
        self.cli.process_command_line("rm --force /test/auto_testing_table")

    def test_mk_rm_variation(self):
        """mkvar, rm. Create variation and delete it"""
        self.cli.process_command_line("mkvar auto_testing_variation -p test #hahaha")
        self.cli.process(["mkvar", "auto_testing_variation2", "-p", "test"], 0)  # Regression test for GitHub #3
        # TODO check test table internals are right
        self.cli.process_command_line("rm --force -v auto_testing_variation")
        self.cli.process_command_line("rm --force -v auto_testing_variation2")

    def test_add_rm_assignment(self):
        """add, rm. Add constants and remove them"""
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(tests_dir, "test_table.txt")
        print(test_file)
        self.cli.process_command_line("add /test/test_vars/test_table " + test_file)
        self.output.truncate(0)
        self.cli.process_command_line("vers /test/test_vars/test_table")
        text = str(self.output.getvalue())
        line = text.split("\n")[1]
        assignment_id = int(shlex.split(line)[0])
        self.cli.process_command_line("rm -f -a {0}".format(assignment_id))

    def test_add_with_run_range_assignment(self):
        """Regression tests for failing add with run range"""
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(tests_dir, "test_table.txt")
        print(test_file)
        self.cli.process_command_line("add -r 0-1000 /test/test_vars/test_table " + test_file)
        self.output.truncate(0)
        self.cli.process_command_line("vers /test/test_vars/test_table")
        text = str(self.output.getvalue())
        line = text.split("\n")[1]
        assignment_id = int(shlex.split(line)[0])
        self.cli.process_command_line("rm -f -a {0}".format(assignment_id))

    def test_pwd(self):
        """pwd. General test"""
        self.cli.process_command_line("pwd")
        self.assertIn("/", self.output.getvalue())

    def test_run(self):
        """run. Test if 0 is default run"""
        self.cli.process_command_line("run")
        self.assertIn("0", self.output.getvalue())

    def test_run_change(self):
        """run. Test run is changed"""
        self.cli.process_command_line("run 1")
        self.output.truncate(0)
        self.cli.process_command_line("run")
        self.assertIn("1", self.output.getvalue())

    def test_var(self):
        """var. Test if 'default' variation is default"""
        # default run is 0
        self.cli.process_command_line("var")
        self.assertIn("default", self.output.getvalue())

    def test_var_change(self):
        """var. Test variation change"""
        self.cli.process_command_line("var test_var")
        self.output.truncate(0)
        self.cli.process_command_line("var")
        self.assertIn("test_var", self.output.getvalue())

    def test_vers(self):
        """vers. General usage test"""
        self.cli.process_command_line("vers /test/test_vars/test_table")
        result = self.output.getvalue()

        # REGRESSION test: for v. 1.02, doesn't show data if context default run is not in run-range
        self.assertIn("500-3000", result, "Because test_table has data for 500-3000 run-range")

    def test_vers_variation_run(self):
        """vers. Test if vers limits variation and run range if -v and -r flags are given"""
        self.cli.process_command_line("vers /test/test_vars/test_table -v default -r 0")
        result = self.output.getvalue()

        self.assertNotIn("subtest", result)
        self.assertNotIn("500-3000", result)  # There is test data for 500-3000 run-range

    def test_vers_bad_params(self):
        """vers. Test vers bad parameters"""

        # wrong directory
        self.assertRaises(ObjectIsNotFoundInDbError, self.cli.process_command_line, "vers /some/wrong/dir/table")
        self.assertRaises(ObjectIsNotFoundInDbError, self.cli.process_command_line, "vers /test/test_vars/wrong_table")

    def test_skip_sqlite_logging(self):
        """
        check that for sqlite connection user name is skipped
        """
        self.cli.process_command_line("ls")  # run command that requires connection make it to connect
        self.assertFalse(self.cli.provider.logging_enabled)

    def test_log(self):
        """
        log. general test
        """
        self.cli.process_command_line("log")
