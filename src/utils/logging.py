import bpy
import enum
import time
import types
import textwrap
import traceback
from dataclasses import dataclass


class LogLevel(enum.IntEnum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5


@dataclass
class PendingLogEntry:
    timestamp: time.struct_time
    log_level: LogLevel
    message: str


class LogLevelDescriptor:
    def __init__(
        self, log_instance: "LogBase", log_level: LogLevel, description: str
    ) -> None:
        self.__doc__ = description
        self.log_instance = log_instance
        self.log_level = log_level

    def __call__(self, message: str, print_console: bool = True) -> None:
        self.log_instance.process_message(
            PendingLogEntry(time.localtime(), self.log_level, message), print_console
        )


class LogBase:
    MAX_HISTORY = 1000

    def __init__(self) -> None:
        self.history = list()

        self.debug = LogLevelDescriptor(
            self,
            LogLevel.DEBUG,
            "Debug log entries are intended for addon developer use only",
        )
        self.info = LogLevelDescriptor(
            self, LogLevel.INFO, "Generic information to keep the user in the loop"
        )
        self.warning = LogLevelDescriptor(
            self,
            LogLevel.WARNING,
            (
                "Warnings are intended for things that is not really an error but that "
                "the user should still be made aware of"
            ),
        )
        self.error = LogLevelDescriptor(
            self, LogLevel.ERROR, "Errors the user should be made aware of"
        )
        self.fatal = LogLevelDescriptor(
            self,
            LogLevel.FATAL,
            (
                "Fatal errors are errors that we can't recover from and we don't "
                "know how to tell the user to recover from them"
            ),
        )

    def exception(self, message: str) -> None:
        tab = "\t"
        self.fatal(
            f"{message}\n{textwrap.indent(traceback.format_exc().strip(), tab)}\n"
        )


class LogInstance(LogBase):
    "Log instance"

    def process_message(self, message: PendingLogEntry, print_console: bool) -> None:
        preferences: types.SimpleNamespace | bpy.types.AddonPreferences
        try:
            preferences = bpy.context.preferences.addons[__package__].preferences
        except KeyError:
            # XXX DEV(simulate preferences
            preferences = types.SimpleNamespace()
            preferences.log_target = "devlog"

        # Get or create text target based on addon preference `log_target´
        text = bpy.data.texts.get(preferences.log_target) or bpy.data.texts.new(
            preferences.log_target
        )

        t = time.strftime("%X", message.timestamp)
        line = f"{t} {message.log_level.name}: {message.message}"
        text.write(f"{line}\n")
        if print_console:
            print(line)
        self.history.append(message)

        if len(self.history) > self.MAX_HISTORY:
            self.history = self.history[-self.MAX_HISTORY :]


class DummyLogInstance(LogBase):
    "Dummy log"

    def process_message(self, message: PendingLogEntry) -> None:
        pass


log = LogInstance()
no_logging = DummyLogInstance()
