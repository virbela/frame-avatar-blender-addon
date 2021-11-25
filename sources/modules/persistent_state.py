# Store hidden within bpy.props.StringProperty

try:
    import bpy
except ImportError:
    import modules.mocks.bpy_mock as bpy