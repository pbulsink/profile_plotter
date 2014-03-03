Readme.md

This script requires an input file with the energies of each step.

ACS recommends 1200 dpi for images in b/w used for TOC images.

Typically, input will be in hartrees (from gaussian, turbomole, etc) and
output should be in kj/mol.

Only 24 characters will be printed on a line at each energy point.

Attaching an image isn't yet possible.


This file is of the following format:

Title
Plot Filename.format (png default)
width, height[, dpi] (in pixels) (default dip is 1200)
input energy units, output energy units ('hartrees','kj/mol', 'kcal/mol', 'ev', 'cm-1')
0 reference line (or put 0 for absolute values)

Line, energy, "value text", [Connected_to, colour, "image"]
1, -10000, "1", , b, "plt1.png" 
2, -9000, "TS 2", 1,
3
4
5
6

