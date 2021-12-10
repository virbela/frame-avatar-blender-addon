import enum
class COLORS(enum.Enum):
	BLACK = (0.0, 0.0, 0.0, 1.0)
	WHITE = (1.0, 1.0, 1.0, 1.0)

class MIRROR_TYPE(enum.Enum):
	PRIMARY = object()
	SECONDARY = object()



WORK_SCENE = 'Scene'
BAKE_SCENE = 'Baking'
BAKE_MATERIAL = 'BakeMaterial'