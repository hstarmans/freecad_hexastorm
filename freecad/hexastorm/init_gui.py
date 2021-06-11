import os

import FreeCADGui as Gui
import FreeCAD as App

from freecad.hexastorm import ICONPATH
from .commands import DrawRay


class HexastormWorkbench(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """

    MenuText = "Hexastorm workbench"
    ToolTip = "Adds optical properties to prism scanner design"
    Icon = os.path.join(ICONPATH, "template_resource.svg")
    commands = ['DrawRay']

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """

        App.Console.PrintMessage("switching to workbench_starterkit\n")
        self.appendToolbar("Tools", self.commands)
        self.appendMenu("Tools", self.commands)
        Gui.addCommand('DrawRay', DrawRay())

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
