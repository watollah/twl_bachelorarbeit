import tkinter as tk
from tkinter import ttk
import typing
from typing import TypeVar
from typing import final

class Shape:
    def __init__(self):
        pass

    def is_at(self, x: int, y: int) -> bool:
        return False

class NodeShape(Shape):

    RADIUS: int = 5

    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def is_at(self, x: int, y: int) -> bool:
        return True if abs(self.x - x) <= self.RADIUS and abs(self.y - y) <= self.RADIUS else False

class BeamShape(Shape):
    def __init__(self, start_node: NodeShape, end_node: NodeShape):
        self.start_node: NodeShape = start_node
        self.end_node:NodeShape = end_node

class SupportShape(Shape):
    def __init__(self, node: NodeShape):
        self.node: NodeShape = node

class ForceShape(Shape):
    def __init__(self, node: NodeShape):
        self.node: NodeShape = node

class StaticalSystem:
    def __init__(self):
        self.nodes: list[NodeShape] = []
        self.beams: list[BeamShape] = []
        self.supports: list[SupportShape] = []
        self.forces: list[ForceShape] = []

    def create_node(self, x: int, y: int) -> NodeShape:
        node = NodeShape(x, y)
        self.nodes.append(node)
        return node

    def create_beam(self, start_node: NodeShape, end_node: NodeShape) -> BeamShape:
        beam = BeamShape(start_node, end_node)
        self.beams.append(beam)
        return beam

class Tool:
    def __init__(self, editor: 'DiagramEditor', name: str, id: int, symbol: str):
        self.editor: 'DiagramEditor' = editor
        self.name: str = name
        self.id: int = id
        self.symbol: str = symbol
   
    @final
    def selected(self):
        """Perform tool change"""
        self.editor.selected_tool.run_when_deselected()
        self.run_when_selected()
        self.editor.selected_tool = self

    def run_when_selected(self):
        """Code to be executed when the tool is selected"""
        print('now selected: ', self.name)
    
    def run_when_deselected(self):
        """Code to be executed when the tool is deselected"""
        print('now deselected: ', self.name)

    def action(self, event):
        """Code to be executed when the user clicks on the canvas while the tool is active"""
        pass

class SelectTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Select', 0, '\u2d3d')

class BeamTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Beam', 1, '\ua5ec')
        self.start_node: NodeShape | None = None

    def action(self, event):
        clicked_node: NodeShape | None = self.editor.find_shape_at(event.x, event.y, self.editor.statical_system.nodes)

        if clicked_node:
            if self.start_node is None:
                self.start_node = clicked_node
            else:
                self.editor.create_beam(self.start_node, clicked_node)
                self.start_node = None
        else:
            if self.start_node is None:
                self.start_node = self.editor.create_node(event.x, event.y)
            else:
                end_node = self.editor.create_node(event.x, event.y)
                self.editor.create_beam(self.start_node, end_node)
                self.start_node = None

class SupportTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Support', 2, '\u29cb')

class ForceTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Force', 3, '\u2b07')

class DiagramEditor:
    def __init__(self, master, statical_system):
        self.canvas: tk.Canvas = tk.Canvas(master)
        self.canvas.bind("<Button-1>", self.on_click)
        self.statical_system: StaticalSystem = statical_system
        
        #create toolbar
        self.tools = [SelectTool(self), BeamTool(self), SupportTool(self), ForceTool(self)]
        self.selected_tool = self.tools[0]
        self.canvas.find

        toolbar = tk.Frame(self.canvas)
        toolbar.place(relx=0, rely=0, anchor=tk.NW)
        for tool in self.tools:
            rb = ttk.Radiobutton(toolbar, text=tool.symbol, variable=self.selected_tool, value=tool, command=tool.selected, style='Toolbutton')
            rb.grid(row=0, column=tool.id)
        ttk.Style().configure('Toolbutton', font=('Helvetica', 14), padding = (10, 10), width = 2) #todo: improve sizing with grid

    def change_tool(self):
        """Code to be executed when the tool is changed"""
    
    def update(self):
        """Clear canvas and redraw all of the shapes"""
        self.canvas.delete("all")
        for beam in self.statical_system.beams:
            self.canvas.create_line(beam.start_node.x, beam.start_node.y, beam.end_node.x, beam.end_node.y)
        
        for node in self.statical_system.nodes:
            self.canvas.create_oval(node.x - 5, node.y - 5, node.x + 5, node.y + 5, fill="black", tags="node")

    def on_click(self, event):
        """Handle mouse clicks on the canvas"""
        if isinstance(self.selected_tool, BeamTool):
            self.selected_tool.action(event)

    def create_node(self, x: int, y: int) -> NodeShape:
        node = self.statical_system.create_node(x, y)
        self.update()
        return node

    def create_beam(self, start_node: NodeShape, end_node: NodeShape) -> BeamShape:
        beam = self.statical_system.create_beam(start_node, end_node)
        self.update()
        return beam
    
    S = TypeVar('S', bound=Shape)
    @staticmethod
    def find_shape_at(x: int, y: int, shapes: list[S]) -> S | None:
        """Checks if one of the shapes in the list is at the specified Coordinate"""
        return next(filter(lambda s: s.is_at(x, y), shapes), None)

def main():
    root = tk.Tk()
    root.title("Test")
    editor = DiagramEditor(root, StaticalSystem())
    editor.canvas.pack()
    root.mainloop()

if __name__ == "__main__":
    main()