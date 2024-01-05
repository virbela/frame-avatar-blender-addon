from bpy.types import Context, Operator

from .base import FabaOperator
from ..utils.helpers import require_bake_scene
from ..props import HomeomorphicProperties


def setup_bake_scene(operator: Operator, context: Context, ht: HomeomorphicProperties):
    require_bake_scene()


class FABA_OT_setup_bake_scene(FabaOperator):
    bl_label =            "Create Bake Scene"
    bl_idname =           "faba.setup_bake_scene"
    bl_description =      "Create bake scene"
    faba_operator =       setup_bake_scene

classes = (
    FABA_OT_setup_bake_scene,
)