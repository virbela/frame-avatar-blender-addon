from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    FloatVectorProperty,
    IntProperty,
    EnumProperty,
    CollectionProperty,
)

from ..utils.helpers import EnumDescriptor


EFFECT_TYPE = EnumDescriptor(
    ("POSITION", "Position Effect", "Effect to transform shape positions", "", 0),
    ("COLOR", "Color Effect", "Effect to override shape color", "", 1),
)


class PositionEffect(PropertyGroup):
    parent_shapekey: StringProperty(  # type: ignore
        name="Parent Shapekey",
        description="Shape key used as the relative key for this effect",
    )

    effect_shapekey: StringProperty(  # type: ignore
        name="Effect Shapekey", description="Shape key with the final effect"
    )


class ColorEffect(PropertyGroup):
    shape: StringProperty(name="Target Shapekey")  # type: ignore

    color: FloatVectorProperty(  # type: ignore
        name="Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )

    vert_group: StringProperty(name="Vertex Group")  # type: ignore


class EffectProperty(PropertyGroup):
    name: StringProperty(name="Effect Name", default="Untitled Effect")  # type: ignore

    type: EnumProperty(items=tuple(EFFECT_TYPE), name="Effect Type")  # type: ignore

    target: IntProperty(name="Effect identifier", default=-1)  # type: ignore

    positions: CollectionProperty(type=PositionEffect)  # type: ignore

    colors: CollectionProperty(type=ColorEffect)  # type: ignore
