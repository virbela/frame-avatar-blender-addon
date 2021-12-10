import bpy

from ..helpers import get_homeomorphic_tool_state, pending_classes
from ..exceptions import BakeException, InternalError

class frame_operator(bpy.types.Operator):
	frame_operator = None

	#contribution note 6B
	def __init_subclass__(cls):
		pending_classes.append(cls)

	def execute(self, context):
		if HT := get_homeomorphic_tool_state(context):	#contribution note 2
			if self.frame_operator:
				try:
					self.frame_operator(context, HT)

				except BakeException.base as e:	#contribution note 4
					#TODO - log this error properly
					print('FAIL', e)
					return {'CANCELLED'}

				#TODO - we should also catch the generic exception, log it (including traceback) and then re-raise it for blender to deal with it

				return {'FINISHED'}
			else:
				raise InternalError(f'{self} does not define `frame_operator´ and can not be executed')	#contribution note 5

		return {'CANCELLED'}

