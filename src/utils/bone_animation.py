import os
import bpy
import json 
import copy
import math
import numpy
from pathlib import Path
from mathutils import Matrix
from bpy.types import Context, PoseBone
from bpy_extras.io_utils import axis_conversion

from .logging import log
from ..props import HomeomorphicProperties
from .helpers import get_action_frame_range, get_animation_objects, require_bake_scene, get_gltf_export_indices

class BoneAnimationExporter:
    weights = dict()
    transforms = dict()
    head_transforms = dict()

    def __init__(self, context: Context, ht: HomeomorphicProperties):
        log.info("Bone animation export started ...")
        self.ht = ht
        self.context = context
        self.armature = None

        sc = require_bake_scene()
        for ob in sc.objects:
            if ob.type == "ARMATURE":
                self.armature = ob
        
        if not self.armature:
            self.armature = self.ht.avatar_rig

        self.head_bone_name = ht.avatar_head_bone
        self.bones = [b.name for b in self.armature.data.bones if b.use_deform]
        self.animated_objects = get_animation_objects(ht)

        self.set_weights()
        self.set_transforms()
        self.save_animation_json()

    @classmethod
    def load_from_json(cls, context: Context, ht: HomeomorphicProperties):
        transforms = dict()
        head_transforms = dict()
        weights_compare = list()

        for path in ht.export_animation_json_paths:
            jsonfile = bpy.path.abspath(path.file)
            with open(Path(jsonfile), "r") as file:
                data = json.loads(file.read())
                if "weights" in data.keys():
                    weights_compare.append(data["weights"])

                if "transforms" in data.keys():
                    for animName, trans in data["transforms"].items():
                        transforms[animName] = trans

                if "head_transforms" in data.keys():
                    for animName, trans in data["head_transforms"].items():
                        head_transforms[animName] = trans


        # TODO(ranjian0)
        # compare the weights and make sure they are all the same for the animations

        cls.weights = copy.deepcopy(weights_compare[0])
        cls.transforms = copy.deepcopy(transforms)
        cls.head_transforms = copy.deepcopy(head_transforms)


    def set_weights(self):
        log.info("\tCalculating vertex weights...")
        max_weights_per_vert = 10
        export_indices = get_gltf_export_indices(self.ht.avatar_mesh)

        def el(val, count):
            # create empty list filled with `val` `count`` times
            return [val] * count

        for obj in self.animated_objects:
            self.ht.export_progress_step(1.0)
            self.weights[obj.name] = dict()

            tmp_map = dict()
            for v in obj.data.vertices:
                # XXX Important to only use the groups for deformation bones, any other vertex groups
                #     should be ignored (preserves user created groups too)
                vgroups = [g for g in v.groups if obj.vertex_groups[g.group].name in self.bones]

                weights_per_vert = min(max_weights_per_vert, len(vgroups))

                groups = sorted(vgroups, key=lambda x: -x.weight)[:weights_per_vert]
                total_weight = sum((x.weight for x in groups), 0.0) or 1.0
                bones = ([x.group for x in groups] + el(0, weights_per_vert))[:weights_per_vert]
                weights = ([x.weight / total_weight for x in groups] + el(0.0, weights_per_vert))[:weights_per_vert]
                
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
        with open(os.path.join(directory, "weights.json"), "w") as file:
            json.dump(self.weights, file, indent=4)

    def set_transforms(self):
        log.info("\tGetting bone transforms...")
        bakescene = require_bake_scene()
        # blender z-up to babylon y-up
        R1 = Matrix.Rotation(math.radians(180), 4, "Y")
        R2 = Matrix.Rotation(math.radians(-90), 4, "X")

        # Our rig has -Y as forward, R1 switches it to +Y
        axis_basis_change = axis_conversion(
            from_forward="Y", from_up="Z",
            to_forward="Z", to_up="Y"
        ).to_4x4() @ R1

        def calc_bone_matrix(pose_bone: PoseBone) -> Matrix:
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
            return mat

        def get_bone_mat(pose_bone: PoseBone) -> list:
            mat = calc_bone_matrix(pose_bone)
            # XXX Export Matrix in column major format
            return [round(mat[j][i], 4) for i in range(4) for j in range(4)]
        
        def get_head_transform(head_bone: PoseBone) -> tuple:
            # mat = calc_bone_matrix(head_bone)
            mat = head_bone.matrix @ axis_basis_change
            loc, _, _ = mat.decompose()
            return list(loc.to_tuple(4))

        last_frame = bakescene.frame_current
        last_action = self.armature.animation_data.action
        for action in bpy.data.actions:
            if not action.use_fake_user:
                continue

            self.ht.export_progress_step(1.0)
            if action.name not in [ea.name for ea in self.ht.export_animation_actions]:
                # Possibly not a valid export action eg tpose
                continue

            action_enabled = {e.name: e.checked for e in self.ht.export_animation_actions}.get(action.name, False)
            if not action_enabled:
                # Current action is not marked for export
                continue

            self.armature.animation_data.action = action
            self.transforms[action.name] = list()
            self.head_transforms[action.name] = list()
            for i in range(*get_action_frame_range(action)):
                bakescene.frame_set(i)
                self.context.view_layer.update()
                mats = [get_bone_mat(self.armature.pose.bones[bname]) for bname in self.bones]
                self.transforms[action.name].append(sum(mats, []))
                head_bone_locs = [get_head_transform(self.armature.pose.bones[bname]) for bname in self.bones if bname == self.head_bone_name]
                self.head_transforms[action.name].append(sum(head_bone_locs, []))

        # -- restore last action and frame
        self.armature.animation_data.action = last_action
        bakescene.frame_set(last_frame)
        self.context.view_layer.update()

    def export_transforms_json(self):
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        with open(os.path.join(directory, "bone_transforms.json"), "w") as file:
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

        oldimg = bpy.data.images.get("weights_texture")
        if oldimg:
            bpy.data.images.remove(oldimg)
        
        img = bpy.data.images.new(name="weights_texture", width=width // 3, height=height, alpha=False)
        img.alpha_mode = "NONE"
        img.file_format = "PNG"
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
            img.file_format = "PNG"
            img.pixels = buff.ravel()
            img.update()
            img.filepath = os.path.join(directory, f"{tname}.png")
            img.save()

    def save_animation_json(self):
        filepath = bpy.data.filepath
        filename = Path(filepath).stem
        directory = os.path.dirname(filepath)
        data = {
            "weights": self.weights,
            "transforms": self.transforms,
            "head_transforms": self.head_transforms
        }
        with open(os.path.join(directory, f"{filename}.json"), "w") as file:
            json.dump(data, file)
