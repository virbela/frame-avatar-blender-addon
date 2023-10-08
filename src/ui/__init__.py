import bpy
from .deprecated import (
    register_ui as deprecated_ui_register,
    unregister_ui as deprecated_ui_unregister,
)

from .pt_effects import (
    FABA_PT_effects,
    FABA_UL_effects,
)

classes = (
    FABA_UL_effects,
    # XXX Order matters. This is the order in which the panels show up
    FABA_PT_effects,
)

register, unregister = bpy.utils.register_classes_factory(classes)


def register_ui() -> None:
    deprecated_ui_register()
    register()


def unregister_ui() -> None:
    deprecated_ui_unregister()
    unregister()
