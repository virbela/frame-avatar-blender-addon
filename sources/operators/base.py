import bpy

from ..helpers import get_homeomorphic_tool_state, pending_classes
from ..exceptions import BakeException, InternalError
from ..logging import log_writer as log

class frame_operator(bpy.types.Operator):
	frame_operator = lambda context, HT: None
	frame_poll = lambda context : True

	#contribution note 6B
	def __init_subclass__(cls):
		pending_classes.append(cls)

	@classmethod
	def poll(cls, context):
		return cls.frame_poll(context)

	def execute(self, context):
		if HT := get_homeomorphic_tool_state(context):	#contribution note 2
			if self.frame_operator:
				try:
					self.frame_operator(context, HT)

				except BakeException.base as e:	#contribution note 4
					log.exception(f'Exception when calling operator for {self}: {e}')
					return {'CANCELLED'}

				except Exception as e:
					log.exception(f'Exception when calling operator for {self}: {e}')
					raise #We also raise this to let blender know things went wrong

				return {'FINISHED'}
			else:
				raise InternalError(f'{self} does not define `frame_operator` and can not be executed')	#contribution note 5

		return {'CANCELLED'}

