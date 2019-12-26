import unittest
import gdb_logger


class TestBreakpoints(unittest.TestCase):
    def test_breakpoints(self):
        fb=gdb_logger.FunctionBreakpoint('toy-c/main.cpp','main')
        self.assertEqual('-break-insert --source toy-c/main.cpp --function main',fb.to_gdbmi())

        lb=gdb_logger.LineBreakpoint('toy-c/main.cpp',15)
        self.assertEqual('-break-insert --source toy-c/main.cpp --line 15',lb.to_gdbmi())
    
