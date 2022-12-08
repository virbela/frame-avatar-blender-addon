import typing
from bpy.types import Operator, Context
from ..utils.logging import log_writer as log
from ..utils.exceptions import BakeException, InternalError
from ..utils.helpers import get_homeomorphic_tool_state, pending_classes

class frame_operator(Operator):
	frame_poll = lambda context : True
	frame_operator = lambda context, HT: None

	#contribution note 6B
	def __init_subclass__(cls):
		pending_classes.append(cls)

	@classmethod
	def poll(cls, context: Context) -> bool:
		return cls.frame_poll(context)

	def execute(self, context: Context) -> typing.Union[typing.Set[str], typing.Set[int]]:
		if HT := get_homeomorphic_tool_state(context):	#contribution note 2
			if self.frame_operator:
				try:
					self.frame_operator(context, HT)

				except BakeException.base as e:	#contribution note 4
					log.exception(f'Exception when calling operator for {self}: {e}')
					return {'CANCELLED'}

				except Exception as e:
					log.exception(f'Exception when calling operator for {self}: {e}')
					return {'CANCELLED'}

				return {'FINISHED'}
			else:
				raise InternalError(f'{self} does not define `frame_operator` and can not be executed')	#contribution note 5

		return {'CANCELLED'}

