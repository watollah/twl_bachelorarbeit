from tkinter import filedialog, messagebox
import json
import os

from c2d_app import TwlApp
from c2d_components import Node, Beam, Support, Force


FILE_PATH: str | None = None
EXTENSION: str = ".c2d"

def get_project_name() -> str | None:
    """Get the name of the project from the project path."""
    return os.path.splitext(os.path.basename(FILE_PATH))[0] if FILE_PATH else None

def new_project():
    """Clear all data from the Model and reset the stored project path."""
    global FILE_PATH
    if not TwlApp.model().is_empty() and not TwlApp.saved_state().get():
        ok = messagebox.askokcancel("Warning", "Creating a new project will discard current changes.", default="cancel")
        if not ok:
            return
    TwlApp.model().clear()
    FILE_PATH = None
    print("Project cleared")
    TwlApp.saved_state().set(True)

def save_project():
    """Serialize the project and save it to the stored project path. If no path is stored ask the user to provide one."""
    global FILE_PATH
    if FILE_PATH:
        with open(FILE_PATH, "w") as file:
            serialized_project = serialize_project()
            json.dump(serialized_project, file)
            print("Project saved to", FILE_PATH)
        TwlApp.saved_state().set(True)
        return
    save_project_as()

def save_project_as():
    """Serialize the project and save it to a new path."""
    global FILE_PATH
    new_file_path = filedialog.asksaveasfilename(defaultextension=EXTENSION, filetypes=[("C2D Projects", f"*{EXTENSION}")])
    if new_file_path:
        FILE_PATH = new_file_path
        save_project()

def open_project(file_path=None) -> bool:
    """Open a project from a specified path. Warning is displayed for loss of current project. If accepted current project is cleared, new path is stored
    and project from path is deserialized."""
    global FILE_PATH
    if not TwlApp.saved_state().get():
        ok = messagebox.askokcancel("Warning", "Opening a new project will discard current changes.", default="cancel")
        if not ok:
            return False
    file_path = file_path if file_path else filedialog.askopenfilename(filetypes=[("C2D Projects", f"*{EXTENSION}")])
    if file_path:
        FILE_PATH = file_path
        with open(FILE_PATH, "r") as file:
            serialized_project = json.load(file)
            TwlApp.update_manager().pause_observing()
            deserialize_project(serialized_project)
            TwlApp.update_manager().resume_observing()
        print("Project loaded from", FILE_PATH)
        TwlApp.saved_state().set(True)
        return True
    return False

def serialize_project():
    """Project is converted to a dict in preparation to be stored in a json file."""
    serialized_project = {
        "nodes": [(node.id, node.x, node.y) for node in TwlApp.model().nodes],
        "beams": [(beam.id, beam.start_node.id, beam.end_node.id) for beam in TwlApp.model().beams],
        "supports": [(support.id, support.node.id, support.angle, support.constraints) for support in TwlApp.model().supports],
        "forces": [(force.id, force.node.id, force.angle, force.strength) for force in TwlApp.model().forces]
    }
    return serialized_project

def deserialize_project(serialized_project):
    """Project is read from a string in json text format. The data in the file is converted to objects."""
    model = TwlApp.model()
    model.clear()

    for id, x, y in serialized_project["nodes"]:
        node = Node(model, x, y, id)
        model.nodes.append(node)

    for id, start_node_id, end_node_id in serialized_project["beams"]:
        start_node = model.nodes.component_for_id(start_node_id)
        end_node = model.nodes.component_for_id(end_node_id)
        assert(start_node)
        assert(end_node)
        beam = Beam(model, start_node, end_node, id)
        model.beams.append(beam)

    for id, node_id, angle, constraints in serialized_project["supports"]:
        node = model.nodes.component_for_id(node_id)
        assert(node)
        support = Support(model, node, angle, constraints, id)
        model.supports.append(support)

    for id, node_id, angle, strength in serialized_project["forces"]:
        node = model.nodes.component_for_id(node_id)
        assert(node)
        force = Force(model, node, angle, strength, id)
        model.forces.append(force)