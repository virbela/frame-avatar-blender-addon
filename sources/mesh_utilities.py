import bmesh
from mathutils import Vector, Matrix
from math import acos, pi

#Create singletons of special meaning
ACTIVE_LAYER = type('ACTIVE_LAYER', (), {})

#Settings
TRESHOLD = 1e-4	#I don't understand why we need such a "loose" treshold for this dataset.


def quantize_value(value, step):
	return round(value / step) * step


def get_uv_map_from_mesh(obj, uv_layer=ACTIVE_LAYER):
	'If uv_layer is ACTIVE_LAYER, the active UV layer will be used, otherwise, uv_layer is considered to be the index of the wanted UV layer.'

	mesh = bmesh.new()
	mesh.from_mesh(obj.data)

	if uv_layer is ACTIVE_LAYER:
		uv_layer_index = mesh.loops.layers.uv.active
	else:
		uv_layer_index = uv_layer

	uv_map = dict()
	for face in mesh.faces:
		for loop in face.loops:
			uv_map[loop.vert.index] = Vector(loop[uv_layer_index].uv)	#Note - copy Vector here since the vector reference will be invalid outside of this context

	return uv_map


def rotate_vector(vector, rotation):
	new_vector = vector.copy()	#It is possible .rotate modifies in place so it seems best to copy first - this could be adjusted if this is not the case
	new_vector.rotate(Matrix.Rotation(rotation, 2))

	return new_vector

class uv_transformation_calculator:
	def __init__(self, reference_uv_map):
		#Find two furthest points in UV map
		max_len = None

		for ref_index1, ref1 in reference_uv_map.items():
			for ref_index2, ref2 in reference_uv_map.items():
				l = (ref1 - ref2).magnitude
				if max_len is None or l > max_len:
					max_len = l
					endpoints = ref_index1, ref_index2
					print(ref1, ref2, l)

		self.ep1, self.ep2 = endpoints
		self.reference_distance = max_len
		self.reference_uv_map = reference_uv_map

		#Todo - make sure we found proper endpoints?


	def calculate_transform(self, target_uv_map):

		try:
			#Get reference and target endpoints as vectors
			R1, R2 = self.reference_uv_map[self.ep1], self.reference_uv_map[self.ep2]
			T1, T2 = target_uv_map[self.ep1], target_uv_map[self.ep2]

			#Calculate distances of the endpoints of target_uv_map
			distance = (T1 - T2).magnitude

			#Calculate scale
			scale = distance / self.reference_distance

			#Calculate rotation
			reference_vector = (R2 - R1).normalized()
			target_vector = (T2 - T1).normalized()
			dot = reference_vector.dot(target_vector)

			if 1.0 < dot <= (1.0 + TRESHOLD):	#Check for slight overflow (a lot of overflow would create a math domain error)
				dot = 1.0

			rotation = acos(dot)

			#Note from https://docs.blender.org/api/current/mathutils.html
			# 2D vectors are a special case that can only be rotated by a 2x2 matrix.

			pos_rot_result = (rotate_vector(reference_vector, rotation) - target_vector).magnitude
			neg_rot_result = (rotate_vector(reference_vector, -rotation) - target_vector).magnitude
			#We scale the comparisons to make sure the error is scale invariant
			if pos_rot_result * scale < TRESHOLD:
				pass
				#print(f'rotation: +{rotation}')
			elif neg_rot_result * scale < TRESHOLD:
				pass
				#print(f'rotation: -{rotation}')
			else:
				raise Exception(f'Could not determine rotation (got {rotation} for vectors {reference_vector} and {target_vector}, distances: {pos_rot_result * scale}, {neg_rot_result * scale} (treshold: {TRESHOLD}))')

			# Note: If we want to quantize rotation we should do that here (this could be an option in that case)
			# rotation = quantize_value(rotation, pi * .5)

			#Calculate translation
			translation = T1 - rotate_vector(R1, rotation) * scale

			return [translation.x, translation.y, rotation, scale]
		except ValueError as source_error:
			raise ValueError(f'Failed to calcualte transform of UV map using reference points {R1} - {R2} and target points {T1} - {T2}.') from source_error