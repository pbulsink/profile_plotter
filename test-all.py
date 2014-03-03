#!/usr/bin/env python
"""Testall.py"""

from unittest import TestLoader, TextTestRunner, TestSuite
from profile_plotter_test import TestParseFile, TestPlotEntry, TestPlotInfo
from profile_plotter_helpers_test import TestSimpleFuncs

if __name__ == "__main__":
    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(TestParseFile),
        loader.loadTestsFromTestCase(TestPlotEntry),
        loader.loadTestsFromTestCase(TestPlotInfo),
        loader.loadTestsFromTestCase(TestSimpleFuncs)
                ))

    runner = TextTestRunner(verbosity = 2)
    runner.run(suite)

