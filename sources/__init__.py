""" Blender avatar creation addon for FRAME """
try:
    import bpy
except ImportError:
    pass
from modules.create_bake_targets import CreateBakeTargets

""" Create UI """
# Create Bake Targets
CreateBakeTargets()
# Pack UVs
# Paint
# Export

""" Operators """
