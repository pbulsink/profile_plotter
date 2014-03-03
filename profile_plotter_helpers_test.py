#!/usr/bin/env python
"""profile_plotter_helpers_test"""

import unittest
import os
from profile_plotter_helpers import *
import matplotlib.pyplot as plt

class TestSimpleFuncs(unittest.TestCase):
    """Test the simple functions"""
    
    def setUp(self):
        write_file('testfile1', ['testfile1',''])
        write_file('testfile2', ['testfile2',''])
        write_file('testread.txt', ['Hello', 'This is a test read file'])

    def tearDown(self):
        os.remove('testfile1')
        os.remove('testfile2')
        os.remove('testread.txt')

    def testreadcleanfile(self):
        """Test reading a clean file"""
        infile = read_clean_file('testread.txt')
        self.assertEqual(infile, ['Hello', 'This is a test read file'])
    
    def test_is_int_int(self):
        """Test the is_int function with a good int"""
        self.assertEqual(is_int(1), True)

    def test_is_int_string(self):
        """Test the is_int function with a good str"""
        self.assertEqual(is_int('1'), True)

    def test_is_int_negative(self):
        """Test the is_int function with a good negative string"""
        self.assertEqual(is_int('-1'), True)

    def test_is_int_float(self):
        """Test the is_int function with a bad float"""
        self.assertEqual(is_int('1.01'), False)

    def test_is_int_fail(self):
        """Test the is_int function with a bad string"""
        self.assertEqual(is_int('one'), False)

    def test_is_positive_int_pgood(self):
        """Test the is_positive_int function with a good value"""
        self.assertEqual(is_positive_int(1), True)

    def test_is_positive_int_ngood(self):
        """Test the is_positive_int function with a bad value"""
        self.assertEqual(is_positive_int(-1), False)

    def test_is_positive_int_string(self):
        """Test the is_positive_int function with a good string"""
        self.assertEqual(is_positive_int('1'), True)

    def test_is_positive_int_negative(self):
        """Test the is_positive_int function with a bad string"""
        self.assertEqual(is_positive_int('-1'), False)

    def test_is_positive_int_fail(self):
        """Test the is_positive_int function with a bad word"""
        self.assertEqual(is_positive_int('one'), False)

    def test_file_exists_true(self):
        """Test the file_exists function with a list"""
        self.assertEqual(check_files_exist(['testfile1', 'testfile2']), True)

    def test_file_exists_false(self):
        """Test the file_exists function with a file not exists"""
        self.assertEqual(check_files_exist(['testfile3']), False)

    def test_convert_units(self):
        """Test conversion between two units"""
        self.assertAlmostEqual(convert_units(-1, 'hartrees', 'kj/mol'), -2625.50)

    def test_convert_units2(self):
        """One more test with a multiplyer factor"""
        self.assertAlmostEqual(convert_units(-10, 'kj/mol', 'cm-1'), -835.93)

    def test_check_format(self):
        """See if check-format works"""
        self.assertEqual(check_format('jpg'), 'jpg')

    def test_check_bad_format(self):
        """See if check-format fails ok"""
        self.assertEqual(check_format('blurg'), 'png')

    def test_is_float_pgood(self):
        """Test the is_float function with a good value"""
        self.assertEqual(is_float(1.01), True)

    def test_is_float_ngood(self):
        """Test the is_float function with a good negative"""
        self.assertEqual(is_float(-1.01), True)

    def test_is_float_string(self):
        """Test the is_float function with a good string"""
        self.assertEqual(is_float('1.01'), True)

    def test_is_float_negative(self):
        """Test the is_float function with a good negative string"""
        self.assertEqual(is_float('-1.01'), True)

    def test_is_float_int(self):
        """Test the is_float function with a good int"""
        self.assertEqual(is_float(1), True)

    def test_is_float_strint(self):
        """Test the is_float function with a good int string"""
        self.assertEqual(is_float('1'), True)

    def test_is_float_fail(self):
        """Test the is_float function with a bad string"""
        self.assertEqual(is_float('one'), False)

if __name__ == '__main__':
    unittest.main(verbosity=2)

