import typing
from bpy.types import Operator, Context
from ..utils.logging import log
from ..utils.exceptions import BakeException, InternalError
from ..utils.helpers import get_homeomorphic_tool_state

class FabaOperator(Operator):
  faba_poll = lambda context : True
  faba_operator = lambda context, HT: None

  @classmethod
  def poll(cls, context: Context) -> bool:
    return cls.faba_poll(context)

  def execute(self, context: Context) -> typing.Union[typing.Set[str], typing.Set[int]]:
    if HT := get_homeomorphic_tool_state(context):	#contribution note 2
      if self.faba_operator:
        try:
          self.faba_operator(context, HT)

        except BakeException.base as e:	#contribution note 4
          log.exception(f"Exception when calling operator for {self}: {e}")
          return {"CANCELLED"}

        except Exception as e:
          log.exception(f"Exception when calling operator for {self}: {e}")
          return {"CANCELLED"}

        return {"FINISHED"}
      else:
        raise InternalError(f"{self} does not define `frame_operator` and can not be executed")	#contribution note 5

    return {"CANCELLED"}

