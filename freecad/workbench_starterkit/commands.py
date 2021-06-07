import os
import FreeCAD
import FreeCADGui as Gui

from freecad.workbench_starterkit import my_numpy_function

class BaseCommand(object):
    NAME = ""
    GEAR_FUNCTION = None
    ICONDIR = os.path.join(os.path.dirname(__file__), "resources")

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        Gui.doCommandGui("import freecad.workbench_starterkit.commands")
        Gui.doCommandGui("freecad.workbench_starterkit.commands.{}(2)".format(
            self.__class__.__name__))
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")
    
    def GetResources(self):
        return {'Pixmap': self.Pixmap,
                'MenuText': self.MenuText,
                'ToolTip': self.ToolTip}

class Sqrt(BaseCommand):
    NAME = "squareroot"
    GEAR_FUNCTION = my_numpy_function
    Pixmap = os.path.join(BaseCommand.ICONDIR, 'template_resource.svg')
    MenuText = 'Square root'
    ToolTip = 'Compute a square root'