import bmesh
from .local_math import convert_vectors, ROTATION_TRESHOLD
from .logging import log_writer as log

#Note that we could import local_math from . and override the ROTATION_TRESHOLD if needed

#Create singletons of special meaning
ACTIVE_LAYER = type('ACTIVE_LAYER', (), {})

def get_uv_map_from_mesh(obj, uv_layer=ACTIVE_LAYER):
	'If uv_layer is ACTIVE_LAYER, the active UV layer will be used, otherwise, uv_layer is considered to be the index of the wanted UV layer.'

	mesh = bmesh.from_edit_mesh(obj.data)

	if uv_layer is ACTIVE_LAYER:
		uv_layer_index = mesh.loops.layers.uv.active
	else:
		uv_layer_index = uv_layer

	uv_map = dict()
	for face in mesh.faces:
		for loop in face.loops:
			uv_point = convert_vectors(loop[uv_layer_index].uv)	#Note - copy Vector here since the vector reference will be invalid outside of this context
			uv_point.y = 1.0 - uv_point.y
			uv_map[loop.vert.index] = uv_point

	return uv_map



class uv_transformation_calculator:
	def __init__(self, reference_uv_map):

		#Find two furthest points in UV map
		max_len = None
		for ref_index1, ref1 in reference_uv_map.items():
			for ref_index2, ref2 in reference_uv_map.items():
				l = abs(ref1 - ref2)
				if max_len is None or l > max_len:
					max_len = l
					endpoints = ref_index1, ref_index2

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
			distance = abs(T1 - T2)

			#Calculate scale
			scale = distance / self.reference_distance

			#Calculate rotation - TODO: use the signed_angle feature of blenders Vector functions
			reference_vector = (R2 - R1).normalized()
			target_vector = (T2 - T1).normalized()

			rotation = reference_vector.get_signed_angle(target_vector)

			# Note: If we want to quantize rotation we should do that here (this could be an option in that case)
			# Note: If we do quantize rotation and the islands are not actually quantized in the rotation we will fail the verification step
			# rotation = quantize_value(rotation, pi * .5)

			#Calculate translation
			translation = T1 - R1.rotate(rotation) * scale


			#Verify calculated transform
			e1 = ((R1.rotate(rotation) * scale + translation) - T1).error()
			e2 = ((R2.rotate(rotation) * scale + translation) - T2).error()

			log.info(f'Translation: {translation} Rotation: {rotation} Errors: {e1, e2}')

			if e1 > ROTATION_TRESHOLD or e2 > ROTATION_TRESHOLD:
				raise ValueError('Failed to properly calculate transform')

			return [translation.x, translation.y, rotation, scale]
		except ValueError as source_error:
			raise ValueError(f'Failed to calcualte transform of UV map using reference points {R1} - {R2} and target points {T1} - {T2}.') from source_error
