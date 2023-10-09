from .deprecated import (
    register_props as deprecated_props_register,
    unregister_props as deprecated_props_unregister,
    HomeomorphicProperties,
    BakeVariant,
    BakeTargetMirrorEntry,
    BakeTarget,
    PositionEffect,
    ColorEffect,
)

__all__ = [
    "HomeomorphicProperties",
    "BakeVariant",
    "BakeTargetMirrorEntry",
    "BakeTarget",
    "PositionEffect",
    "ColorEffect",
]

def register_props() -> None:
    deprecated_props_register()


def unregister_props() -> None:
    deprecated_props_unregister()
