import modules.state as state

try:
    import bpy
except ImportError:
    import modules.mocks.bpy_mock as bpy

from modules.create_bake_targets import create_bake_targets
from modules.pack_uvs import pack_uvs
from modules.paint import paint
from modules.export import export

"""
THESE GET CALLED BY BUTTON CLICK HANDLERS
# Create Bake Targets
create_bake_targets()
# Pack UVs
pack_uvs()
# Paint
paint()
# Export
export()
"""

# JUST FOR TESTING
create_bake_targets()

def create_buttons(ui: dict) -> None:
    """ Create buttons """
    # Create buttons
    # ui.create_bake_targets_button = ui.layout.operator("frame_avatar_blender_addon.create_bake_targets", text="Create Bake Targets")
    # ui.pack_uvs_button = ui.layout.operator("frame_avatar_blender_addon.pack_uvs", text="Pack UVs")
    # ui.paint_button = ui.layout.operator("frame_avatar_blender_addon.paint", text="Paint")
    # ui.export_button = ui.layout.operator("frame_avatar_blender_addon.export", text="Export")

def create_ui() -> None:
    """ Create UI """
    ui = {}
    # Create UI
    create_buttons(ui)
    state.set_ui(ui)
    