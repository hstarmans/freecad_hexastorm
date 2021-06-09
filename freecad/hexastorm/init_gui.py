import os

import FreeCADGui as Gui
import FreeCAD as App

from freecad.hexastorm import ICONPATH
from freecad.hexastorm import my_numpy_function
from .commands import Sqrt


class HexastormWorkbench(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """

    MenuText = "Hexastorm workbench"
    ToolTip = "Adds optical properties to prism scanner design"
    Icon = os.path.join(ICONPATH, "template_resource.svg")
    commands = ['Sqrt']

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """

        App.Console.PrintMessage("switching to workbench_starterkit\n")
        App.Console.PrintMessage("run a numpy function: sqrt(100)"
                                 + f"= {my_numpy_function.my_foo(100)}\n")

        self.appendToolbar("Tools", self.commands)
        self.appendMenu("Tools", self.commands)
        Gui.addCommand('Sqrt', Sqrt())

    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        pass

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        pass


Gui.addWorkbench(HexastormWorkbench())
