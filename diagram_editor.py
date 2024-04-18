import tkinter as tk
from tkinter import ttk
from typing import final
import number_entry
from statical_system import *



class Tool:
    def __init__(self, editor: 'DiagramEditor', name: str, id: int, symbol: str):
        self.editor: 'DiagramEditor' = editor
        self.name: str = name
        self.id: int = id
        self.symbol: str = symbol
   
    @final
    def selected(self):
        """Perform tool change"""
        self.editor.selected_tool.deactivate()
        self.activate()
        self.editor.selected_tool = self

    def activate(self):
        """Code to be executed when the tool is selected"""
        print('now selected: ', self.name)
    
    def deactivate(self):
        """Code to be executed when the tool is deselected"""
        print('now deselected: ', self.name)

    def action(self, event):
        """Code to be executed when the user clicks on the canvas while the tool is active"""
        pass

class SelectTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Select', 0, '\u2d3d')

    def activate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.canvas.tag_bind(node.id, "<Button-1>", self.select_node)

        for beam in self.editor.statical_system.beams:
            self.editor.canvas.tag_bind(beam.id, "<Button-1>", self.select_beam)

        for support in self.editor.statical_system.supports:
            self.editor.canvas.tag_bind(support.id, "<Button-1>", self.select_support)

    def deactivate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.canvas.tag_unbind(node.id, "<Button-1>")

        for beam in self.editor.statical_system.beams:
            self.editor.canvas.tag_unbind(beam.id, "<Button-1>")
            
        for support in self.editor.statical_system.supports:
            self.editor.canvas.tag_unbind(support.id, "<Button-1>")

    def deselect_all(self):
        for shape in self.editor.selection:
            shape.deselect()
            self.editor.selection.remove(shape)

    def select_node(self, event):
        node = StaticalSystem.find_component_at(event.x, event.y, self.editor.statical_system.nodes)
        if node != None:
            self.deselect_all()
            self.editor.selection.append(node)
            node.select()

        print('not found' if node == None else node.id)

    def select_beam(self, event):
        beam = StaticalSystem.find_component_at(event.x, event.y, self.editor.statical_system.beams)
        print('not found' if beam == None else beam.id)

    def select_support(self, event):
        support = StaticalSystem.find_component_at(event.x, event.y, self.editor.statical_system.supports)
        print('not found' if support == None else support.id)
    
class BeamTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Beam', 1, '\ua5ec')
        self.start_node: Node | None = None

    def activate(self):
        self.editor.canvas.bind("<Button-1>", self.action)

    def deactivate(self):
        self.editor.canvas.unbind("<Button-1>")

    def action(self, event):
        clicked_node: Node | None = StaticalSystem.find_component_at(event.x, event.y, self.editor.statical_system.nodes)

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

    def activate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.canvas.tag_bind(node.id, "<Button-1>", self.action)
    
    def deactivate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.canvas.tag_unbind(node.id, "<Button-1>")

    def action(self, event):
        clicked_node: Node | None = StaticalSystem.find_component_at(event.x, event.y, self.editor.statical_system.nodes)
        if clicked_node:
            has_support = any(s.node == clicked_node for s in self.editor.statical_system.supports)
            if not has_support:
                self.editor.create_support(clicked_node)
                print(f"Created support on Node {clicked_node.id}")

class ForceTool(Tool):
    def __init__(self, editor):
        super().__init__(editor, 'Force', 3, '\u2b07')

class DiagramEditor:
    def __init__(self, master, statical_system):
        self.canvas: tk.Canvas = tk.Canvas(master)
        self.statical_system: StaticalSystem = statical_system
        self.selection: list[Component] = []
        
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
    
    def create_node(self, x: int, y: int) -> Node:
        node_shape_id = self.canvas.create_oval(x - Node.RADIUS, y - Node.RADIUS, x + Node.RADIUS, y + Node.RADIUS, fill='white', width = Node.BORDER, tags='node')
        node = self.statical_system.create_node(node_shape_id, x, y)
        self.canvas.tag_lower('beam', 'node')
        return node

    def create_beam(self, start_node: Node, end_node: Node) -> Beam:
        beam_shape_id = self.canvas.create_line(start_node.x, start_node.y, end_node.x, end_node.y, width=Beam.WIDTH, tags='beam')
        beam = self.statical_system.create_beam(beam_shape_id, start_node, end_node)
        self.canvas.tag_lower('beam', 'node')
        return beam
    
    def create_support(self, node: Node):
        support_shape_id = self.canvas.create_polygon(node.x, node.y, node.x - Support.WIDTH / 2, node.y + Support.HEIGHT, node.x + Support.WIDTH / 2, node.y + Support.HEIGHT, outline='black', fill='white', width=Support.BORDER, tags='support')
        support = self.statical_system.create_support(support_shape_id, node)
        self.canvas.tag_lower('support', 'node')
        return support

def main():
    root = tk.Tk()
    root.title("Test")
    editor = DiagramEditor(root, StaticalSystem())
    editor.canvas.pack()
    root.mainloop()

if __name__ == "__main__":
    main()