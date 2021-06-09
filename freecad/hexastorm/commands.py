import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
from pyoptools.misc.pmisc.misc import wavelength2RGB

from freecad.hexastorm import my_numpy_function
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
        Gui.doCommandGui("freecad.hexastorm.commands.{}.create(2)".format(
            self.__class__.__name__))
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")

    def GetResources(self):
        return {'Pixmap': self.Pixmap,
                'MenuText': self.MenuText,
                'ToolTip': self.ToolTip}

    @classmethod
    def create(cls, arg):
        val = cls.FUNCTION(arg)
        App.Console.PrintMessage("run a numpy function:" +
                                 f"sqrt({arg}) = {val}\n")


class Sqrt(BaseCommand):
    NAME = "squareroot"
    FUNCTION = my_numpy_function.my_foo
    Pixmap = os.path.join(BaseCommand.ICONDIR,
                          'template_resource.svg')
    MenuText = 'Square root'
    ToolTip = 'Computes a square root'


def get_prop_shape(ray):
    ''' translate object from pyoptools ray to FreeCAD shape '''
    P1 = App.Base.Vector(tuple(ray.pos))
    if len(ray.childs) > 0:
        P2 = App.Base.Vector(tuple(ray.childs[0].pos))
    else:
        P2 = App.Base.Vector(tuple(ray.pos + 10. * ray.dir))

    if ray.intensity != 0:
        L1 = [App.makeLine(P1, P2)]
        for i in ray.childs:
            L1 = L1+get_prop_shape(i)
    else:
        L1 = []
    return L1


class DrawRay(BaseCommand):
    doc = App.activeDocument()

    # this is the object upon which you should define your system
    PP = system.PrismScanner()
    # App.ActiveDocument.getObject('prism001').Shape.Solids[0].Placement


    # creating a group simplifies removal of rays
    grp = doc.addObject("App::DocumentObjectGroup", "Rays")
    llines = []

    # Create a dictionary to group rays by wavelength 
    raydict = {}

    for ray in PP.S.prop_ray:
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
