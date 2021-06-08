import os
import FreeCAD as App
import FreeCADGui as Gui

from freecad.hexastorm import my_numpy_function

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
        App.Console.PrintMessage(f"run a numpy function: sqrt({arg}) = {val}\n")


class Sqrt(BaseCommand):
    NAME = "squareroot"
    FUNCTION = my_numpy_function.my_foo
    Pixmap = os.path.join(BaseCommand.ICONDIR, 'template_resource.svg')
    MenuText = 'Square root'
    ToolTip = 'Computes a square root'