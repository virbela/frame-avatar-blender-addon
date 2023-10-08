from bpy.types import PropertyGroup
from bpy.props import IntProperty, StringProperty, CollectionProperty


class BakeTargetReference(PropertyGroup):
    target: IntProperty(name="Bake target identifier", default=-1)  # type: ignore


class BakeGroup(PropertyGroup):
    name: StringProperty(name="Group name", default="Untitled group")  # type: ignore

    members: CollectionProperty(type=BakeTargetReference)  # type: ignore

    selected_member: IntProperty(name="Selected bake target", default=-1)  # type: ignore
