import modules.state as state

try:
    import bpy
except ImportError:
    import modules.mocks.bpy_mock as bpy

def paint() -> None:
    pass
