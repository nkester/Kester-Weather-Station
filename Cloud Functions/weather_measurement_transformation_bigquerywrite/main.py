import base64
import functions_framework
import json
import pandas as pd
from google.cloud import bigquery
#from firebase_admin import initialize_app, firestore
#import google.cloud.firestore
#from google.cloud import storage

#app = initialize_app()

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def extract_weather_measure(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    base_data = base64.b64decode(cloud_event.data["message"]["data"])
    decoded_data = json.loads(base_data.decode('utf-8'))

    test_data = pd.concat(
        [pd.json_normalize(decoded_data["object"]["messages"][0]),
        pd.json_normalize(decoded_data["object"]["messages"][1])]
    )

    test_data["time"] = decoded_data["time"]

    print(test_data)

    #records = test_data.to_json(orient = "records",lines = True)

    # [START adminSdkPush]
    #firestore_client: google.cloud.firestore.Client = firestore.client()

    # Push the new message into Cloud Firestore using the Firebase Admin SDK.
    #_, doc_ref = firestore_client.collection("messages").add({"record": records})

    # Bucket Informatoin
    #bucket_name = "kesterweather_measurements"
    #destination_blob_name = "measure_" + str(decoded_data["time"])

    # Uploads a file to the bucket.
    #storage_client = storage.Client()
    #bucket = storage_client.get_bucket(bucket_name)
    #blob = bucket.blob(destination_blob_name)

    #blob.upload_from_string(records)

    # Writing to BigQuery
    # From https://stackoverflow.com/questions/60844628/gcp-cloud-function-to-write-data-to-bigquery-runs-with-success-but-data-doesnt

    table_id = "weather-station-ef6ca.weather_measures.measures"
    
    ## Get BiqQuery Set up
    client = bigquery.Client()
    table = client.get_table(table_id)
    errors = client.insert_rows_from_dataframe(table, test_data)  # Make an API request.
    if errors == []:
        print("Data Loaded")
        return "Success"
    else:
        print(errors)
        return "Failed"

