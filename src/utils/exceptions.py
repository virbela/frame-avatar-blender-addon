import typing
from bpy.types import Object


class InternalError(Exception):
    pass


class FrameException:
    class FailedToCreateNamedEntry(Exception):
        def __init__(self, collection: typing.Any, name: str) -> None:
            super().__init__(
                (
                    "Failed to create a named entry "
                    f"named `{name}` in collection {collection}."
                )
            )

    class NamedEntryNotFound(Exception):
        def __init__(self, collection: typing.Any, name: str) -> None:
            super().__init__(
                f"No entry named `{name}` was found in collection {collection}."
            )

    class NoNameGivenForCollectionLookup(Exception):
        def __init__(self, collection: typing.Any) -> None:
            super().__init__(
                f"No name was given for look up in collection {collection}."
            )


class BakeException:
    class base(Exception):
        pass

    class NoActiveMaterial(base):
        def __init__(self, object: Object) -> None:
            self.object = object
            super().__init__(
                f"{object} has no active material which is required for the operation."
            )

    class NoObjectChosen(base):
        def __init__(self, name: str) -> None:
            self.name = name
            super().__init__(
                (
                    "The operation requries an object to be"
                    f"chosen and no such object `{name}` exists."
                )
            )

    class NoSuchScene(base):
        def __init__(self, name: str) -> None:
            self.name = name
            super().__init__(
                f"The operation requires a scene named `{name}` which was not found."
            )

    class MissingBakeTargetVariant(base):
        def __init__(self, name: str) -> None:
            self.name = name
            super().__init__(f"A bake target was not found for `{name}`.")
