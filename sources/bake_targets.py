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
