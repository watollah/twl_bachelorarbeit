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
        self.editor.bind("<Button-1>", self.handle_selection)
        self.editor.bind("<Shift-Button-1>", self.handle_shift_selection)

    def deactivate(self):
        self.editor.unbind("<Button-1>")
        self.editor.unbind("<Shift-Button-1>")

    def selectable_components(self) -> list[Component]:
        return list(chain(self.editor.statical_system.beams, self.editor.statical_system.supports, self.editor.statical_system.forces))

    def select(self, component):
        self.editor.itemconfig(component.id, component.selected_style())
        self.editor.selection.append(component)
        print(f"selected: {component.id}")

    def deselect(self, component):
        self.editor.itemconfig(component.id, component.default_style())
        self.editor.selection.remove(component)
        print(f"deselected: {component.id}")

    def clear_selection(self):
        for component in list(self.editor.selection):
            self.deselect(component)

    def handle_selection(self, event):
        self.clear_selection()
        component = StaticalSystem.find_component_at(event.x, event.y, self.selectable_components())
        if component == None:
            print("not found")
            return
        elif component == self.editor:
            pass
        self.select(component)

    def handle_shift_selection(self, event):
        component = StaticalSystem.find_component_at(event.x, event.y, self.selectable_components())
        if component == None:
            print("not found")
            return
        elif component in self.editor.selection:
            self.deselect(component)
            return
        self.select(component)


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
        node_shape_id = self.create_oval(x - Node.RADIUS, y - Node.RADIUS, x + Node.RADIUS, y + Node.RADIUS, fill=Node.FILL_COLOR, outline=Node.BORDER_COLOR, width = Node.BORDER, tags='node')
        node = Node(node_shape_id, x, y)
        self.statical_system.nodes.append(node)
        self.tag_lower('beam', 'node')
        return node

    def create_beam(self, start_node: Node, end_node: Node) -> Beam:
        beam_shape_id = self.create_line(start_node.x, start_node.y, end_node.x, end_node.y, fill=Beam.FILL_COLOR, width=Beam.WIDTH, tags='beam')
        beam = Beam(beam_shape_id, start_node, end_node)
        self.statical_system.beams.append(beam)
        self.tag_lower('beam', 'node')
        return beam
    
    def create_support(self, node: Node):
        support_shape_id = self.create_polygon(node.x, node.y, node.x - Support.WIDTH / 2, node.y + Support.HEIGHT, node.x + Support.WIDTH / 2, node.y + Support.HEIGHT, fill=Support.FILL_COLOR, outline=Support.BORDER_COLOR, width=Support.BORDER, tags='support')
        support = Support(support_shape_id, node)
        self.statical_system.supports.append(support)
        self.tag_lower('support', 'node')
        return support
    
    def create_force(self, node: Node):
        arrow: Line = Force("", node).arrow() #create temporary object to get the position of the arrow
        force_shape_id = self.create_line(arrow.start.x, arrow.start.y, arrow.end.x, arrow.end.y, width=Force.WIDTH, arrow=tk.FIRST, arrowshape=Force.ARROW_SHAPE, fill=Force.BORDER_COLOR, tags='force')
        force = Force(force_shape_id, node)
        self.statical_system.forces.append(force)
        self.tag_lower('force', 'node')
        return force