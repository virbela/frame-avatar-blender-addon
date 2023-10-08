import bpy
from bpy.types import Operator, Context

from .base import FabaOperator
from .common import GenericList
from ..utils.helpers import AttrGet, AttrSet
from ..props import HomeomorphicProperties


class Effects:
    @staticmethod
    def add(operator: Operator, context: Context, ht: HomeomorphicProperties) -> None:
        GenericList.add(
            ht.effect_collection,
            AttrGet(ht, "selected_effect"),
            AttrSet(ht, "selected_effect"),
        )

    @staticmethod
    def remove(
        operator: Operator, context: Context, ht: HomeomorphicProperties
    ) -> None:
        GenericList.remove(
            ht.effect_collection,
            AttrGet(ht, "selected_effect"),
            AttrSet(ht, "selected_effect"),
        )

    @staticmethod
    def add_position_effect(
        operator: Operator, context: Context, ht: HomeomorphicProperties
    ) -> None:
        if ht.selected_effect != -1:
            et = ht.effect_collection[ht.selected_effect]
            et.positions.add()

    @staticmethod
    def remove_position_effect(
        operator: Operator, context: Context, ht: HomeomorphicProperties
    ) -> None:
        if ht.selected_effect != -1:
            et = ht.effect_collection[ht.selected_effect]
            et.positions.remove(operator.index)

    @staticmethod
    def add_color_effect(
        operator: Operator, context: Context, ht: HomeomorphicProperties
    ) -> None:
        if ht.selected_effect != -1:
            et = ht.effect_collection[ht.selected_effect]
            et.colors.add()

    @staticmethod
    def remove_color_effect(
        operator: Operator, context: Context, ht: HomeomorphicProperties
    ) -> None:
        if ht.selected_effect != -1:
            et = ht.effect_collection[ht.selected_effect]
            et.colors.remove(operator.index)


class FABA_OT_remove_effect(FabaOperator):
    bl_label = "-"
    bl_description = "Remove selected effect"
    bl_idname = "faba.remove_effect"
    faba_operator = Effects.remove


class FABA_OT_add_effect(FabaOperator):
    bl_label = "+"
    bl_description = "Add Effect"
    bl_idname = "faba.add_effect"
    faba_operator = Effects.add


class FABA_OT_remove_position_effect(FabaOperator):
    bl_label = "-"
    bl_description = "Remove position effect"
    bl_idname = "faba.remove_position_effect"
    faba_operator = Effects.remove_position_effect

    index: bpy.props.IntProperty()  # type: ignore


class FABA_OT_add_position_effect(FabaOperator):
    bl_label = "+"
    bl_description = "Add position effect"
    bl_idname = "faba.add_position_effect"
    faba_operator = Effects.add_position_effect


class FABA_OT_remove_color_effect(FabaOperator):
    bl_label = "-"
    bl_description = "Remove color effect"
    bl_idname = "faba.remove_color_effect"
    faba_operator = Effects.remove_color_effect

    index: bpy.props.IntProperty()  # type: ignore


class FABA_OT_add_color_effect(FabaOperator):
    bl_label = "+"
    bl_description = "Add color effect"
    bl_idname = "faba.add_color_effect"
    faba_operator = Effects.add_color_effect
