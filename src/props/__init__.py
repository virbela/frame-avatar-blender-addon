import bpy

from .baketarget import BakeTarget
from .bakevariant import BakeVariant
from .homeomorphic import HomeomorphicProperties
from .effect import ColorEffect, PositionEffect, EffectProperty
from .animation import AnimationProperty, ExportAnimationJSONPathProperty


classes = (
    BakeVariant,
    BakeTarget,

    ColorEffect,
    PositionEffect,
    EffectProperty,

    AnimationProperty,
    ExportAnimationJSONPathProperty,

    HomeomorphicProperties,
)

register, unregister = bpy.utils.register_classes_factory(classes)


def register_props():
    register()

    bpy.types.Scene.homeomorphictools = bpy.props.PointerProperty(type=HomeomorphicProperties)



def unregister_props():
    del bpy.types.Scene.homeomorphictools

    unregister()