import bpy
import sys
from pathlib import Path
THISDIR = Path(__file__).parent
sys.path.insert(0, str(THISDIR.parent.absolute()))


def main():
    import src
    src.register()
    bpy.ops.wm.open_mainfile(filepath=str(THISDIR.absolute() / "debug.blend"))

    bpy.ops.frame.export()

    src.unregister()

    files = list(THISDIR.glob("*.glb"))
    files += list(THISDIR.glob("*.npy"))
    files += list(THISDIR.glob("*.gltf"))
    files += list(THISDIR.glob("*.json"))
    [f.unlink() for f in files]


if __name__ == '__main__':
    main()
