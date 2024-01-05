import bpy

from .ops_animation import classes as animation_classes
from .ops_baking import classes as baking_classes
from .ops_dev import classes as dev_classes
from .ops_effects import classes as effects_classes
from .ops_export import classes as export_classes
from .ops_helpers import classes as helpers_classes
from .ops_intro import classes as intro_classes
from .ops_texture import classes as texture_classes
from .ops_workmaterial import classes as workmaterial_classes
from .ops_workmesh import classes as workmesh_classes


classes = (
    *animation_classes,
    *baking_classes,
    *dev_classes,
    *effects_classes,
    *export_classes,
    *helpers_classes,
    *intro_classes,
    *texture_classes,
    *workmaterial_classes,
    *workmesh_classes,
)

register_ops, unregister_ops = bpy.utils.register_classes_factory(classes)