import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
from pyoptools.misc.pmisc.misc import wavelength2RGB

# from freecad.hexastorm import my_numpy_function
from prisms import system


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


# class Sqrt(BaseCommand):
#     NAME = "squareroot"
#     Pixmap = os.path.join(BaseCommand.ICONDIR,
#                           'template_resource.svg')
#     MenuText = 'Square root'
#     ToolTip = 'Computes a square root'

#     def create(self):
#         val = my_numpy_function.my_foo(2)
#         App.Console.PrintMessage(f"Root of 2 equals {val}")


def get_prop_shape(ray):
    ''' translate object from pyoptools ray to FreeCAD shape '''
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


class DrawRay(BaseCommand):
    NAME = "draw ray"
    Pixmap = os.path.join(BaseCommand.ICONDIR,
                          'template_resource.svg')
    MenuText = 'Draw ray using pyOpTools'
    ToolTip = 'Draws rays'

    def __init__(self) -> None:
        #super().__init__(self)
        self.PP = system.PrismScanner()

    def update_positions(self):
        '''retrieves position optical components
           from Freecad document and pushes these
           to the settings in the optical system
           The two code bases do not share common shapes,
           which should be developed but is out of scope
        '''
        App.Console.PrintMessage("Starting to update position\n")
        # for prism, mirror and diode
        # center of mass is well defined
        pos_prism = list(App.ActiveDocument
                            .getObject('prism001')
                            .Shape.Solids[0]
                            .CenterOfMass)
        self.PP.set_orientation('prism', position=pos_prism)

        pos_mirror = list(App.ActiveDocument
                             .getObject('mirror001')
                             .Shape.Solids[0]
                             .CenterOfMass)
        self.PP.set_orientation('mirror', position=pos_mirror)

        # not implemented
        # pos_diode = (App.ActiveDocument
        #                 .getObjectsByLabel('photodiode')[0]
        #                 .Shape.CenterOfMass)

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
            PP = self.PP
            thickness = (PP.S[PP.naming[lensname]][0]
                           .thickness)
            assert boundbox.XMin < 0
            pos = [boundbox.XMin+thickness/2,
                   (boundbox.YMax-boundbox.YMin)*0.5,
                   (boundbox.ZMax-boundbox.ZMin)*0.5]
            self.PP.set_orientation(lensname,
                                    position=pos)

        boundboxCL1 = (App.ActiveDocument
                          .getObject('CLens1001')
                          .Shape
                          .BoundBox)
        posCLlens(boundboxCL1, 'CL1')

        boundboxCL2 = (App.ActiveDocument
                          .getObject('CLens2001')
                          .Shape
                          .BoundBox)
        posCLlens(boundboxCL2, 'CL2')

        App.Console.PrintMessage("Saving position")
        # self.PP.save_system('temp.pkl')

    def FUNCTION(self):
        doc = App.activeDocument()

        self.__init__(self)
        self.update_positions(self)
        self.PP.draw_five_rays()

        if doc is None:
            App.Console.PrintMessage("No active document found,"
                                     + " execution stopped")
            return

        # this is the object upon which you should define your system
        # App.ActiveDocument.getObject('prism001').Shape.Solids[0].Placement

        # creating a group simplifies removal of rays
        grp = doc.addObject("App::DocumentObjectGroup",
                            "Rays")
        llines = []

        # Create a dictionary to group rays by wavelength
        raydict = {}

        for ray in self.PP.S.prop_ray:
            #lines = Part.Wire(get_prop_shape(ray))
            llines = get_prop_shape(ray)
            wl = ray.wavelength
            raydict[wl] = llines+raydict.get(wl, [])

        for wl in raydict.keys():
            lines = Part.makeCompound(raydict[wl])
            myObj = App.ActiveDocument.addObject("Part::FeaturePython", "Ray")
            myObj.Shape = lines
            r, g, b = wavelength2RGB(wl)
            myObj.ViewObject.LineColor = (r, g, b, 0.)
            myObj.ViewObject.Proxy = 0
            grp.addObject(myObj)

        App.ActiveDocument.recompute()
