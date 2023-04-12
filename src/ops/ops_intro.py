from bpy.types import Context, Operator

from ..utils.helpers import require_bake_scene
from ..utils.properties import HomeomorphicProperties


def setup_bake_scene(operator: Operator, context: Context, ht: HomeomorphicProperties):
    require_bake_scene(context)
