import bpy
from ..utils.helpers import is_dev 

from .panels import (
    FRAME_PT_export,
    FRAME_PT_effects,
    FRAME_PT_workflow,
    FRAME_PT_node_dev_tools,
    FRAME_PT_bake_targets
)
from .elements import (
    FRAME_UL_effects,
    FRAME_UL_bake_groups,
    FRAME_UL_bake_variants,
    FRAME_UL_bake_targets,
    FRAME_UL_bake_group_members,
    FRAME_UL_bake_target_mirrors
)

classes = (
    FRAME_UL_effects,
    FRAME_UL_bake_groups,
    FRAME_UL_bake_variants,
    FRAME_UL_bake_targets,
    FRAME_UL_bake_group_members,
    FRAME_UL_bake_target_mirrors,

    # XXX Order matters. This is the order in which the panels show up
    FRAME_PT_workflow,
    FRAME_PT_bake_targets,
    FRAME_PT_effects,
    FRAME_PT_export,
)

if is_dev():
    classes += (FRAME_PT_node_dev_tools,)

register_ui, unregister_ui = bpy.utils.register_classes_factory(classes)
