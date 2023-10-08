import typing
from bpy.types import Operator, Context

from ..utils.logging import log
from ..props import HomeomorphicProperties
from ..utils.exceptions import BakeException
from ..utils.helpers import get_homeomorphic_tool_state

PollFunction = typing.Callable[[Context], bool]
OperatorFunction = typing.Callable[[Context, HomeomorphicProperties], None]


def empty_poll(context: Context) -> bool:
    return True


def empty_op(context: Context, ht: HomeomorphicProperties) -> None:
    pass


class FabaOperator(Operator):
    faba_poll: PollFunction = empty_poll
    faba_operator: OperatorFunction = empty_op

    @classmethod
    def poll(cls, context: Context) -> bool:
        return cls.faba_poll(context)

    def execute(
        self, context: Context
    ) -> typing.Union[typing.Set[str], typing.Set[int]]:
        if HT := get_homeomorphic_tool_state(context):
            try:
                self.faba_operator(context, HT)

            except BakeException.base as e:
                log.exception(f"Exception when calling operator for {self}: {e}")
                return {"CANCELLED"}

            except Exception as e:
                log.exception(f"Exception when calling operator for {self}: {e}")
                return {"CANCELLED"}

            return {"FINISHED"}
        return {"CANCELLED"}
