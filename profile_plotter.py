#!/usr/bin/env python
#Profile Plotter
#Programmer: Philip Bulsink
#Licence: BSD
#Plots reaction profiles using matplotlib by reading in energies from a file.
#See the readme.md file for more information

from profile_plotter_helpers import *

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
        self.text = text[:20].strip()

    def add_colour(self, colour):
        """
        make sure the colour is in the list and standardize the possible output
        else return black
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
            print "Number {} not valid.".format(number)
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
        self.textheight = 0.0
        self.textwidth = 0.4
        self.textlocations = list()

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
        self.add_outunits(u[1])

    def add_inunits(self, units):
        """Adds input units to the PlotInfo"""
        for u in UNIT_LIST:
            if units.lower().strip() == u:
                self.inunits = u
                break

    def add_outunits(self, units):
        """Adds output units to the PlotInfo"""
        for u in UNIT_LIST:
            if units.lower().strip() == u:
                self.outunits = u
                break

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
        #inputdata.splitlines()
        for l in inputdata:
            if l != '':
                d = l.split(',')
                if len(d) == 3:
                    d.append(d[0] - 1)
                while len(d) < 6:
                    d.append("")
                
                self.plotdata.append(PlotEntry(d[0], d[3], d[4], d[1], d[5], d[2]))

        if self.reference_line > len(self.plotdata):
            raise FormatError(self.reference_line,
                              "Can't refrerence to line {}. Only {} lines exist."
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
            p.energy = convert_units(p.energy, self.inunits, self.outunits)
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
        self.dx = 24
        self.movex = self.dx/2*(self.maxenergy-self.minenergy)/self.height
        #vectors are ([x,x], [y,y], 'colour,style')
        for i in range(len(self.plotdata)):
            pthis = self.plotdata[i]
            if i != len(self.plotdata) - 1:
                pnext = self.plotdata[i+1]
            else:
                pnext = False
            
            point = [[pthis.xindex - 0.165, pthis.xindex + 0.165],
                     [pthis.energy, pthis.energy], '-', pthis.colour, 3]
            self.vectors.append(point)
            t = [pthis.xindex, pthis.energy+self.movex, pthis.text,
                 pthis.colour,'bottom', 'center', 'white', False]
            self.texts.append(t)
            engval = "{0:.1f}".format(pthis.energy)
            t = [pthis.xindex,
                 pthis.energy-self.movex, engval,
                 pthis.colour, 'top','center', 'white', False]
            self.texts.append(t)
            if pnext:
                if pnext.connected_to != pthis.number:
                    pthis = self.plotdata[pnext.connected_to - 1]
                point = [[pthis.xindex + 0.165, pnext.xindex - 0.165],
                        [pthis.energy, pnext.energy], '--', pnext.colour, 1]
                self.vectors.append(point)
                yax = (pthis.energy + pnext.energy)/2
                engval = "({0:.1f})".format(pnext.energy - pthis.energy)
                if pnext.energy - pthis.energy > 0:
                    va = 'top'
                else:
                    va = 'bottom'
                t = [pthis.xindex+0.55, yax, engval, pnext.colour, va, 'left',
                     None, True]
                self.texts.append(t)

    def find_overlaps(self):
        """This iterates the self.texts and finds all instances of overlapping
        text. Nudges up and down to try get around overlaps."""
        more_overlaps = True
        icounter = 0
        while more_overlaps and icounter < 20:
            more_overlaps = False
            icounter += 1
            for i in range(len(self.texts)):
                for j in range(i):
                    if not j == i:
                        # rec=[x1, y1, x2, y2]
                        dx = self.texts[i][8][1][0]-self.texts[i][8][0][0]
                        dy = self.texts[i][8][1][1]-self.texts[i][8][0][1]
                        reca = [self.texts[i][0],
                                self.texts[i][1],
                                self.texts[i][0] + dx,
                                self.texts[i][1] + dy]
                        dx = self.texts[j][8][1][0]-self.texts[j][8][0][0]
                        dy = self.texts[j][8][1][1]-self.texts[j][8][0][1]
                        recb = [self.texts[j][0],
                                self.texts[j][1],
                                self.texts[j][0] + dx,
                                self.texts[j][1] + dy]
                        if test_overlap(reca, recb):
                            self.fix_overlap(i,j)
                            more_overlaps=True


    def fix_overlap(self, refa, refb):
        """Overlap fixes can be in multiple directions:
        IF one is ascending and one is decending:
            move ascending up, descending down
        IF Both same directions, same Y value
            If one is larger value than other, move larger +ve up, -ve down
            If same value:
                move refa up, refb down <-- error also
        IF otherwise:
            move higher value up, lower value down
        """
        if self.texts[refa][7] == False and self.texts[refb][7] == False:
            return
        delta = finddelta(self.texts[refa][1], self.texts[refb][1],
                          self.textheight) + 0.1

        if self.texts[refa][7] == True and self.texts[refb][7] == True:
            vala = clean_float(self.texts[refa][2])
            valb = clean_float(self.texts[refb][2])
            if vala == '' or valb == '' or vala == valb:
                # +/- based on y
                if self.texts[refa][1] > self.texts[refb][1]:
                    self.texts[refa][1] = self.texts[refa][1] + delta/2
                    self.texts[refb][1] = self.texts[refb][1] - delta/2
                else:
                    self.texts[refa][1] = self.texts[refa][1] - delta/2
                    self.texts[refb][1] = self.texts[refb][1] + delta/2
            elif vala > 0 and valb < 0:
                # +/- based on vala/b
                self.texts[refa][1] = self.texts[refa][1] + delta/2
                self.texts[refb][1] = self.texts[refb][1] - delta/2
            elif vala < 0 and valb > 0:
                # +/- based on vala/b +/-
                self.texts[refa][1] = self.texts[refa][1] - delta/2
                self.texts[refb][1] = self.texts[refb][1] + delta/2
            else:
                # +/- based on magnitude vala/b
                if vala > valb:
                    self.texts[refa][1] = self.texts[refa][1] + delta/2
                    self.texts[refb][1] = self.texts[refb][1] - delta/2
                else:
                    self.texts[refa][1] = self.texts[refa][1] - delta/2
                    self.texts[refb][1] = self.texts[refb][1] + delta/2
        elif self.texts[refb][7] == False:
            if self.texts[refa][1] > self.texts[refb][1]:
                self.texts[refa][1] = self.texts[refa][1] + delta
            else:
                self.texts[refa][1] = self.texts[refa][1] - delta
        elif self.texts[refa][7] == False:
            if self.texts[refa][1] > self.texts[refb][1]:
                self.texts[refb][1] = self.texts[refb][1] - delta
            else:
                self.texts[refb][1] = self.texts[refb][1] + delta
        return

def parse_file(ifile):
    """Parse the file and get all the information needed."""
    inputfile = read_clean_file(ifile)
    inputdir = path.dirname(ifile)
    plot = PlotInfo()
    plot.add_title(inputfile[0])
    plot.add_filename(os.path.join(inputdir, inputfile[1]))
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
    r = fig.canvas.get_renderer()
    w = plot.width/plot.dpi
    h = plot.height/plot.dpi
    fig.set_size_inches(w, h)
    plt.clf()
    ax = plt.subplot()
    ax.set_xlim(0., plot.maxxindex+1)
    ax.set_ylim(plot.minenergy, plot.maxenergy)
    
    for v in plot.vectors:
        ax.plot(v[0], v[1], v[2], color = v[3], lw = v[4])

    for t in plot.texts:
        tbox = ax.text(t[0], t[1], t[2], color = t[3], va = t[4], ha = t[5], transform=ax.transData)
        bb = tbox.get_window_extent(renderer=r)
        t.append(ax.transData.inverted().transform(bb))
        t[0] = ax.transData.inverted().transform(bb)[0][0]
        t[1] = ax.transData.inverted().transform(bb)[0][1]
        t[4] = 'bottom'
        t[5] = 'left'

    plot.find_overlaps()
    plt.clf()
    ax = plt.subplot()
    ax.set_xlim(0., plot.maxxindex+1)
    ax.set_ylim(plot.minenergy, plot.maxenergy)
    plt.axis("off")
    
    for v in plot.vectors:
        ax.plot(v[0], v[1], v[2], color = v[3], lw = v[4], zorder=1)

    for t in plot.texts:
        if t[6]:
            ax.text(t[0], t[1], t[2], color = t[3], va = t[4], ha = t[5],
                     backgroundcolor = t[6], zorder=2)
        else:
            ax.text(t[0], t[1], t[2], color = t[3], va = t[4], ha = t[5],
                    zorder=3)

    #plt.show()
    plt.savefig(plot.filename, format=plot.filetype)#, bbox_inches='tight')


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
    print "OK!"
    

if __name__ == '__main__':
    main()
