from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty, 
    FloatVectorProperty, 
    IntProperty, 
    EnumProperty, 
    CollectionProperty
)

from ..utils.helpers import EnumDescriptor


EFFECT_TYPE = EnumDescriptor(
    ("POSITION",       "Position Effect",            "Effect to transform shape positions",
        "",            0),

    ("COLOR",          "Color Effect",               "Effect to override shape color",
        "",            1),

)

class PositionEffect(PropertyGroup):
    parent_shapekey: StringProperty(
        name="Parent Shapekey",
        description="Shape key used as the relative key for this effect"
    )

    effect_shapekey: StringProperty(
        name="Effect Shapekey",
        description="Shape key with the final effect"
    )



class ColorEffect(PropertyGroup):
    shape: StringProperty(
        name="Target Shapekey"
    )

    color: FloatVectorProperty(
        name="Color", 
        subtype="COLOR",
        size = 4,
        min = 0.0,
        max = 1.0,
        default = (1.0, 1.0, 1.0, 1.0)
    )

    vert_group: StringProperty(
        name="Vertex Group"
    )


class EffectProperty(PropertyGroup):
    name: StringProperty(
        name="Effect Name", 
        default="Untitled Effect"
    )

    type: EnumProperty(
        items=tuple(EFFECT_TYPE), 
        name="Effect Type"
    )

    target: IntProperty(
        name="Effect identifier", 
        default=-1
    )

    positions: CollectionProperty(
        type=PositionEffect
    )

    colors: CollectionProperty(
        type=ColorEffect
    )

