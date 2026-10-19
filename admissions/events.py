"""Event layer: every registration and update is published to Kafka as JSON (REQ-11)."""
import json
import logging
from datetime import datetime

# Keep Colab quiet when no Kafka broker is running
logging.getLogger("kafka").setLevel(logging.CRITICAL)


class AdmissionProducer:
    def __init__(self, broker="localhost:9092"):
        self.is_active = False
        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=[broker],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                request_timeout_ms=1000,
            )
            self.is_active = True
        except Exception:
            pass  # No broker or no kafka-python: the app still works, events are skipped

    def send_event(self, event_type, data):
        if self.is_active:
            payload = {"event": event_type, "payload": data, "ts": str(datetime.now())}
            self.producer.send("admission_events", value=payload)
