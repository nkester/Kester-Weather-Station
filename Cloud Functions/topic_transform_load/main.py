import base64
import json
import functions_framework
from google.cloud import storage, bigquery

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def topic_transform_load(cloud_event):

    # Feature toggles
    enable_logging = True
    enable_cloud_storage = True
    enable_bigquery = True

    # Resource names
    bucket_name = "kesterweather_measurements"
    table_id = "weather-station-ef6ca.weather_measures.measures"

    # Decode Pub/Sub message
    raw_data = base64.b64decode(cloud_event.data["message"]["data"])
    decoded = json.loads(raw_data.decode("utf-8"))

    if enable_logging:
        print(f"Received uplink at {decoded.get('time')}")
        print("Full message:")
        print(json.dumps(decoded, indent=2))

    # Extract the flat object produced by the new S2120 v2.0 codec
    obj = decoded.get("object", {})

    # Build a normalized record matching your old schema
    # (type, measurementId, measurementValue)
    measurements = [
        {"type": "Air Temperature",       "measurementId": "4097", "measurementValue": obj.get("temperature_c")},
        {"type": "Air Humidity",          "measurementId": "4098", "measurementValue": obj.get("humidity_percent")},
        {"type": "Light Intensity",       "measurementId": "4099", "measurementValue": obj.get("light_lux")},
        {"type": "UV Index",              "measurementId": "4190", "measurementValue": obj.get("uv_index")},
        {"type": "Wind Speed",            "measurementId": "4105", "measurementValue": obj.get("wind_speed_m_s")},
        {"type": "Wind Direction Sensor", "measurementId": "4104", "measurementValue": obj.get("wind_direction_deg")},
        {"type": "Rain Gauge",            "measurementId": "4113", "measurementValue": obj.get("rainfall_intensity_mm_h")},
        {"type": "Barometric Pressure",   "measurementId": "4101", "measurementValue": obj.get("pressure_pa")},
        {"type": "Peak Wind Gust",        "measurementId": "4191", "measurementValue": obj.get("peak_wind_gust_m_s")},
        {"type": "Rain Accumulation",     "measurementId": "4213", "measurementValue": obj.get("rain_accumulation_mm")},
    ]

    # Add timestamp to each record
    for m in measurements:
        m["time"] = decoded.get("time")

    # Convert to JSON Lines format
    jsonl_output = "\n".join(json.dumps(m) for m in measurements)

    if enable_logging:
        print("Transformed JSONL:")
        print(jsonl_output)

    # -------------------------
    # Cloud Storage Upload
    # -------------------------
    if enable_cloud_storage:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        filename = f"measure_{decoded.get('time')}.jsonl"
        blob = bucket.blob(filename)
        blob.upload_from_string(jsonl_output)

        print(f"Uploaded to Cloud Storage: {filename}")

    # -------------------------
    # BigQuery Insert
    # -------------------------
    if enable_bigquery:
        client = bigquery.Client()
        table = client.get_table(table_id)

        errors = client.insert_rows_json(table, measurements)

        if not errors:
            print("BigQuery load successful")
        else:
            print("BigQuery load errors:")
            print(errors)

    return "OK"