import bpy 


class BakeTargetReference(bpy.types.PropertyGroup):
    target:             bpy.props.IntProperty(name='Bake target identifier', default=-1)


class BakeGroup(bpy.types.PropertyGroup):
    name:               bpy.props.StringProperty(name="Group name", default='Untitled group')
    members:            bpy.props.CollectionProperty(type = BakeTargetReference)
    selected_member:    bpy.props.IntProperty(name = "Selected bake target", default = -1)
