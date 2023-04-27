import bpy
import sys
from pathlib import Path
THISDIR = Path(__file__).parent
sys.path.insert(0, str(THISDIR.parent.absolute()))

from src import register, unregister

def main():
    register()
    
    bpy.ops.wm.open_mainfile(filepath=str(THISDIR.absolute() / "debug.blend"))
    bpy.ops.faba.export()

    unregister()

    files = list(THISDIR.glob("*.glb"))
    files += list(THISDIR.glob("*.npy"))
    files += list(THISDIR.glob("*.gltf"))
    files += list(THISDIR.glob("*.json"))
    [f.unlink() for f in files]


if __name__ == '__main__':
    main()
