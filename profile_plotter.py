#!/usr/bin/env python
#Profile Plotter
#Programmer: Philip Bulsink
#Licence: BSD
#Plots reaction profiles using matplotlib by reading in energies from a file.
#See the readme.md file for more information

from profile_plotter_helpers import *

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.path as Path

import argparse
from os import path


class PlotEntry:
    """Holds individual entries to the plot object"""
    def __init__(self, number, connected_to, colour, energy, image, text):
        self.number = self.add_number(number)
        self.xindex = self.add_number(number)
        self.add_connected(connected_to)
        self.colour = self.add_colour(colour.strip())
        self.energy = self.add_energy(energy)
        self.image = self.check_image(image)
        self.text = text[:24]

    def add_colour(self, colour):
        """
        make sure the colour is in the list and standardize the possible output
        """
        if colour.lower() in COLOURS:
            return colour.lower()
        for key in COLOURS:
            if colour.lower() in key:
                return colour.lower()
        return 'black'

    def check_image(self, image):
        """
        Ensure the plot file exists.. Maybe change to checking for image file?
        """
        if image != "" and check_files_exist([image]):
            return image
        return None

    def add_number(self, number):
        """Make sure number makes sense"""
        if is_positive_int(number):
            return int(number)
        else:
            raise FormatError(number, "Number {} not valid.".format(number))

    def add_connected(self, connection):
        if is_positive_int(connection):
            self.connected_to = int(connection)
        else:
            self.connected_to = ''

    def add_energy(self, eng):
        if is_float(eng):
            return float(eng)
        else:
            raise FormatError(eng, "Energy {} not valid.".format(eng))


class PlotInfo:
    """Holds the info for the plot as an object"""
    def __init__(self):
        self.title = ''
        self.filename = ''
        self.filetype = 'png'
        self.width = 600
        self.height = 400
        self.inunits = 'hartree'
        self.outunits = 'kj/mol'
        self.reference_line = 1
        self.maxenergy = -0.0
        self.minenergy = 0.0
        self.maxxindex = 0

    def add_title(self, title):
        """Adds a title to the PlotInfo"""
        self.title = title

    def add_filename(self, filename):
        """Adds a filename to the PlotInfo"""
        self.filename = filename
        ftype = path.splitext(filename)[1][1:]
        self.filetype = check_format(ftype)
        if ftype != self.filetype:
            self.filename = path.splitext(filename)[0] + '.' + self.filetype

    def add_dimensions(self, dimensions):
        """Adds dimensions to the PlotInfo"""
        dim = dimensions.split(', ')
        if len(dim) == 2:
            try:
                self.width = int(dim[0])
                self.height = int(dim[1])
            except ValueError:
                raise DimensionError(dimensions)
            else:
                self.dpi = 1200
        elif len(dim) == 3:
            try:
                self.width = int(dim[0])
                self.height = int(dim[1])
                self.dpi = int(dim[2])
            except ValueError:
                raise DimensionError(dimensions)
        else:
            raise DimensionError(dimensions)

    def add_units(self, units):
        u = units.split(', ')
        if len(u) != 2:
            raise UnitError(units)
        self.add_inunits(u[0])
        self.add_inunits(u[1])

    def add_inunits(self, units):
        """Adds input units to the PlotInfo"""
        if units in UNIT_LIST:
            self.inunits = units
        else:
            raise UnitError(units)

    def add_outunits(self, units):
        """Adds output units to the PlotInfo"""
        if units in UNIT_LIST:
            self.outunits = units
        else:
            raise UnitError(units)

    def add_reference(self, reference):
        """Adds zero reference to the PlotInfo"""
        if is_int(reference):
            self.reference_line = int(reference)
        else:
            raise FormatError(reference, "Error in reference line syntax: {}."
                              .format(reference))

    def parsedata(self, inputdata):
        """Parse the rest of the data into the Infolist"""
        self.plotdata = list()
        for l in inputdata:
            d = l.split(',')
            if len(d) == 3:
                d.append(d[0] - 1)
            while len(d) < 6:
                d.append("")
            
            self.plotdata.append(PlotEntry(d[0], d[3], d[4], d[1], d[5], d[2]))

        if self.reference_line > len(self.plotdata):
            raise FormatError(self.reference_line,
                              "Can't refrerence to line {}. only {} lines exist."
                              .format(self.reference_line, len(self.plotdata)))
        #fixing the xindex values for the datapoints, and changing energy to
        #output units
        self.plotdata[0].xindex = 1
        self.plotdata[0].energy = convert_units(float(self.plotdata[0].energy),
                                                self.inunits, self.outunits)
        self.maxenergy = self.plotdata[0].energy
        self.minenergy = self.plotdata[0].energy
        self.maxxindex = self.plotdata[0].xindex
        for p in self.plotdata[1:]:
            if not p.connected_to:
                p.add_connected(p.number - 1)
            p.xindex = self.plotdata[p.connected_to - 1].xindex+1
            p.energy = convert_units(float(p.energy), self.inunits, self.outunits)
            if p.energy < self.minenergy:
                self.minenergy = p.energy
            elif p.energy > self.maxenergy:
                self.maxenergy = p.energy
            if p.xindex > self.maxxindex:
                self.maxxindex = p.xindex
        #zeroing plotdata to reference (if needed)
        if self.reference_line != 0:
            ref = self.plotdata[self.reference_line - 1].energy
            for p in self.plotdata:
                p.energy = p.energy - ref
            self.maxenergy = self.maxenergy - ref
            self.minenergy = self.minenergy - ref

    def generate_vectors(self):
        self.vectors = list()
        self.texts = list()
        #vectors are ([x,x], [y,y], 'colour,style')
        for i in range(len(self.plotdata)):
            pthis = self.plotdata[i]
            if i != len(self.plotdata) - 1:
                pnext = self.plotdata[i+1]
            else:
                pnext = False
            
            point = [[pthis.xindex - 0.165, pthis.xindex + 0.165],
                     [pthis.energy, pthis.energy], '-', pthis.colour, 2]
            self.vectors.append(point)
            t = [pthis.xindex, pthis.energy, pthis.text,
                 pthis.colour,'bottom', 'center']
            self.texts.append(t)
            engval = "{0:.1f}".format(pthis.energy)
            t = [pthis.xindex, pthis.energy-(abs(self.maxenergy)*0.01), engval,
                 pthis.colour, 'top','center']
            self.texts.append(t)
            if pnext:
                if pnext.connected_to != pthis.number:
                    pthis = self.plotdata[pnext.connected_to - 1]
                point = [[pthis.xindex + 0.165, pnext.xindex - 0.165],
                        [pthis.energy, pnext.energy], '--', pnext.colour, 1]
                self.vectors.append(point)
                yax = (pthis.energy + pnext.energy)/2
                engval = "({0:.1f})".format(pnext.energy - pthis.energy)
                t = [pthis.xindex+0.55, yax, engval, pnext.colour, 'center', 'left']
                self.texts.append(t)
                    


