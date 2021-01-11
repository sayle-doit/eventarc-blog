# Sayle's Eventarc Medium Article Code

This is the codebase to be used with the Medium article located at: <TODO add the URL here>

## Notes
This code is intended to be a proof-of-concept and show you how to use Cloud Run and Eventarc. It is not intended to be run in a production environment as-is as many best practices around running it are outside the scope of the article subject.

## gcloud commands
Below is a very concise set of the gcloud commands used in the blog to get the system up and running. I have added comments to each value in here to explain what they are for easier understanding.

Setting Environment variables:
```
# Cloud Build Tag Name
TAG_NAME=<tag>
# Cloud Run Service Name
CLOUD_RUN_SERVICE=<service name>
# Region to run Cloud Run Service in
CLOUD_RUN_REGION=<region>
# Eventarc Trigger Name
TRIGGER_NAME=<trigger name>
# Region (or global) to run Eventarc trigger in (value will be either a region or the value "global")
TRIGGER_LOCATON=<global or region>
# Google Cloud Storage Bucket Name
BUCKET_NAME=<bucket name>
# BigQuery Output Table Name (must be full table name in format "project.dataset.table")
BQ_TABLE=<BigQuery full table name>

# These two use the above variables to build additional environment variables
# Project Name
PROJECT=$(gcloud config get-value project)
# Container Image Name
IMAGE=gcr.io/"$PROJECT"/"$TAG_NAME":latest
```

Create the service:
```
gcloud run deploy $CLOUD_RUN_SERVICE \
  --region="$CLOUD_RUN_REGION"
  --tag "$IMAGE" \
  --platform managed \
  --set-env-vars=BUCKET="$BUCKET",BIGQUERY_TABLE="$BQ_TABLE"
```

Create the Eventarc trigger:
```
gcloud beta eventarc triggers create "$TRIGGER_NAME" \
  --location="$TRIGGER_LOCATON" \
  --destination-run-service "$CLOUD_RUN_SERVICE"  \
  --matching-criteria type=google.cloud.audit.log.v1.written \
  --matching-criteria methodName=storage.objects.create \
  --matching-criteria serviceName=storage.googleapis.com
```

Future usage of the above once per-resource triggering functionality is added:
```
gcloud beta eventarc triggers create "$TRIGGER_NAME" \
  --location="$LOCATION" \
  --destination-run-service "$CLOUD_RUN_SERVICE"  \
  --matching-criteria type=google.cloud.audit.log.v1.written \
  --matching-criteria methodName=storage.objects.create \
  --matching-criteria serviceName=storage.googleapis.com \
  --matching-criteria resourceName=projects/_/buckets/"$BUCKET_NAME"
```
