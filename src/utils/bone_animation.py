import os
import bpy
import json 
import math
import numpy
from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion

from .properties import HomeomorphicProperties
from .helpers import get_animation_objects, require_bake_scene, get_gltf_export_indices

class BoneAnimationExporter:
    weights = dict()
    transforms = dict()

    def __init__(self, context: bpy.types.Context, ht: HomeomorphicProperties):
        self.ht = ht
        self.context = context
        self.armature = None

        sc = require_bake_scene(context)
        for ob in sc.objects:
            if ob.type == 'ARMATURE':
                self.armature = ob

        self.bones = [b.name for b in self.armature.data.bones]
        self.animated_objects = get_animation_objects(ht)

        self.set_weights()
        self.set_transforms()

    def set_weights(self):
        export_indices = get_gltf_export_indices(self.ht.avatar_object)

        for obj in self.animated_objects:
            self.weights[obj.name] = dict()

            tmp_map = dict()
            for v in obj.data.vertices:
                groups = sorted(v.groups, key=lambda x: -x.weight)[:4]
                total_weight = sum((x.weight for x in groups), 0.0) or 1.0
                bones = ([x.group for x in groups] + [0, 0, 0, 0])[:4]
                weights = ([x.weight / total_weight for x in groups] + [0.0, 0.0, 0.0, 0.0])[:4]
                
                all_weights = [0.0] * len(self.bones)
                for idx, bname in enumerate(self.bones):
                    if bname not in obj.vertex_groups:
                        continue
                    
                    vg = obj.vertex_groups[bname]
                    if vg.index in bones:
                        all_weights[idx] = weights[bones.index(vg.index)]

                tmp_map[v.index] = all_weights

            # convert verts to export indices
            for i, index in enumerate(export_indices):
                self.weights[obj.name][str(i)] = tmp_map[index]

    def export_weights_json(self):
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        with open(os.path.join(directory, "weights.json"), 'w') as file:
            json.dump(self.weights, file, indent=4)

    def set_transforms(self):
        bakescene = require_bake_scene(self.context)
        # blender z-up to babylon y-up
        R1 = Matrix.Rotation(math.radians(180), 4, 'Y')
        R2 = Matrix.Rotation(math.radians(-90), 4, 'X')

        # Our rig has -Y as forward, R1 switches it to +Y
        axis_basis_change = axis_conversion(
            from_forward='Y', from_up='Z',
            to_forward='Z', to_up='Y'
        ).to_4x4() @ R1

        def get_bone_mat(pose_bone: bpy.types.PoseBone):
            inverse_bind_pose = (
                self.armature.matrix_world @ 
                pose_bone.bone.matrix_local
            ).inverted_safe()

            bone_matrix = (
                self.armature.matrix_world @
                pose_bone.matrix
            )

            # Read right to left
            # 1. convert axis basis, 
            # 2. inverse rest pose (go to origin), 
            # 3. move to actual bone transform
            # 4. R2 ?? TODO(ranjian0) Investigate
            mat = R2 @ bone_matrix @ inverse_bind_pose @ axis_basis_change

            # XXX Export Matrix in column major format
            return [round(mat[j][i], 4) for i in range(4) for j in range(4)]

        for action in bpy.data.actions:
            # if action.name == 'tpose':
            #     continue

            self.armature.animation_data.action = action
            self.transforms[action.name] = list()
            sx, sy = action.frame_range
            if (sy - sx) > 1:
                # range stop is exclusive, so add one if animation has more than one frame
                sy += 1

            for i in range(int(sx), int(sy)):
                bakescene.frame_set(i)
                self.context.view_layer.update()
                mats = [get_bone_mat(self.armature.pose.bones[bname]) for bname in self.bones]
                self.transforms[action.name].append(sum(mats, []))

    def export_transforms_json(self):
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        with open(os.path.join(directory, "bone_transforms.json"), 'w') as file:
            json.dump(self.transforms, file, indent=4)

    def save_weights_to_png(self):
        num_bones = len(self.weights[self.animated_objects[0].name].keys())
        num_objects = len(self.animated_objects)
        num_weights = len(self.weights[self.animated_objects[0].name][self.bones[0]])

        width = num_weights
        height = num_bones * num_objects
        buff = numpy.zeros((width, height), dtype=numpy.float32)
        for oi, ob in enumerate(self.weights.keys()):
            for bi, bo in enumerate(self.weights[self.animated_objects[0].name].keys()):
                idx = oi * num_bones + bi
                try: 
                    buff[:,idx] = self.weights[ob][bo]
                except KeyError as e:
                    print(ob, bo)
                    raise e

        oldimg = bpy.data.images.get('weights_texture')
        if oldimg:
            bpy.data.images.remove(oldimg)
        
        img = bpy.data.images.new(name='weights_texture', width=width // 3, height=height, alpha=False)
        img.alpha_mode = 'NONE'
        img.file_format = 'PNG'
        img.pixels = buff.ravel()
        img.update()
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        img.filepath = os.path.join(directory, f"bone_weights.png")
        img.save()

    def save_transforms_to_png(self):
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)

        for action in bpy.data.actions:
            data = self.transforms[action.name]
            height = len(data)
            width = len(data[0])

            buff = numpy.zeros(width * height, dtype=numpy.float32)
            buff[:] = sum(data, [])

            tname = f"{action.name}_bone_mats"
            oldimg = bpy.data.images.get(tname)
            if oldimg:
                bpy.data.images.remove(oldimg)
            
            img = bpy.data.images.new(name=tname, width=width // 4, height=height, alpha=False)
            img.file_format = 'PNG'
            img.pixels = buff.ravel()
            img.update()
            img.filepath = os.path.join(directory, f"{tname}.png")
            img.save()