#!/usr/bin/env python

__revision__ = "test/option-p.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-p')

test.fail_test(test.stderr() !=
		"Warning:  the -p option is not yet implemented\n")

test.pass_test()
 
