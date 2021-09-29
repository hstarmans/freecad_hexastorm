import os
from os.path import dirname
from pathlib import Path
from numpy.testing import assert_array_almost_equal
from copy import deepcopy

import FreeCAD as App
import FreeCADGui as Gui
import Part
from pyoptools.misc.pmisc.misc import wavelength2RGB

import prisms


class BaseCommand(object):
    NAME = ""
    FUNCTION = None
    ICONDIR = os.path.join(os.path.dirname(__file__), "resources")

    def IsActive(self):
        if App.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        Gui.doCommandGui("import freecad.hexastorm.commands")
        Gui.doCommandGui("freecad.hexastorm.commands.{}.create()".format(
            self.__class__.__name__))
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")

    def GetResources(self):
        return {'Pixmap': self.Pixmap,
                'MenuText': self.MenuText,
                'ToolTip': self.ToolTip}

    @classmethod
    def create(cls):
        '''action which is executed'''
        cls.FUNCTION(cls)


def get_prop_shape(ray):
    '''translate object from pyoptools ray to FreeCAD shape '''
    P1 = App.Base.Vector(tuple(ray.pos))
    if len(ray.childs) > 0:
        P2 = App.Base.Vector(tuple(ray.childs[0].pos))
    else:
        P2 = App.Base.Vector(tuple(ray.pos + 10. * ray.dir))

    if ray.intensity != 0:
        L1 = [Part.makeLine(P1, P2)]
        for i in ray.childs:
            L1 = L1+get_prop_shape(i)
    else:
        L1 = []
    return L1


def alignment_test(a, b, decimal=1, msg=None):
    '''verifies to arrays are equal within range
       prints result to Freecad output

    a       -- array 1
    b       -- array 2
    decimal -- desired accuracy
    msg     -- string which clarifies what is tested
    '''
    try:
        assert_array_almost_equal(a, b, decimal=decimal)
    except AssertionError as e:
        if msg:
            msg += ' not aligned.\n'
        App.Console.PrintMessage(msg+str(e)+'\n')
        return
    msg += f' are aligned within {decimal} decimal.\n'
    App.Console.PrintMessage(msg)


class DrawRay(BaseCommand):
    NAME = "draw ray"
    Pixmap = os.path.join(BaseCommand.ICONDIR,
                          'template_resource.svg')
    MenuText = 'Draw ray using pyOpTools'
    ToolTip = 'Draws rays'

    def __init__(self) -> None:
        self.PP = prisms.system.PrismScanner()

    def update_positions(self):
        '''retrieves position optical components
           from Freecad document and pushes these
           to the settings in the optical system
           The two code bases do not share common shapes,
           which should be developed but is out of scope
        '''
        PP = self.PP

        def grabcenter(name):
            return list(App.ActiveDocument
                           .getObject(name)
                           .Shape.Solids[0]
                           .CenterOfMass)

        # laser origin
        pos_laser = grabcenter('lenstube001')
        PP.ray_prop['pos'] = pos_laser

        # for prism, mirror and diode
        # center of mass is well defined
        pos_prism = grabcenter('prism001')
        PP.set_orientation('prism', position=pos_prism)

        # CHECK center laser at center prism
        alignment_test(pos_laser[1:],
                       pos_prism[1:],
                       msg="Laser and prism")

        pos_mirror = grabcenter('mirror001')
        # in pyoptools reflective side is at 0 not center
        # of mass, so it requires correction, it assumed
        # thickness is 2
        cor = pow(2, 0.5)
        pos_mirror[2] = pos_mirror[2] + cor
        pos_mirror[1] = pos_mirror[1] + cor
        PP.set_orientation('mirror', position=pos_mirror)

        pos_diode = (App.ActiveDocument
                        .getObjectsByLabel('photodiode')[0]
                        .Shape.CenterOfMass)
        # transformation matrix needs to be applied
        pos_diode = list(App.ActiveDocument
                            .getObject('photodiode_cape')
                            .Placement
                            .Matrix*pos_diode)
        PP.set_orientation('diode', position=pos_diode)

        # cylinder lenses are compound objects
        # and do not have center of
        # mass. As a result Boundbox is used.
        # on Boundbox objects you can get XMax, XMin, etc

        # the cylindrical lenses used have their curved part pointing
        # to the laser source.
        # the flat part is well defined and should be at -thickness/2
        # from origin

        def posCLlens(boundbox, lensname):
            '''translate boundbox position
               to position in pyoptools'''
 
            thickness = (PP.S[PP.naming[lensname]][0]
                           .thickness)
            # assert boundbox.XMin < 0
            pos = list(boundbox.Center)
            pos[0] += thickness*0.5
            PP.set_orientation(lensname,
                               position=pos)
            return pos

        boundboxCL1 = (App.ActiveDocument
                          .getObject('CLens1001')
                          .Shape
                          .BoundBox)
        posCL1lens = posCLlens(boundboxCL1, 'CL1')

        # CHECK Y-position first cylinder lens
        alignment_test(posCL1lens[1],
                       pos_prism[1],
                       msg="First cylinder lens and prism")

        # CHECK Z-position first cylinder lens
        boundboxCL2 = (App.ActiveDocument
                          .getObject('CLens2001')
                          .Shape
                          .BoundBox)
        posCL2lens = posCLlens(boundboxCL2, 'CL2')
        alignment_test(posCL2lens[2],
                       pos_prism[2],
                       msg="Second cylinder lens and prism")

        # Check alignment cylinder lenses
        dist = PP.focal_point(cyllens1=True) - PP.focal_point(cyllens1=False)
        msg = 'Distance focal point CL1 minus CL2'
        alignment_test(dist,
                       0,
                       msg=msg)

        # For debugging, system can be saved and opened with pyoptools
        fname = Path(dirname(dirname(dirname(prisms.__file__))),
                     'Notebooks',
                     'temp.pkl')
        self.PP.save_system(fname)

    def FUNCTION(self):
        doc = App.activeDocument()

        # TODO: the object is never initialized
        #       that's why functions are called
        #       with self which is strange / wrong
        self.__init__(self)
        self.update_positions(self)
        self.PP.draw_key_rays()

        if doc is None:
            App.Console.PrintMessage("No active document found,"
                                     + " execution stopped")
            return

        # creating a group simplifies removal of rays
        grp = doc.addObject("App::DocumentObjectGroup",
                            "Rays")
        llines = []

        # Create a dictionary to group rays by wavelength
        raydict = {}

        for ray in self.PP.S.prop_ray:
            llines = get_prop_shape(ray)
            wl = ray.wavelength
            raydict[wl] = llines+raydict.get(wl, [])

        # draw focal point
        edge = self.PP.focal_point(cyllens1=False,
                                   simple=False)
        high_edge = deepcopy(edge)
        low_edge = deepcopy(edge)
        high_edge[1] = edge[1]-2
        low_edge[1] = edge[1]+2

        P1 = App.Base.Vector(tuple(low_edge))
        P2 = App.Base.Vector(tuple(high_edge))
        llines = [Part.makeLine(P1, P2)]
        # we draw in red
        raydict[0.800] = llines+raydict.get(wl, [])

        for idx, wl in enumerate(raydict.keys()):
            lines = Part.makeCompound(raydict[wl])
            myObj = App.ActiveDocument.addObject("Part::FeaturePython",
                                                 f"Ray{idx}")
            myObj.Shape = lines
            r, g, b = wavelength2RGB(wl)
            myObj.ViewObject.LineColor = (r, g, b, 0.)
            myObj.ViewObject.Proxy = 0
            grp.addObject(myObj)

        App.ActiveDocument.recompute()
