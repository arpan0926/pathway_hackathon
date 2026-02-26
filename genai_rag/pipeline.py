import pathway as pw
import time

print("🚀 Pathway Logistics Pipeline started")

# Schema definitions matching database columns
class ShipmentSchema(pw.Schema):
    shipment_id: str = pw.column_definition(primary_key=True)
    source: str
    destination: str
    vehicle_id: str
    status: str
    current_eta: int

class TelemetrySchema(pw.Schema):
    id: int = pw.column_definition(primary_key=True)
    shipment_id: str
    ts: int
    lat: float
    lon: float
    speed_kmph: float
    load_status: str

class AlertSchema(pw.Schema):
    id: int = pw.column_definition(primary_key=True)
    shipment_id: str
    alert_type: str
    metric: str
    value: float
    threshold: float
    is_active: bool

# Kafka settings
rdkafka_settings = {
    "bootstrap.servers": "kafka:9092",
    "group.id": "pathway-logistics-group",
    "auto.offset.reset": "earliest",
}

# Read from Debezium CDC streams
shipments = pw.io.debezium.read(
    rdkafka_settings,
    topic_name="dbserver1.public.shipments",
    type="postgres",
    schema=ShipmentSchema
)

telemetry = pw.io.debezium.read(
    rdkafka_settings,
    topic_name="dbserver1.public.telemetry",
    type="postgres",
    schema=TelemetrySchema
)

alerts = pw.io.debezium.read(
    rdkafka_settings,
    topic_name="dbserver1.public.alerts",
    type="postgres",
    schema=AlertSchema
)

# Transform and select columns
shipments_view = shipments.select(
    shipment_id=pw.this.shipment_id,
    source=pw.this.source,
    destination=pw.this.destination,
    vehicle_id=pw.this.vehicle_id,
    status=pw.this.status
)

telemetry_view = telemetry.select(
    shipment_id=pw.this.shipment_id,
    speed_kmph=pw.this.speed_kmph,
    lat=pw.this.lat,
    lon=pw.this.lon,
    load_status=pw.this.load_status
)

alerts_view = alerts.select(
    shipment_id=pw.this.shipment_id,
    alert_type=pw.this.alert_type,
    metric=pw.this.metric,
    value=pw.this.value,
    threshold=pw.this.threshold,
    is_active=pw.this.is_active
)

# Output to stdout
print("\n📦 === SHIPMENTS STREAM ===")
pw.io.jsonlines.write(shipments_view, "/dev/stdout")

print("\n📡 === TELEMETRY STREAM ===")
pw.io.jsonlines.write(telemetry_view, "/dev/stdout")

print("\n🚨 === ALERTS STREAM ===")
pw.io.jsonlines.write(alerts_view, "/dev/stdout")

# Run the pipeline
pw.run()