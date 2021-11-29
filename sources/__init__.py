""" Blender avatar creation addon for FRAME """
try:
    import bpy
except ImportError:
    import modules.mocks.bpy_mock as bpy

from modules.create_ui import create_ui

def main():
    """ Create UI """
    create_ui()
    """ Operators """

if __name__ == "__main__":
    main()



