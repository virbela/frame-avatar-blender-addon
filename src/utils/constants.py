import enum
from pathlib import Path

ASSET_DIR = Path(__file__).parent.parent.joinpath("assets").absolute()

class COLORS(enum.Enum):
    BLACK = (0.0, 0.0, 0.0, 1.0)
    WHITE = (1.0, 1.0, 1.0, 1.0)

IGNORED = type("IGNORED", (), {})

WORK_SCENE = "Scene"
BAKE_SCENE = "Baking"
PARTITIONING_OBJECT = "_uv_partitioning_object_"
BAKE_MATERIAL = "BakeMaterial"

TARGET_UV_MAP = "TargetMap"
PAINTING_UV_MAP = "PaintingMap"

GLB_VERT_COUNT = 441


class Assets:
    class AvatarBase:
        url = ASSET_DIR / "avatarbase.blend"
        name = "Avatar"

    class Materials:
        url = ASSET_DIR / "materials.blend"
        class BakeAO:
            name = "bake_material_ao"

        class BakeDiffuse:
            name = "bake_material_diffuse"

        class BakePreview:
            name = "bake_material_preview"

