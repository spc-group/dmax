import inspect
from collections.abc import Awaitable
from typing import TypeAlias, TypeVar

from typing_extensions import TypeIs

T = TypeVar("T")

SyncOrAsync: TypeAlias = T | Awaitable[T]


def _isawaitable(value: SyncOrAsync[T]) -> TypeIs[Awaitable[T]]:
    return inspect.isawaitable(value)


async def maybe_await(ret: SyncOrAsync[T]) -> T:
    if _isawaitable(ret):
        return await ret
    else:
        return ret
