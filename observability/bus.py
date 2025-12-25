from observability.sinks.log_sink import LogEventSink

class ObservabilityBus:
    def __init__(self):
        self.sinks = [LogEventSink()]

    def emit(self, event):
        for sink in self.sinks:
            sink.emit(event)


bus = ObservabilityBus()
