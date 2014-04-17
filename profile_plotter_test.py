#!/usr/bin/env python
"""profile_plotter_test"""

import unittest
import os
from profile_plotter import *
from profile_plotter_helpers import *

class TestPlotEntry(unittest.TestCase):
    """Test the PlotEntry functions"""
    def setUp(self):
        self.plotE = PlotEntry(2, 1, 'b', 100, '', '')

    def test_add_colour_ok(self):
        """add an ok colour"""
        self.assertEqual(self.plotE.add_colour('red'), 'red')

    def test_add_colour_no(self):
        self.assertEqual(self.plotE.add_colour('blarg'), 'black')
    
    def test_add_number(self):
        self.assertEqual(self.plotE.add_number(1), 1)


class TestPlotInfo(unittest.TestCase):
    """Test the PlotEntry functions"""
    def setUp(self):
        self.plotI = PlotInfo()
        self.indata = [
            '1, -100, "1", , black',
            '2, -80, "TS2", , black',
            '3, -105, "Int3", , black',
            '4, -92, "TS4", , black',
            '5, -110, "Int5", , black',
            '6, -72, "TS6", , black',
            '7, -120, "Prod7", , black',
            '8, -97, "Int 8", 4, blue',
            '9, -85, "TS9", 8, blue',
            '10, -102, "10", 9, blue',
            '11, -77, "TS 11", 10, blue',
            '12, -130, "12 + 13", 11, blue',
        ]

    def test_add_title(self):
        """adds a title to the plot"""
        self.plotI.add_title('Test')
        self.assertEqual(self.plotI.title, 'Test')

    def test_add_ok_filename(self):
        """Adds a filename and ok filetype"""
        self.plotI.add_filename("test1.png")
        self.assertEqual(self.plotI.filename, 'test1.png')

    def test_add_bad_filename(self):
        """Adds a file name with bad filetype"""
        self.plotI.add_filename("test1.blarg")
        self.assertEqual(self.plotI.filename, 'test1.png')

    def test_add_2_dimensions(self):
        """Test 2 dimension input"""
        self.plotI.add_dimensions("600, 400")
        self.assertEqual(self.plotI.width + self.plotI.height, 1000)

    def test_add_3_dimensions(self):
        """Test 3 dimension input"""
        self.plotI.add_dimensions("600, 400, 200")
        self.assertEqual(self.plotI.dpi, 200)

    def test_add_ok_inunits(self):
        """Test adding good input units"""
        self.plotI.add_inunits("hartrees")
        self.assertEqual(self.plotI.inunits, "hartrees")

    def test_add_bad_inunits(self):
        """Test adding bad input units"""
        with self.assertRaises(UnitError) as cm:
            self.plotI.add_inunits("blarg")
        the_exception = cm.exception

    def test_add_units(self):
        self.plotI.add_units("hartrees, kj/mol")
        self.assertEqual(self.plotI.outunits, "kj/mol")

    def test_add_outunits(self):
        """Make sure outunits are ok too."""
        self.plotI.add_outunits("kj/mol")
        self.assertEqual(self.plotI.outunits, "kj/mol")

    def test_add_reference_line(self):
        """Test adding a reference line to the plot"""
        self.plotI.add_reference(7)
        self.assertEqual(self.plotI.reference_line, 7)

    def test_parsing_data(self):
        """Test data parsing"""
        self.plotI.add_reference(1)
        self.plotI.add_inunits('hartrees')
        self.plotI.add_outunits('kj/mol')
        self.plotI.parsedata(self.indata)
        self.plotI.generate_vectors()
        self.assertEqual(self.plotI.maxxindex, 9)

    def test_generating_vectors(self):
        """Test Vector Generation"""
        self.plotI.add_reference(1)
        self.plotI.add_inunits('hartrees')
        self.plotI.add_outunits('kj/mol')
        self.plotI.parsedata(self.indata)
        self.plotI.generate_vectors()
        self.assertEqual(self.plotI.vectors[0],
                         [[0.835, 1.165], [0.0, 0.0], '-', 'black', 3])


    def test_generating_texts(self):
        """Same code, generate texts instead"""
        self.plotI.add_reference(1)
        self.plotI.add_inunits('hartrees')
        self.plotI.add_outunits('kj/mol')
        self.plotI.parsedata(self.indata)
        self.plotI.generate_vectors()
        self.assertEqual(self.plotI.texts[0],
                         [1, 2205.42, '"1"', 'black', 'bottom', 'center', 'white', False])


class TestParseFile(unittest.TestCase):
    """Test the PlotEntry functions"""
    def setUp(self):
        inputfile = [
            'TestPlot',
            'testplot.png',
            '400, 600, 1100',
            'hartrees, kj/mol',
            '4',
            '1, -100, "1", , black',
            '2, -80, "TS2", , black',
            '3, -105, "Int3", , black',
            '4, -92, "TS4", , black',
            '5, -110, "Int5", , black',
            '6, -72, "TS6", , black',
            '7, -120, "Prod7", , black',
            '8, -97, "Int 8", 4, blue',
            '9, -85, "TS9", 8, blue',
            '10, -102, "10", 9, blue',
            '11, -77, "TS 11", 10, blue',
            '12, -130, "12 + 13", 11, blue',
        ]
        write_file('inputfile.txt', inputfile)
        self.plot = parse_file('inputfile.txt')

    def tearDown(self):
        os.remove("inputfile.txt")

    def test_plot_title(self):
        "see if title parsed ok"
        self.assertEqual(self.plot.title, 'TestPlot')

    def test_plot_filename(self):
        "see if filename parsed ok"
        self.assertEqual(self.plot.filename, 'testplot.png')

    def test_plot_dimensions(self):
        "see if dimensions are ok"
        self.assertEqual(self.plot.dpi, 1100)

    def test_plot_units(self):
        "see if units are ok"
        self.assertEqual(self.plot.outunits, 'kj/mol')

    def test_plot_reference(self):
        "see if reference is ok"
        self.assertEqual(self.plot.reference_line, 4)

    def test_plot_text(self):
        "see if text was generated ok"
        self.assertEqual(self.plot.texts[0],
                         [1, -7.4, '"1"', 'black', 'bottom', 'center', 'white', False])

    def test_plot_vectors(self):
        "see if vectors was generated ok"
        self.assertEqual(self.plot.vectors[0],
                         [[0.835, 1.165], [-8.0, -8.0], '-', 'black', 3])



if __name__ == '__main__':
    unittest.main(verbosity=2)

