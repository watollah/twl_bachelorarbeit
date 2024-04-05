import tkinter as tk
from tkinter import ttk

class Tool:
    def __init__(self, editor, name, id, symbol):
        self.editor = editor
        self.name = name
        self.id = id
        self.symbol = symbol

    def selected(self):
        """Code to be executed when the tool is selected"""
        print('previous selected tool: ', self.editor.selected_tool.name)
        print('now selected: ', self.name)
        self.editor.selected_tool = self
    
    def deselected(self):
        """Code to be executed when the tool is deselected"""
        pass

    def action(self, event):
        """Code to be executed when the user clicks on the canvas while the tool is active"""
        pass

class SelectTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Select', 0, '\u2d3d')

class BeamTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Beam', 1, '\ua5ec')
        self.first_node = None

    def action(self, event):
        print('EVEEEENT')

class SupportTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Support', 2, '\u29cb')

class ForceTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Force', 3, '\u2b07')

class Shape:
    def __init__(self):
        pass

class BeamShape(Shape):
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2

class NodeShape(Shape):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SupportShape(Shape):
    def __init__(self, node):
        self.node = node

class ForceShape(Shape):
    def __init__(self, node):
        self.node = node

class StaticalSystem:
    def __init__(self):
        self.nodes = []
        self.beams = []
        self.supports = []
        self.forces = []

class DiagramEditor:
    def __init__(self, master, statical_system):
        self.canvas = tk.Canvas(master)
        self.canvas.bind("<Button-1>", self.on_click)
        self.statical_system = statical_system
        
        #create toolbar
        self.tools = [SelectTool(self), BeamTool(self), SupportTool(self), ForceTool(self)]
        self.selected_tool = self.tools[0]

        toolbar = tk.Frame(self.canvas)
        toolbar.place(relx=0, rely=0, anchor=tk.NW)
        for tool in self.tools:
            rb = ttk.Radiobutton(toolbar, text=tool.symbol, variable=self.selected_tool, value=tool, command=tool.selected, style='Toolbutton')
            rb.grid(row=0, column=tool.id)
        ttk.Style().configure('Toolbutton', font=('Helvetica', 14), padding = (10, 10), width = 2) #improve sizing with grid

    #clear canvas and redraw all of the shapes
    def update(self):
        self.canvas.delete("all")
    
    #handle mouse clicks on the canvas
    def on_click(self, event):
        if isinstance(self.selected_tool, BeamTool):
            self.selected_tool.action(event)

def main():
    root = tk.Tk()
    root.title("Test")
    editor = DiagramEditor(root, None)
    editor.canvas.pack()
    root.mainloop()

if __name__ == "__main__":
    main()