#!/usr/bin/env python
#profile_plotter_helpers

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COLOURS ={  # Colours from IEC60757
    'black': ['black', 'bk'],
    'brown': ['brown', 'bn'],
    'red': ['red', 'rd'],
    'orange': ['orange', 'og'],
    'yellow': ['yellow', 'ye'],
    'green': ['green', 'gn'],
    'blue': ['blue', 'bl'],
    'cyan': ['cyan', 'cy'],
    'violet': ['violet', 'purple', 'vt', 'pr'],
    'grey': ['grey', 'gray', 'gy'],
    'white': ['white', 'wh'],
    'pink': ['pink', 'pk'],
    'darkblue': ['dark blue', 'db'],
    'lightblue': ['light blue', 'lb'],
    'lime': ['lime', 'lm'],
    'magenta': ['magenta', 'mg'],
    'maroon': ['maroon', 'mr'],
    'olive': ['olive', 'ov'],
    }
UNIT_LIST=['hartrees','kj/mol', 'kcal/mol', 'ev', 'cm-1']
CONVERSION = {
    'hartrees':[1, 2625.50, 627.51, 27.212, 219474],
    'kj/mol' :[0.00038088, 1, 0.23901, 0.010364, 83.593],
    'kcal/mol': [0.0015936, 4.1840, 1, 0.043363, 349.75],
    'ev': [0.036749, 96.485, 23.061, 1, 8065.5],
    'cm-1': [0.0000045563, 0.011963, 0.0028591, 0.00012398, 1]
    }


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class FormatError(Error):
    """
    Error in input file due to syntax
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg


class FileAccessError(Error):
    """Error accessing file"""
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg


class DimensionError(Error):
    """Error in dimensions in input
    Attributes: dim = dimensions"""
    def __init__(self, dim):
        self.dim = dim
        self.msg = "Dimensions of {} not valid.".format(dim)


class UnitError(Error):
    """Error in units in input
    Attributes: unit = units"""
    def __init__(self, unit):
        self.unit = unit
        self.msg = "Units of {} not valid.".format(self.unit)


def check_files_exist(filelist):
    """Checks for the existance of file(s)"""
    allexist = True
    for f in filelist:
        if not os.path.isfile(f):
            allexist = False
            break
    return allexist


def read_clean_file(filename):
    """Reads in a file, cleaning line endings and returning a list of lines"""
    try:
        with open(filename, 'r') as f:
            ilines = f.readlines()
    except Exception as e:
        raise FileAccessError("Error reading file {}.".format(filename), e)

    lines = list()
    for line in ilines:
        lines.append(line.strip())

    return lines


def check_format(fmt):
    """Compare the requested format to the list of available. If not good,
    return png (default) or svg, or raise error."""
    fig = plt.figure()
    formats = fig.canvas.get_supported_filetypes()
    if formats.has_key(fmt):
        return fmt
    elif formats.has_key('png'):
        return 'png'
    elif formats.has_key('svg'):
        return 'png'
    else:
        raise FormatError(
            fmt,
            'Unknown file format. Could not find alternate format.')


def is_int(num):
    """Test the input num to be an int. Return True/False"""
    try:
        int(num)
        return True
    except ValueError:
        return False


def is_float(num):
    """Test the input number to be a float. Return True/False"""
    try:
        float(num)
        return True
    except ValueError:
        return False


def is_positive_int(num):
    """Test the input to be a positive integer"""
    if is_int(num):
        if int(num) >= 0:
            return True
        else:
            return False
    else:
        return False


def convert_units(value, inunit, outunit):
    """Convert a value from inunit to outunits."""
    if inunit not in UNIT_LIST:
        raise UnitError(inunit)
    elif outunit not in UNIT_LIST:
        raise UnitError(outunit)
    return value * CONVERSION[inunit][UNIT_LIST.index(outunit)]


def write_file(filename, lines):
    """Writes a file 'filename' from lines"""
    try:
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line + '\n')
    except Exception as e:
        raise FileAccessError("Error writing file {}.".format(filename), e)
