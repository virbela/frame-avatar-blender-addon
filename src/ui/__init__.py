import bpy

from .panels import (
    FABA_PT_export,
    FABA_PT_effects,
    FABA_PT_workflow,
    FABA_PT_bake_targets
)
from .elements import (
    FABA_UL_effects,
    FABA_UL_bake_groups,
    FABA_UL_bake_variants,
    FABA_UL_bake_targets,
    FABA_UL_bake_group_members,
    FABA_UL_bake_target_mirrors
)

classes = (
    FABA_UL_effects,
    FABA_UL_bake_groups,
    FABA_UL_bake_variants,
    FABA_UL_bake_targets,
    FABA_UL_bake_group_members,
    FABA_UL_bake_target_mirrors,

    # XXX Order matters. This is the order in which the panels show up
    FABA_PT_workflow,
    FABA_PT_bake_targets,
    FABA_PT_effects,
    FABA_PT_export,
)

register_ui, unregister_ui = bpy.utils.register_classes_factory(classes)
