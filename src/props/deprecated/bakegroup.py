from bpy.types import PropertyGroup
from bpy.props import IntProperty, StringProperty, CollectionProperty


class BakeTargetReference(PropertyGroup):
    target: IntProperty(name="Bake target identifier", default=-1)


class BakeGroup(PropertyGroup):
    name: StringProperty(name="Group name", default="Untitled group")

    members: CollectionProperty(type=BakeTargetReference)

    selected_member: IntProperty(name="Selected bake target", default=-1)
