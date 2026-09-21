# script for investigating met office AWS data

import boto3 # may need to set up aws credentials?
from botocore import UNSIGNED
from botocore.config import Config


BUCKET_NAME = "met-office-land-observations-data"
# ^ most important bit is the bucket name, which is public and can be found in the met office docs

s3 = boto3.client(
    "s3",
    region_name="eu-west-2",
    config=Config(signature_version=UNSIGNED), # no authentication, public. otherwise boto3 expects aws creds
)

response = s3.list_objects_v2(
    Bucket=BUCKET_NAME,
    MaxKeys=20, # only show 20 items for now
)

for item in response.get("Contents", []):
    print(item["Key"])