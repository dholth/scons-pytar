"""
TestSCons.py:  a testing framework for the SCons software construction
tool.

A TestSCons environment object is created via the usual invocation:

    test = TestSCons()

TestScons is a subclass of TestCmd, and hence has available all of its
methods and attributes, as well as any overridden or additional methods
or attributes defined in this subclass.
"""

# Copyright 2001, 2002, 2003 Steven Knight

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import os.path
import string
import sys

import TestCmd

python = TestCmd.python_executable

class TestFailed(Exception):
    def __init__(self, args=None):
        self.args = args

class TestNoResult(Exception):
    def __init__(self, args=None):
        self.args = args

if os.name == 'posix':
    def _failed(self, status = 0):
        if self.status is None:
            return None
        if os.WIFSIGNALED(self.status):
            return None
        return _status(self) != status
    def _status(self):
        if os.WIFEXITED(self.status):
            return os.WEXITSTATUS(self.status)
        else:
            return None
elif os.name == 'nt':
    def _failed(self, status = 0):
        return not self.status is None and self.status != status
    def _status(self):
        return self.status

class TestSCons(TestCmd.TestCmd):
    """Class for testing SCons.

    This provides a common place for initializing SCons tests,
    eliminating the need to begin every test with the same repeated
    initializations.
    """

    def __init__(self, **kw):
	"""Initialize an SCons testing object.

	If they're not overridden by keyword arguments, this
	initializes the object with the following default values:

		program = 'scons' if it exists,
			  else 'scons.py'
		interpreter = 'python'
		match = TestCmd.match_exact
		workdir = ''

        The workdir value means that, by default, a temporary workspace
        directory is created for a TestSCons environment.  In addition,
	this method changes directory (chdir) to the workspace directory,
	so an explicit "chdir = '.'" on all of the run() method calls
	is not necessary.
	"""
	if not kw.has_key('program'):
            kw['program'] = os.environ.get('SCONS')
            if not kw['program']:
                if os.path.exists('scons'):
                    kw['program'] = 'scons'
                else:
                    kw['program'] = 'scons.py'
	if not kw.has_key('interpreter') and not os.environ.get('SCONS_EXEC'):
	    kw['interpreter'] = python
	if not kw.has_key('match'):
	    kw['match'] = TestCmd.match_exact
	if not kw.has_key('workdir'):
	    kw['workdir'] = ''
	apply(TestCmd.TestCmd.__init__, [self], kw)
	os.chdir(self.workdir)

    def run(self, options = None, arguments = None,
                  stdout = None, stderr = '', status = 0, **kw):
	"""Runs SCons.

        This is the same as the base TestCmd.run() method, with
        the addition of:

		stdout	The expected standard output from
			the command.  A value of None means
			don't test standard output.

		stderr	The expected error output from
			the command.  A value of None means
			don't test error output.

                status  The expected exit status from the 
                        command. 

        By default, this does not test standard output (stdout = None),
        and expects that error output is empty (stderr = "").
	"""
        if options:
            arguments = options + " " + arguments
        kw['arguments'] = arguments
	try:
	    apply(TestCmd.TestCmd.run, [self], kw)
	except:
	    print "STDOUT ============"
	    print self.stdout()
	    print "STDERR ============"
	    print self.stderr()
	    raise
	if _failed(self, status):
            expect = ''
            if status != 0:
                expect = " (expected %s)" % str(status)
            print "%s returned %s%s" % (self.program, str(_status(self)), expect)
            print "STDOUT ============"
            print self.stdout()
	    print "STDERR ============"
	    print self.stderr()
	    raise TestFailed
	if not stdout is None and not self.match(self.stdout(), stdout):
                print "Expected STDOUT =========="
                print stdout
                print "Actual STDOUT ============"
                print self.stdout()
                stderr = self.stderr()
                if stderr:
                    print "STDERR ==================="
                    print stderr
                raise TestFailed
	if not stderr is None and not self.match(self.stderr(), stderr):
            print "STDOUT ==================="
            print self.stdout()
	    print "Expected STDERR =========="
	    print stderr
	    print "Actual STDERR ============"
	    print self.stderr()
	    raise TestFailed

    def detect(self, var, prog):
        """
        Detect a program named 'prog' by first checking  the construction 
        variable named 'var' and finally searching the path. If either method
        fails to detect the program, then false is returned, otherwise 
        the programs full path is returned.
        """

        import SCons.Environment
        try:
            return SCons.Environment.Environment()[var] == prog and self.where_is(prog)
        except KeyError:
            return None

    def wrap_stdout(self, build_str = "", read_str = ""):
        """Wraps standard output string(s) in the normal
        "Reading ... done" and "Building ... done" strings
        """
        return "scons: Reading SConscript files ...\n" + \
               read_str + \
               "scons: done reading SConscript files.\n" + \
               "scons: Building targets ...\n" + \
               build_str + \
               "scons: done building targets.\n"

    def up_to_date(self, options = None, arguments = None, **kw):
        s = ""
        for arg in string.split(arguments):
            s = s + 'scons: "%s" is up to date.\n' % arg
            if options:
                arguments = options + " " + arguments
        kw['arguments'] = arguments
        kw['stdout'] = self.wrap_stdout(build_str = s)
        apply(self.run, [], kw)
