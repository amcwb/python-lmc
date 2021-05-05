from typing import Generic, List, Optional, Type, TypeVar


T = TypeVar('T')


class Listener(Generic[T]):
    def recv(self, data: T):
        raise NotImplementedError


ListenerType = Type[Listener]


class Bus(Generic[T]):
    listeners: List[ListenerType]

    def __init__(self) -> None:
        self.listeners = []

    def register(self, listener: ListenerType):
        self.listeners.append(listener)

    def broadcast(self, data: T):
        for listener in self.listeners:
            listener.recv(data)


class Register(ListenerType, Generic[T]):
    data: T

    def __init__(self, initial: Optional[T] = None):
        self.data = initial

    def recv(self, data: T):
        self.data = data
