# Cloud Function: `new_https_funct`  

Deploy with the following command. This assumes the shell is in the current directory of the source files.  

```
gcloud functions deploy flask_function --gen2 --region=us-east1 --runtime=python312 --source=.flask_function --entry-point=common_cloud_functions_function --trigger-http
```  

Running the previous command prompts with the question if you want to allow unauthenticated invocations of the new function.

References:  
[GCP Regions](https://cloud.google.com/functions/docs/locations#tier_1_pricing)  
[Python Runtimes](https://cloud.google.com/functions/docs/concepts/execution-environment#python)