def parse_file(ifile):
    """Parse the file and get all the information needed."""
    inputfile = read_clean_file(ifile)
    plot = PlotInfo()
    plot.add_title(inputfile[0])
    plot.add_filename(inputfile[1])
    plot.add_dimensions(inputfile[2])
    plot.add_units(inputfile[3])
    plot.add_reference(inputfile[4])
    plot.parsedata(inputfile[5:])
    plot.generate_vectors()
    return plot


def prepare_plot(plot):
    """Setup and save the plot"""
    #start up plot
    fig = plt.figure(frameon=False)
    w = plot.width/plot.dpi
    h = plot.height/plot.dpi
    fig.set_size_inches(w, h)

    if plot.title:
        plt.title = plot.title
    #plt.axis([0, plot.maxxindex, plot.minenergy-(abs(plot.minenergy*0.1)),
              #plot.maxenergy + (abs(plot.maxenergy * 0.1))])
    plt.axis('off')
    
    for v in plot.vectors:
        plt.plot(v[0], v[1], v[2], color = v[3], lw = v[4])
    for t in plot.texts:
        plt.text(t[0], t[1], t[2], color = t[3], va = t[4], ha = t[5])

    #plt.show()
    plt.savefig(plot.filename, format=plot.filetype, bbox_inches='tight')


def main():
    """Run the code"""
    parser = argparse.ArgumentParser("Usage: %prog [options]")
    parser.add_argument('file',
                        help="Read plot data from input FILE")

    args = parser.parse_args()
    
    infile = args.file
    #check file exists, if not request file.
    if not check_files_exist([infile]):
        exit()
    #file is good. let's go!

    plot = parse_file(infile)
    prepare_plot(plot)
    

if __name__ == '__main__':
    main()
