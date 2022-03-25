import bmesh
from mathutils import Matrix
from .logging import log_writer as log


def get_uv_map_from_mesh(obj):
	'If uv_layer is ACTIVE_LAYER, the active UV layer will be used, otherwise, uv_layer is considered to be the index of the wanted UV layer.'

	if obj.mode == 'EDIT':
		mesh = bmesh.from_edit_mesh(obj.data)
	else:
		mesh = bmesh.new()
		mesh.from_mesh(obj.data)

	uv_layer_index = mesh.loops.layers.uv.active

	uv_map = dict()
	for face in mesh.faces:
		for loop in face.loops:
			uv_map[loop.vert.index] = loop[uv_layer_index].uv.copy()

	return uv_map

class uv_transformation_calculator:
	def __init__(self, reference_uv_map):

		#Find two furthest points in UV map
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

		log.info(f"UV endpoints {self.ep1}:{reference_uv_map[self.ep1]} - {self.ep2}:{reference_uv_map[self.ep2]}")


	def calculate_transform(self, target_uv_map):
		#Get reference and target endpoints as vectors
		R1, R2 = self.reference_uv_map[self.ep1], self.reference_uv_map[self.ep2]
		T1, T2 = target_uv_map[self.ep1], target_uv_map[self.ep2]
		distance = (T1 - T2).length

		# Calculate scale
		scale = distance / self.reference_distance

		# Calculate rotation
		reference_vector = (R2 - R1).normalized()
		target_vector = (T2 - T1).normalized()
		rotation = reference_vector.angle_signed(target_vector)

		#Calculate translation
		original = R1.copy()
		original.rotate(Matrix.Rotation(rotation, 2))
		translation = T1 - (original * scale)

		log.info(f"UV Transform: T:{translation} R:{rotation} S:{scale}")

		return [translation.x, translation.y, rotation, scale]
