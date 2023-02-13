from dataclasses import dataclass

from .helpers import popup_message
from .properties import BakeVariant, HomeomorphicProperties

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


def validate_bake_target_setup(ht: HomeomorphicProperties) -> bool:
	for bake_target in ht.bake_target_collection:
		if bake_target.bake_mode == "UV_BM_MIRRORED":
			# XXX What to do here
			continue

		if bake_target.uv_mode == "UV_IM_NIL":
			# XXX Nil UV has not setup, skip
			continue

		# at this point we have a regular baketarget with uv setup
		# check that a workmesh and intermediate atlas is assigned
		default_variant: BakeVariant = bake_target.variant_collection[0]
		if not default_variant.workmesh:
			popup_message(f"Missing workmesh in {bake_target.name}", "Workmesh Error")
			return False 

		if not default_variant.intermediate_atlas:
			popup_message(f"Missing intermediate atlas in {bake_target.name}", "Atlas Error")
			return False

	return True