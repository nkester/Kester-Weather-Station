# Cloud Function: `topic_transform_load`  

This function is triggered by messages published to the `weather` Pub/Sub topic. It reads the message, parses out the information, and performs three write actions. One to a file stored in a Google Cloud Storage bucket, one to a BigQuery dataset, and the final to a Google FireStore Document library. These are all redundant. The BigQuery dataset is the only currently used and the Cloud Storage bucket allows us to access past events in case we want to do something different. __The FireStore is no longer needed.__

Deploy with the following command. This assumes the shell is in the `Cloud Functions` directory (one level up from the source files).  

```
gcloud functions deploy topic_transform_load \
--gen2 \
--region=us-east1 \
--runtime=python312 \
--source=./topic_transform_load \
--entry-point=topic_transform_load \
--memory=256MiB \
--cpu=0.083 \
--timeout=60 \
--min-instances=0 \
--max-instances=5 \
--trigger-topic=weather
```

References:  
[GCP Regions](https://cloud.google.com/functions/docs/locations#tier_1_pricing)  
[GCP Deploy PubSub Functions](https://cloud.google.com/functions/docs/tutorials/pubsub#deploying_the_function)
[Python Runtimes](https://cloud.google.com/functions/docs/concepts/execution-environment#python)