from tkinter import filedialog, messagebox, BooleanVar
import json
import os

from twl_app import *
from twl_components import *

FILENAME: str | None = None

def get_project_name() -> str | None:
    return os.path.splitext(os.path.basename(FILENAME))[0] if FILENAME else None

def clear_project(is_saved: BooleanVar):
    global FILENAME
    if not TwlApp.model().is_empty() and not is_saved.get():
        ok = messagebox.askokcancel("Warning", "Creating a new project will discard current changes.", default="cancel")
        if not ok:
            return
    TwlApp.model().clear()
    FILENAME = None
    print("Project cleared")
    is_saved.set(True)

def save_project(is_saved: BooleanVar):
    global FILENAME
    if FILENAME:
        with open(FILENAME, "w") as file:
            serialized_project = serialize_project()
            json.dump(serialized_project, file)
            print("Project saved to", FILENAME)
        is_saved.set(True)
        return
    save_project_as(is_saved)

def save_project_as(is_saved: BooleanVar):
    global FILENAME
    new_filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if new_filename:
        FILENAME = new_filename
        save_project(is_saved)

def open_project(is_saved: BooleanVar):
    global FILENAME
    if not is_saved.get():
        ok = messagebox.askokcancel("Warning", "Opening a new project will discard current changes.", default="cancel")
        if not ok:
            return
    new_filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if new_filename:
        FILENAME = new_filename
        with open(FILENAME, "r") as file:
            serialized_project = json.load(file)
            TwlApp.update_manager().pause()
            deserialize_project(serialized_project)
            TwlApp.update_manager().resume()
        print("Project loaded from", FILENAME)
        is_saved.set(True)

def serialize_project():
    serialized_project = {
        "nodes": [(node.id, node.x, node.y) for node in TwlApp.model().nodes],
        "beams": [(beam.id, beam.start_node.id, beam.end_node.id) for beam in TwlApp.model().beams],
        "supports": [(support.id, support.node.id, support.angle, support.constraints) for support in TwlApp.model().supports],
        "forces": [(force.id, force.node.id, force.angle, force.strength) for force in TwlApp.model().forces]
    }
    return serialized_project

def deserialize_project(serialized_project):
    model = TwlApp.model()
    model.clear()

    for id, x, y in serialized_project["nodes"]:
        node = Node(model, x, y)
        node.id = id
        model.nodes.append(node)

    for id, start_node_id, end_node_id in serialized_project["beams"]:
        start_node = model.nodes.get_component(start_node_id)
        end_node = model.nodes.get_component(end_node_id)
        assert(start_node)
        assert(end_node)
        beam = Beam(model, start_node, end_node)
        beam.id = id
        model.beams.append(beam)

    for id, node_id, angle, constraints in serialized_project["supports"]:
        node = model.nodes.get_component(node_id)
        assert(node)
        support = Support(model, node, angle, constraints)
        model.supports.append(support)

    for id, node_id, angle, strength in serialized_project["forces"]:
        node = model.nodes.get_component(node_id)
        assert(node)
        force = Force(model, node, angle, strength)
        model.forces.append(force)