from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Input = TypeVar('Input', contravariant=True)
Output = TypeVar('Output', covariant=True)


class UseCaseInterface(Generic[Input, Output], ABC):
    """
    Base class  for use case contract
    `input` and `output` usualy DTOs
    """

    @abstractmethod
    async def __call__(self, input: Input) -> Output:
        raise NotImplementedError
