import bmesh
from bpy.types import Object
from mathutils import Vector
from dataclasses import dataclass

from .logging import log
from .constants import TARGET_UV_MAP


@dataclass
class UVTransform:
    centroid: Vector
    translation: Vector
    scale: float
    rotation: float

    def isNil(self) -> None:
        return (
            self.scale == 1.0
            and self.rotation == 0
            and self.translation == Vector((0, 0))
        )


def get_uv_map_from_mesh(obj: Object) -> dict[int, Vector]:
    "If uv_layer is ACTIVE_LAYER, the active UV layer will be used, otherwise, uv_layer is considered to be the index of the wanted UV layer."

    if obj.mode == "EDIT":
        mesh = bmesh.from_edit_mesh(obj.data)
    else:
        mesh = bmesh.new()
        mesh.from_mesh(obj.data)

    uv_layer_index = mesh.loops.layers.uv.get(TARGET_UV_MAP)

    uv_map = dict()
    for face in mesh.faces:
        for loop in face.loops:
            uv = loop[uv_layer_index].uv.copy()
            uv.y = 1.0 - uv.y
            uv_map[loop.vert.index] = uv

    return uv_map


class UVTransformationCalculator:
    def __init__(self, reference_uv_map: dict[int, Vector]) -> None:
        # Find two furthest points in UV map
        max_len = None
        for ref_index1, ref1 in reference_uv_map.items():
            for ref_index2, ref2 in reference_uv_map.items():
                l = (ref1 - ref2).length
                if max_len is None or l > max_len:
                    max_len = l
                    endpoints = ref_index1, ref_index2

        self.ep1, self.ep2 = endpoints
        self.reference_distance = max_len
        self.reference_uv_map = reference_uv_map

        log.info(
            f"UV endpoints {self.ep1}:{reference_uv_map[self.ep1]} - {self.ep2}:{reference_uv_map[self.ep2]}",
            print_console=False,
        )

    def get_centroid(self, uv_map: dict[int, Vector]) -> Vector:
        vecs = list(uv_map.values())
        sorted_x = sorted(vecs, key=lambda v: v.x)
        sorted_y = sorted(vecs, key=lambda v: v.y)
        min_x, max_x = sorted_x[0].x, sorted_x[-1].x
        min_y, max_y = sorted_y[0].y, sorted_y[-1].y
        return Vector(((min_x + max_x) / 2, (min_y + max_y) / 2))

    def calculate_transform(self, target_uv_map: dict[int, Vector]) -> UVTransform:
        # Get reference and target endpoints as vectors
        R1, R2 = self.reference_uv_map[self.ep1], self.reference_uv_map[self.ep2]
        T1, T2 = target_uv_map[self.ep1], target_uv_map[self.ep2]
        distance = (T1 - T2).length

        # Calculate scale
        scale = distance / self.reference_distance

        # Calculate rotation
        reference_vector = (R2 - R1).normalized()
        target_vector = (T2 - T1).normalized()
        rotation = reference_vector.angle_signed(target_vector)

        # Calculate translation
        reference_centroid = self.get_centroid(self.reference_uv_map)
        target_centroid = self.get_centroid(target_uv_map)
        translation = target_centroid - reference_centroid

        transform = UVTransform(
            centroid=reference_centroid,
            translation=translation,
            scale=scale,
            rotation=rotation,
        )
        log.info(f"UV Transform: {transform}", print_console=False)
        return transform
