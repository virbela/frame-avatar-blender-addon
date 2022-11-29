import os
import bpy
import json 
import numpy
from .properties import HomeomorphicProperties
from .helpers import get_animation_objects, require_bake_scene, get_gltf_export_indices

class Weights:

    def __init__(self, context: bpy.types.Context, ht: HomeomorphicProperties):
        self.ht = ht
        self.context = context
        self.armature = None
        self.weights = dict()
        self.transforms = dict()

        sc = require_bake_scene(context)
        for ob in sc.objects:
            if ob.type == 'ARMATURE':
                self.armature = ob

        self.bones = [b.name for b in self.armature.data.bones]
        self.animated_objects = get_animation_objects(ht)

        self.set_weights()
        self.set_transforms()
        self.save_weights_to_png()
        self.save_transforms_to_png()
        self.export_weights_json()
        self.export_transforms_json()

    def set_weights(self):
        self.weights = dict()

        for obj in self.animated_objects:
            self.weights[obj.name] = dict()
            for bone_name in self.bones:
                if bone_name not in obj.vertex_groups:
                    self.weights[obj.name][bone_name] = list()
                    continue 

                self.weights[obj.name][bone_name] = list()
                wk = self.weights[obj.name][bone_name]
                group = obj.vertex_groups[bone_name]

                for i, v in enumerate(obj.data.vertices):
                    for g in v.groups:
                        if g.group == group.index:
                            wk.append((i, g.weight))
        self.post_process_weights()

    def post_process_weights(self):
        num_verts = len(self.animated_objects[0].data.vertices)

        # set missing weights to zero
        def fill_weights(weights):
            result = []
            wd = {w[0]:w[1] for w in weights}
            for i in range(num_verts):
                if wd.get(i):
                    result.append((i, wd[i]))
                else:
                    result.append((i, 0.0))
            weights[:] = result

        # blender indices to gltf indices
        export_indices = get_gltf_export_indices(self.ht.avatar_object)
        def weights_with_indices(weights):
            if not weights:
                weights[:] = [0.0] * len(export_indices)
                return

            nw = numpy.array([k[1] for k in weights], dtype=float)
            nww = nw[export_indices]
            weights[:] = list(nww)
        
        for _, group in self.weights.items():
            for _, weights in group.items():
                if weights and len(weights) < num_verts:
                    fill_weights(weights)
                weights_with_indices(weights)

    def export_weights_json(self):
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        with open(os.path.join(directory, "weights.json"), 'w') as file:
            json.dump(self.weights, file, indent=4)

    def set_transforms(self):
        def mat_to_list(mat):
            return [mat[i][j] for i in range(4) for j in range(4)]

        for action in bpy.data.actions:
            self.transforms[action.name] = list()
            sx, sy = action.frame_range
            bakescene = require_bake_scene(self.context)
            if (sy - sx) > 1:
                # range stop is exclusive, so add one if animation has more than one frame
                sy += 1

            for i in range(int(sx), int(sy)):
                bakescene.frame_set(i)
                quats = [mat_to_list(b.matrix) for b in self.armature.pose.bones]
                self.transforms[action.name].append(sum(quats, []))

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
