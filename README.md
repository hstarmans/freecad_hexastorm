# Freecad-hexastorm

Workbench to add optics ray tracing capabilities to FreeCAD for a prism scanner.
This workbench only works with the design described [here](https://github.com/hstarmans/hexastorm_design)

## Requirements

- [FreeCAD](https://freecadweb.org/) with python3 support
- [pyOpTools](https://github.com/cihologramas/pyoptools)
- [prisms](https://github.com/hstarmans/opticaldesign)

## Linux Installation

Clone the git into the Mod dir in your FreeCAD root directory, that usually means cloning into ~/.FreeCAD/Mod
directory.
After that you just select the "Hexastorm" workbench in FreeCAD in the usual way. 


## Small Instructions

A problem I encountered while designing the laser scanner is that I could not see the laser rays.
Does the laser hit the center of the prism? Does it hit the photodiode?
This modules solves this problem by visualizing several important properties.
It relies on a specific design as it looks for certain objects within this design.
For instance, it looks for an object called prism001 and tries to determine its center and orientation.
Hereafter, it constructs an analogous model in Pyoptools.
The following commands are supported.  

### Key rays

Plots the following rays for the optical system.
- rays which form the edges of a laser scanline
- central ray through the optical system through untilted prism
- ray which hit edges photodiode

Rays can be removed by simply deleting the object created.

## TODO

- add check of correct laser height, first cylinder lens with respect to prism
- add focal point and visualize

## Related work
This is based upon  
- [pyOpTools](https://github.com/cihologramas/freecad-pyoptools/)
- [workbench_starterkit](https://github.com/FreeCAD/freecad.workbench_starterkit)
