from .logging import log_writer as log
from .config import default_config as config
from .constants import IGNORED
from dataclasses import dataclass


class validation_error:
	# Abstract errors
	@dataclass
	class invalid_bake_target_configuration:
		bake_target:	object

	class internal_error:
		pass

	# Concrete errors - invalid bake target configuration
	class invalid_object_reference(invalid_bake_target_configuration):
		pass

	class too_low_uv_area_weight(invalid_bake_target_configuration):
		pass

	class too_great_uv_area_weight(invalid_bake_target_configuration):
		pass

	class no_atlas_assigned(invalid_bake_target_configuration):
		pass

	# Concrete errors - internal data inconsistencies
	@dataclass
	class invalid_enum(internal_error):
		bake_target:	object
		member:			str




def validate_bake_target_variant(ht, bake_target):
	pass	#TODO - implement
	return []


def validate_bake_target(ht, bake_target):
	result = list()
	# check object reference
	if bake_target.get_object() is None:
		result.append(validation_error.invalid_object_reference(bake_target))

	# check uv area weight
	if config.min_uv_area_weight is not IGNORED and bake_target.uv_area_weight < config.min_uv_area_weight:
		result.append(validation_error.too_low_uv_area_weight(bake_target))
	elif config.max_uv_area_weight is not IGNORED and bake_target.uv_area_weight > config.max_uv_area_weight:
		result.append(validation_error.too_great_uv_area_weight(bake_target))

	# check bake mode
	if bake_target.bake_mode == 'UV_BM_REGULAR':

		if bake_target.uv_mode == 'UV_IM_MONOCHROME':
			pass	#TODO - implement
		elif bake_target.uv_mode == 'UV_IM_COLOR':
			pass	#TODO - implement
		elif bake_target.uv_mode == 'UV_IM_NIL':
			pass	#TODO - implement
		elif bake_target.uv_mode == 'UV_IM_FROZEN':
			pass	#TODO - implement
		else:
			result.append(validation_error.invalid_enum(bake_target, 'uv_mode'))

		# check atlas
		if bake_target.atlas is None:
			result.append(validation_error.no_atlas_assigned(bake_target))


		# TODO(ranjian0) uv_target_channel is a prop in variant not bake target
		# check uv target channel
		# if bake_target.uv_target_channel == 'UV_TARGET_NIL':
		# 	pass	#TODO - implement
		# elif bake_target.uv_target_channel == 'UV_TARGET_COLOR':
		# 	pass	#TODO - implement
		# elif bake_target.uv_target_channel == 'UV_TARGET_R':
		# 	pass	#TODO - implement
		# elif bake_target.uv_target_channel == 'UV_TARGET_G':
		# 	pass	#TODO - implement
		# elif bake_target.uv_target_channel == 'UV_TARGET_B':
		# 	pass	#TODO - implement
		# else:
		# 	result.append(validation_error.invalid_enum(bake_target, 'uv_target_channel'))


		# check multi variants
		if bake_target.multi_variants:
			for variant in bake_target.variant_collection:
				result += validate_bake_target_variant(ht, bake_target)


	elif bake_target.bake_mode == 'UV_BM_MIRRORED':
		pass	#TODO - implement
		#TODO	mirror_source
		#TODO	uv_mirror_axis
	else:
		result.append(validation_error.invalid_enum(bake_target, 'bake_mode'))

	return result


def validate_all(ht):
	result = list()
	log.info('Validating all bake targets')
	for bake_target in ht.bake_target_collection:
		result += validate_bake_target(ht, bake_target)

	for item in result:
		log.info(item)

	return result