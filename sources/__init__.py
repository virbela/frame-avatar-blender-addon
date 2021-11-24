""" Blender avatar creation addon for FRAME """
try:
    import bpy
except ImportError:
    print("This script must be run with Blender.")
from modules.create_bake_targets import create_bake_targets

""" Create UI """
# Create Bake Targets
create_bake_targets()
# Pack UVs
# Paint
# Export

""" Operators """
