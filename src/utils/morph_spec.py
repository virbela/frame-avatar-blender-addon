from pprint import pformat
from bpy.types import Object, Mesh

from .helpers import popup_message
from .logging import log_writer as log

EXPECTED_SHAPEKEYS_COMMON = [
    'Basis',

    # -- mouth animation effects
    'FacialHairs_open_effect',
    'FacialHairs_Long_open_effect',
    'Face_Human_Mouth_Open_effect',
    'FacialHairs_Goatee_open_effect',
    'Face_Human_female_Mouth_Open_effect',

    # -- android
    'Eyes_Android',
    'Face_Android_Complete',
    'Body_Android',

    # -- face
    'Face_Human',
    'Face_Human_female',
    'Eye_Ball',
    'Eye_Pupil',
    'Eye_Lid',
    'Eye_Lid_Liner',
    'Eye_Lid_Liner_Close',
    'Eyebrows__None',
    'FacialHairs_Mustache',
    'FacialHairs_Goatee',
    'FacialHairs',
    'FacialHairs_Long',
    'Hairs_Afro',
    'Hairs_Bob',
    'Hairs_Bun',
    'Hairs_Long_Straight',
    'Hairs_Long_Wavy',
    'Hairs_Crew',
    'Hairs_Mid',
    'Hairs_Mohawk',
    'Hairs_Ponytail',
    'Hairs_Short',
    'Hairs_Tonsure__Hairs_Short',
    'Hairs_Cornrows__None',
    'Hairs_Odango',
    'Hairs_Pigtails',
    'Hairs_Spiky',
    'Hairs_BasicHelmet',
    'Hairs_Undercut_Curly',
    'Hairs_Undercut_Straight',
    'Hairs_Undercut_Mohawk',
    'Hairs_CombOver__Hairs_Short',
    'Hairs_Dreads_Short_1',
    'Hairs_Dreads_Short_2',

    # -- accessories Earings
    'Earring_Hoop_Big_Left__None',
    'Earring_Hoop_Big_Right__None',
    'Earring_Hoop_Small_Left__None',
    'Earring_Hoop_Small_Right__None',
    'Earring_Hoop_Top_Left__None',
    'Earring_Hoop_Top_Right__None',
    'Earring_Post_Left__None',
    'Earring_Post_Right__None',

    # -- accessories Glasses
    'Glasses_Ractangular__None',
    'Glasses_Squares__None',
    'Glasses_Sun_Aviator',
    'Glasses_Sun_Rectangular__Glasses_Sun_Aviator',
    'Glasses_Sun_Round__Glasses_Sun_Aviator',
    'Glasses_Sun_Square__Glasses_Sun_Aviator',

    # -- accessories Hats
    'Hat_Baseball',
    'Hat_Cowboy',
    'Hat_Fedora',
    'Hat_Fedora_Height__Hat_Fedora',
    'Hat_Knitcap',
    'Hat_Knitcap_Deco',
    'Hat_Military',
    'Hat_Newsboy',
    'Hat_Winter',
    'Hat_Hairs_Short__Hairs_Short',
    'Hat_Hairs_Long__Hairs_Long_Wavy',
    'Hat_Hairs_Long2__Hairs_Long_Wavy',
    'Hat_Hairs_Baseball_Long__Hairs_Long_Wavy',
    'Hat_Hairs_Baseball_Ponytail',
    'Hat_Hairs_Winter_Long__Hairs_Long_Wavy',
    'Hat_Knitcap_Border__None',
    'Hat_Hijab',
    'Hat_Yarmulke__None',
    'Hat_Cloche__Hat_Fedora',
    'Hat_Hairs_Cloche_LongStraight__Hairs_Long_Straight',
    'Hat_Hairs_Cloche_LongWavy__Hairs_Long_Wavy',
    'Hat_Hairs_Cloche_Short__Hairs_Short',

    # -- body
    'Body_Human',

    # -- UNUSED (DEPRECATE)
    'Hand',
    'Eye_L',
    'Eye_R',
    'Eye_Border_L',
    'Eye_Border_R',
]

EXPECTED_SHAPEKEYS_FLOATER = [
    'Jacket_SkiJacket',
    'Jacket_Cardigan',
    'Jacket_Blazer',
    'Jacket_Insulated',
    'Jacket_Bolero__Jacket_Cardigan',
    'Jacket_Vest',
    'Jacket_Poncho',
]

EXPECTED_SHAPEKEYS_FLOATER.extend(
    EXPECTED_SHAPEKEYS_COMMON
)

EXPECTED_SHAPEKEYS_FULLBODY = [
    'Arm_L',
    'Arm_R',

    'Leg_L',
    'Leg_R',
    'Formal_pants_L',
    'Formal_pants_R',
    'Boot_short_L',
    'Boot_short_R',

    'Sleeves_Short',
    'Formal_sleeve_L',
    'Formal_sleeve_R',
    'Informal_sleeve_R',
    'Informal_sleeve_L',

    'Formal_Jacket',
    'Informal_Jacket'
]

EXPECTED_SHAPEKEYS_FULLBODY.extend(
    EXPECTED_SHAPEKEYS_COMMON
)

DEPRECATED_SHAPEKEYS = [
    'Hand',
    'Eye_L',
    'Eye_R',
    'Eye_Border_L',
    'Eye_Border_R',
]

def validate_fullbody_morphs(avatar_obj: Object) -> bool:
    me: Mesh = avatar_obj.data
    keys_names = [k.name for k in me.shape_keys.key_blocks]

    names_diff_missing = set(EXPECTED_SHAPEKEYS_FULLBODY) - set(keys_names)
    missing = list(names_diff_missing - set(DEPRECATED_SHAPEKEYS))

    if missing:
        log.error("The following shapekeys are required in the fullbody, but were not found!")
        log.error('--\n' + pformat(sorted(missing)))

        error_str = ", ".join(missing)
        popup_message(error_str, "Missing Shapekeys!")
        return False 

    # XXX Additional shapekeys can be remove during the export step
    # names_diff_additional = set(keys_names) - set(EXPECTED_SHAPEKEYS_FULLBODY)
    # log.info("The following shapekeys were found in the full body avatar, but are not required")
    # log.info(names_diff_additional)
    return True

def validate_floater_morphs(avatar_obj: Object) -> bool:
    me: Mesh = avatar_obj.data
    keys_names = [k.name for k in me.shape_keys.key_blocks]

    names_diff_missing = set(EXPECTED_SHAPEKEYS_FLOATER) - set(keys_names)
    missing = list(names_diff_missing - set(DEPRECATED_SHAPEKEYS))

    if missing:
        log.error("The following shapekeys are required in the floater, but were not found!")
        log.error('--\n' + pformat(sorted(missing)))

        error_str = ", ".join(missing)
        popup_message(error_str, "Missing Shapekeys!")
        return False 

    # XXX Additional shapekeys can be remove during the export step
    # names_diff_additional = set(keys_names) - set(EXPECTED_SHAPEKEYS_FLOATER)
    # log.info("The following shapekeys were found in the floater avatar, but are not required")
    # log.info(names_diff_additional)
    return True
