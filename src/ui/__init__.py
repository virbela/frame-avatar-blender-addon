import bpy
from ..utils.helpers import is_dev

from .pt_workflow import (
    FABA_PT_workflow,
    FABA_PT_workflow_debug,
    # FABA_PT_workflow_baking,
    FABA_PT_workflow_helpers,
    FABA_PT_workflow_texture,
    FABA_PT_workflow_animation,
    FABA_PT_workflow_materials,
    FABA_PT_workflow_workmeshes
)

from .pt_effects import (
    FABA_PT_effects,
    FABA_UL_effects,
)

from .pt_export import (
    FABA_PT_export
)

from .pt_workmesh import (
    FABA_PT_workmesh
)

classes = (
    FABA_UL_effects,

    # XXX Order matters. This is the order in which the panels show up
    FABA_PT_workflow,
    FABA_PT_effects,
    FABA_PT_export,

    # XXX Order of worflow sub-panels
    FABA_PT_workflow_workmeshes,
    FABA_PT_workflow_texture,
    FABA_PT_workflow_materials,
    # FABA_PT_workflow_baking,
    FABA_PT_workflow_helpers,
    FABA_PT_workflow_animation,
    
    FABA_PT_workmesh,
)

if is_dev():
    classes += (FABA_PT_workflow_debug,)

register_ui, unregister_ui = bpy.utils.register_classes_factory(classes)
