from abc import ABC, abstractmethod
from observability.event import ObservabilityEvent

class EventSink(ABC):
    @abstractmethod
    def emit(self, event: ObservabilityEvent):
        pass
