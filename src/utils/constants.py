import enum
class COLORS(enum.Enum):
	BLACK = (0.0, 0.0, 0.0, 1.0)
	WHITE = (1.0, 1.0, 1.0, 1.0)

class MIRROR_TYPE(enum.Enum):
	PRIMARY = object()
	SECONDARY = object()

IGNORED = type('IGNORED', (), {})

WORK_SCENE = 'Scene'
BAKE_SCENE = 'Baking'
PARTITIONING_OBJECT = '_uv_partitioning_object_'
BAKE_MATERIAL = 'BakeMaterial'

TARGET_UV_MAP = 'TargetMap'
PAINTING_UV_MAP = 'PaintingMap'
