import tkinter as tk
from tkinter import ttk
from typing import final, TypeVar
from components import *
from statical_system import *

class Tool:

    ID: int = -1
    NAME: str = "X"
    SYMBOL: str = "X"

    def __init__(self, editor: 'TwlDiagram'):
        self.editor: 'TwlDiagram' = editor
        self.name = "TEST"
   
    @final
    def selected(self):
        """Perform tool change"""
        self.editor.selected_tool.deactivate()
        self.activate()
        self.editor.selected_tool = self

    def activate(self):
        """Code to be executed when the tool is selected"""
        print('now selected: ', self.ID)
    
    def deactivate(self):
        """Code to be executed when the tool is deselected"""
        print('now deselected: ', self.NAME)

    def action(self, event):
        """Code to be executed when the user clicks on the canvas while the tool is active"""
        pass

class SelectTool(Tool):

    ID: int = 0
    NAME: str = 'Select'
    SYMBOL: str = '\u2d3d'

    def activate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.tag_bind(node.id, "<Button-1>", self.select_node)

        for beam in self.editor.statical_system.beams:
            self.editor.tag_bind(beam.id, "<Button-1>", self.select_beam)

        for support in self.editor.statical_system.supports:
            self.editor.tag_bind(support.id, "<Button-1>", self.select_support)

        for force in self.editor.statical_system.forces:
            self.editor.tag_bind(force.id, "<Button-1>", self.select_force)

    def deactivate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.tag_unbind(node.id, "<Button-1>")

        for beam in self.editor.statical_system.beams:
            self.editor.tag_unbind(beam.id, "<Button-1>")
            
        for support in self.editor.statical_system.supports:
            self.editor.tag_unbind(support.id, "<Button-1>")

        for force in self.editor.statical_system.forces:
            self.editor.tag_unbind(force.id, "<Button-1>")

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

    def select_force(self, event):
        force = StaticalSystem.find_component_at(event.x, event.y, self.editor.statical_system.forces)
        print('not found' if force == None else force.id)
    
class BeamTool(Tool):

    ID: int = 1
    NAME: str = 'Beam'
    SYMBOL: str = '\ua5ec'

    def __init__(self, editor):
        super().__init__(editor)
        self.start_node: Node | None = None

    def activate(self):
        self.editor.bind("<Button-1>", self.action)

    def deactivate(self):
        self.editor.unbind("<Button-1>")

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

    ID: int = 2
    NAME: str = 'Support'
    SYMBOL: str = '\u29cb'

    def activate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.tag_bind(node.id, "<Button-1>", self.action)
    
    def deactivate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.tag_unbind(node.id, "<Button-1>")

    def action(self, event):
        clicked_node: Node | None = StaticalSystem.find_component_at(event.x, event.y, self.editor.statical_system.nodes)
        if clicked_node:
            has_support = any(s.node == clicked_node for s in self.editor.statical_system.supports)
            if not has_support:
                self.editor.create_support(clicked_node)
                print(f"Created support on Node {clicked_node.id}")

class ForceTool(Tool):

    ID: int = 3
    NAME: str = 'Force'
    SYMBOL: str = '\u2b07'

    def activate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.tag_bind(node.id, "<Button-1>", self.action)
    
    def deactivate(self):
        for node in self.editor.statical_system.nodes:
            self.editor.tag_unbind(node.id, "<Button-1>")

    def action(self, event):
        clicked_node: Node | None = StaticalSystem.find_component_at(event.x, event.y, self.editor.statical_system.nodes)
        if clicked_node:
            has_force = any(f.node == clicked_node for f in self.editor.statical_system.forces)
            if not has_force:
                self.editor.create_force(clicked_node)
                print(f"Created force on Node {clicked_node.id}")


C = TypeVar('C', bound=Component)

class TwlTable(ttk.Treeview, TwlWidget):
    
    def __init__(self, master, component_list: ComponentList[C]):
        ttk.Treeview.__init__(self, master)
        self.component_list: ComponentList[C] = component_list

    def update(self) -> None:
        self.delete(*self.get_children())
        for component in self.component_list:
            self.insert("", tk.END, text=str(component.id), values=component.get_table_entry())

class TwlDiagram(tk.Canvas, TwlWidget):

    def __init__(self, master, statical_system):
        tk.Canvas.__init__(self, master)
        self.statical_system: StaticalSystem = statical_system
        self.selection: list[Component] = []
        
        #create toolbar
        self.tools = [SelectTool(self), BeamTool(self), SupportTool(self), ForceTool(self)]
        self.selected_tool = self.tools[0]

        toolbar = tk.Frame(self)
        toolbar.place(relx=0, rely=0, anchor=tk.NW)
        for tool in self.tools:
            rb = ttk.Radiobutton(toolbar, text=tool.SYMBOL, variable=self.selected_tool, value=tool, command=tool.selected, style='Toolbutton')
            rb.grid(row=0, column=tool.ID)
        ttk.Style().configure('Toolbutton', font=('Helvetica', 14), padding = (10, 10), width = 2) #todo: improve sizing with grid

    def change_tool(self):
        """Code to be executed when the tool is changed"""

    def update(self) -> None:
        pass

    def create_node(self, x: int, y: int) -> Node:
        node_shape_id = self.create_oval(x - Node.RADIUS, y - Node.RADIUS, x + Node.RADIUS, y + Node.RADIUS, fill='white', width = Node.BORDER, tags='node')
        node = self.statical_system.create_node(node_shape_id, x, y)
        self.tag_lower('beam', 'node')
        return node

    def create_beam(self, start_node: Node, end_node: Node) -> Beam:
        beam_shape_id = self.create_line(start_node.x, start_node.y, end_node.x, end_node.y, width=Beam.WIDTH, tags='beam')
        beam = self.statical_system.create_beam(beam_shape_id, start_node, end_node)
        self.tag_lower('beam', 'node')
        return beam
    
    def create_support(self, node: Node):
        support_shape_id = self.create_polygon(node.x, node.y, node.x - Support.WIDTH / 2, node.y + Support.HEIGHT, node.x + Support.WIDTH / 2, node.y + Support.HEIGHT, outline='black', fill='white', width=Support.BORDER, tags='support')
        support = self.statical_system.create_support(support_shape_id, node)
        self.tag_lower('support', 'node')
        return support
    
    def create_force(self, node: Node):
        arrow: Line = Force("", node).arrow() #create temporary object to get the position of the arrow
        force_shape_id = self.create_line(arrow.start.x, arrow.start.y, arrow.end.x, arrow.end.y, width=Force.WIDTH, arrow=tk.FIRST, arrowshape=Force.ARROW_SHAPE, tags='force')
        force = self.statical_system.create_force(force_shape_id, node)
        self.tag_lower('force', 'node')
        return force