import base64
import functions_framework
import json
import pandas as pd
from firebase_admin import initialize_app, firestore
import google.cloud.firestore

app = initialize_app()

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    base_data = base64.b64decode(cloud_event.data["message"]["data"])
    decoded_data = json.loads(base_data.decode('utf-8'))

    test_data = pd.concat(
        [pd.json_normalize(decoded_data["object"]["messages"][0]),
        pd.json_normalize(decoded_data["object"]["messages"][1])]
    )

    test_data["time"] = decoded_data["time"]

    records = test_data.to_json(orient = "records",lines = True)

    # [START adminSdkPush]
    firestore_client: google.cloud.firestore.Client = firestore.client()

    # Push the new message into Cloud Firestore using the Firebase Admin SDK.
    _, doc_ref = firestore_client.collection("messages").add({"record": records})

    print(records)