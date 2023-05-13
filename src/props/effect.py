import bpy
from ..utils.helpers import enum_descriptor


EFFECT_TYPE = enum_descriptor(
    ('POSITION',       'Position Effect',            'Effect to transform shape positions',
        '',            0),

    ('COLOR',          'Color Effect',               'Effect to override shape color',
        '',            1),

)

class PositionEffect(bpy.types.PropertyGroup):
    parent_shapekey:    bpy.props.StringProperty(
                            name="Parent Shapekey",
                            description="Shape key used as the relative key for this effect"
                        )
    effect_shapekey:    bpy.props.StringProperty(
                            name="Effect Shapekey",
                            description="Shape key with the final effect"
                        )


class ColorEffect(bpy.types.PropertyGroup):
    shape:  bpy.props.StringProperty(name="Target Shapekey")
    color:  bpy.props.FloatVectorProperty(name="Color", subtype='COLOR',
                size = 4,
                min = 0.0,
                max = 1.0,
                default = (1.0, 1.0, 1.0, 1.0)
            )
    vert_group: bpy.props.StringProperty(name="Vertex Group")


class EffectProperty(bpy.types.PropertyGroup):
    name:   bpy.props.StringProperty(name="Effect Name", default='Untitled Effect')
    type:   bpy.props.EnumProperty(items=tuple(EFFECT_TYPE), name="Effect Type")
    target: bpy.props.IntProperty(name='Effect identifier', default=-1)

    positions:  bpy.props.CollectionProperty(type = PositionEffect)
    colors:     bpy.props.CollectionProperty(type = ColorEffect)

