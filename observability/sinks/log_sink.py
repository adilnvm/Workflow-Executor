import json
from observability.sink import EventSink

class LogEventSink(EventSink):
    def emit(self, event):
        print("[OBS]", json.dumps(event.to_dict(), indent=2))
