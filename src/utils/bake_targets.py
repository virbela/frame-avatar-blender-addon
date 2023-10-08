from dataclasses import dataclass

from .helpers import popup_message
from ..props import BakeVariant, HomeomorphicProperties


class ValidationError:
    # Abstract errors
    @dataclass
    class InvalidBakeTargetConfiguration:
        bake_target: object

    class InternalError:
        pass

    # Concrete errors - invalid bake target configuration
    class InvalidObjectReference(InvalidBakeTargetConfiguration):
        pass

    class TooLowUvAreaWeight(InvalidBakeTargetConfiguration):
        pass

    class TooGreatUvAreaWeight(InvalidBakeTargetConfiguration):
        pass

    class NoAtlasAssigned(InvalidBakeTargetConfiguration):
        pass

    # Concrete errors - internal data inconsistencies
    @dataclass
    class InvalidEnum(InternalError):
        bake_target: object
        member: str


def validate_bake_target_setup(ht: HomeomorphicProperties) -> bool:
    for bake_target in ht.bake_target_collection:
        if not bake_target.shape_key_name:
            popup_message(f"Missing shapekey in {bake_target.name}", "Workmesh Error")
            return False

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
            popup_message(
                f"Missing intermediate atlas in {bake_target.name}", "Atlas Error"
            )
            return False

    return True
