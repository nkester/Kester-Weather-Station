# Cloud Function: `https_measure_60day_asis`  

Deploy with the following command. This assumes the shell is in the current directory of the source files.  

```
gcloud functions deploy https_measure_60day_asis \
--gen2 \
--region=us-east1 \
--runtime=python312 \
--source=./https_measure_60day_asis \
--entry-point=https_measure_60day_asis \
--allow-unauthenticated \
--memory=512MiB \
--cpu=0.333 \
--timeout=60 \
--min-instances=0 \
--max-instances=5 \
--trigger-http

```  

References:  
[GCP Regions](https://cloud.google.com/functions/docs/locations#tier_1_pricing)  
[GCP Deploy Functions](https://cloud.google.com/functions/docs/tutorials/http#deploying_the_function)
[Python Runtimes](https://cloud.google.com/functions/docs/concepts/execution-environment#python)