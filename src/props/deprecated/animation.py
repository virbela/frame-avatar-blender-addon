from bpy.types import PropertyGroup
from bpy.props import BoolProperty, StringProperty


class AnimationProperty(PropertyGroup):
    name: StringProperty(
        name="", 
        default=""
    )
    
    checked: BoolProperty(
        name="", 
        default=True, 
        description="Mark for Export"
    )


class ExportAnimationJSONPathProperty(PropertyGroup):
    file: StringProperty(
        name="", 
        default="", 
        subtype="FILE_PATH", 
        description="Path to animation JSON file"
    )
    
    export: BoolProperty(
        name="Mark for export", 
        default=True, 
        description="If checked, this json file data will be included in glb export"
    )


