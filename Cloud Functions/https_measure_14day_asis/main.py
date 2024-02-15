############### MANAGED BY GOOGLE ####################
from flask import Flask, request
from markupsafe import escape
from google.cloud import bigquery
import pandas

app = Flask("google_managed")

@app.route('/my_function', methods=['GET', 'POST'])
def https_measure_14day_asis(request):
    return my_function(request)
############### MANAGED AND PROVIDED BY YOU ####################
def my_function(request):

    #### Enabling CORS
    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return ("", 204, headers)

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}
    #### Enabling CORS

    client = bigquery.Client()
    query_job = client.query(
        """
        SELECT  
          CAST(DATETIME(time, "Europe/Vatican")AS STRING FORMAT 'YYYY-MM-DD HH24:MI:SS') AS local_time,
          type,
          `measurementValue`
        FROM (
            SELECT 
              *,
              row_number() over (partition by type order by time desc) as seqnum
            FROM `weather-station-ef6ca.weather_measures.measures`
              ) AS t
        WHERE seqnum <= 1632
        """
    )

    results = query_job.result()  # Waits for job to complete.

    df = results.to_dataframe()
    json_obj = df.to_json(orient='records', lines = False) # values, records

    return(json_obj, 200, headers)

# https://medium.com/google-cloud/use-multiple-paths-in-cloud-functions-python-and-flask-fc6780e560d3
# https://cloud.google.com/functions/docs/bestpractices/tips
