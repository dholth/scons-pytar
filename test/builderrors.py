
#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestSCons

test = TestSCons.TestSCons()

test.subdir('one', 'two', 'three')

test.write('build.py', r"""
import sys
exitval = int(sys.argv[1])
if exitval == 0:
    contents = open(sys.argv[3], 'r').read()
    file = open(sys.argv[2], 'w')
    file.write(contents)
    file.close()
sys.exit(exitval)
""")

test.write(['one', 'SConstruct'], """
B0 = Builder(name = 'B0', action = "python ../build.py 0 %(target)s %(source)s")
B1 = Builder(name = 'B1', action = "python ../build.py 1 %(target)s %(source)s")
env = Environment(BUILDERS = [B0, B1])
env.B1(target = 'f1.out', source = 'f1.in')
env.B0(target = 'f2.out', source = 'f2.in')
env.B0(target = 'f3.out', source = 'f3.in')
""")

test.write(['one', 'f1.in'], "one/f1.in\n")
test.write(['one', 'f2.in'], "one/f2.in\n")
test.write(['one', 'f3.in'], "one/f3.in\n")

test.run(chdir = 'one', arguments = "f1.out f2.out f3.out",
	 stderr = "scons: *** [f1.out] Error 1\n")

test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.write(['two', 'SConstruct'], """
B0 = Builder(name = 'B0', action = "python ../build.py 0 %(target)s %(source)s")
B1 = Builder(name = 'B1', action = "python ../build.py 1 %(target)s %(source)s")
env = Environment(BUILDERS = [B0, B1])
env.B0(target = 'f1.out', source = 'f1.in')
env.B1(target = 'f2.out', source = 'f2.in')
env.B0(target = 'f3.out', source = 'f3.in')
""")

test.write(['two', 'f1.in'], "two/f1.in\n")
test.write(['two', 'f2.in'], "two/f2.in\n")
test.write(['two', 'f3.in'], "two/f3.in\n")

test.run(chdir = 'two', arguments = "f1.out f2.out f3.out",
	 stderr = "scons: *** [f2.out] Error 1\n")

test.fail_test(test.read(['two', 'f1.out']) != "two/f1.in\n")
test.fail_test(os.path.exists(test.workpath('f2.out')))
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.write(['three', 'SConstruct'], """
B0 = Builder(name = 'B0', action = "python ../build.py 0 %(target)s %(source)s")
B1 = Builder(name = 'B1', action = "python ../build.py 1 %(target)s %(source)s")
env = Environment(BUILDERS = [B0, B1])
env.B0(target = 'f1.out', source = 'f1.in')
env.B0(target = 'f2.out', source = 'f2.in')
env.B1(target = 'f3.out', source = 'f3.in')
""")

test.write(['three', 'f1.in'], "three/f1.in\n")
test.write(['three', 'f2.in'], "three/f2.in\n")
test.write(['three', 'f3.in'], "three/f3.in\n")

test.run(chdir = 'three', arguments = "f1.out f2.out f3.out",
	 stderr = "scons: *** [f3.out] Error 1\n")

test.fail_test(test.read(['three', 'f1.out']) != "three/f1.in\n")
test.fail_test(test.read(['three', 'f2.out']) != "three/f2.in\n")
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.pass_test()
