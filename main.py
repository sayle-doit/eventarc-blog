import os
import re

from flask import Flask, request
from google.cloud import bigquery


app = Flask(__name__)


@app.route("/", methods=["POST"])
def entry():
    # The ce-Resourcename value will be something like this: projects/_/buckets/sayle-eventarc/objects/test_file.txt
    resource_name = request.headers.get('ce-Resourcename')
    bucket = os.environ.get('BUCKET')

    if bucket is None:
        return ("Error the BUCKET environment variable is not set for this instance", 500)

    # This regex just extracts the bucket name and file path from the resource name
    regex = re.compile(f'^projects\/_\/buckets\/{bucket}\/objects\/([\S]+)')
    matches = regex.findall(resource_name)

    # If there isn't a match then exit out gracefully
    if matches is None or len(matches) == 0:
        return ("Created file doesn't match pattern", 200)

    path = matches[0]
    filename, extension = os.path.splitext(path)

    # Check if the file is a CSV or not
    if extension != '.csv':
        print("Warning: File uploaded is not a CSV so not loading into BigQuery.")
        return ("Created file isn't a CSV", 200)

    # Load the file into BigQuery
    client = bigquery.Client()
    uri = f"gs://{bucket}/{path}"
    table = os.environ.get("BIGQUERY_TABLE")

    # If the user has not set the environment variable for the table then error out
    if table is None:
        print("Error: Table env variable not set, so returning.")
        return ("Error BIGQUERY_TABLE environment variable is not set.", 500)

    # Setup and perform the load
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.CSV,
        autodetect=True,
    )
    load_job = client.load_table_from_uri(uri, table, job_config=job_config)

    # Run the job synchronously
    result = load_job.result()

    return (f"Loaded file located at {uri} into BQ table {table}", 200)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
