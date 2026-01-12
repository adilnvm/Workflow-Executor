from observability.sinks.log_sink import LogEventSink
from metrics.collector import metrics


class ObservabilityBus:
    def __init__(self):
        self.sinks = [LogEventSink()]

    def emit(self, event):
        for sink in self.sinks:
            sink.emit(event)

        metrics.record(event.event_type, event.payload)

bus = ObservabilityBus()
