import base64
import functions_framework
import json
import pandas as pd
from google.cloud import storage, bigquery

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def topic_transform_load(cloud_event):

    # Triggers to turn on or off portions of this function
    logging = True
    cloud_storage = True
    big_query = True
    firestore = True

    # Various resource names
    ### Cloud Storage
    bucket_name = "kesterweather_measurements"

    ### BigQuery Write Table
    table_id = "weather-station-ef6ca.weather_measures.measures"

    # Extract the data from the cloud event and load it as a JSON.
    base_data = base64.b64decode(cloud_event.data["message"]["data"])
    decoded_data = json.loads(base_data.decode('utf-8'))

    # Print the time and data of the event to the logs 
    print("Time is "+str(decoded_data["time"]))
    if logging:
      print("The following records were in this message:")
      print(decoded_data)

    # The data is provided in two objects but we want them combined. I'll
    #  do this here by concatenating them into a pandas dataframe.
    combined_data = pd.concat(
        [pd.json_normalize(decoded_data["object"]["messages"][0]),
        pd.json_normalize(decoded_data["object"]["messages"][1])]
    )

    # Add the datetime object as a field to the dataframe.
    combined_data["time"] = decoded_data["time"]

    # Convert the pandas dataframe to a JSONL (JSON line) object
    records = combined_data.to_json(orient = "records",lines = True)

    if logging:
      print("Extracted and Transformed Data:")
      print(records)

    # Write parsed message to a Cloud Storage bucket
    if cloud_storage:

        # Give the file a unique name
        destination_blob_name = "measure_" + str(decoded_data["time"])

        # Uploads a file to the bucket.
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        blob.upload_from_string(records)

        print("Cloud Storage Complete!")

    if big_query:

        # Create a connection object to BigQuery
        client = bigquery.Client()

        # Reference a specific BigQuery Table
        table = client.get_table(table_id)

        # Insert Data Into the Table. If an error occurs, the dictionary is not empty so we print its contents
        errors = client.insert_rows_from_dataframe(table, combined_data)
        if errors == [[]]:
            print("Success, data loaded in Big Query")
            return "Success"
        else:
            print("An error occured")
            print(errors)
            return "Failed"


