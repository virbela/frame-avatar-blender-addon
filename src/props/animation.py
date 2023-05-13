import bpy 


class AnimationProperty(bpy.types.PropertyGroup):
    name:                   bpy.props.StringProperty(name="", default="")
    checked:                bpy.props.BoolProperty(name="", default=True, description="Mark for Export")


class ExportAnimationJSONPathProperty(bpy.types.PropertyGroup):
    file:                  bpy.props.StringProperty(name="", default="", 
                                                    subtype='FILE_PATH', 
                                                    description="Path to animation JSON file")
    export:                bpy.props.BoolProperty(name="Mark for export", default=True, 
                                                  description="If checked, this json file data will be included in glb export")


