import os, requests, base64
from access_key import aws_config
import boto3
from botocore.config import Config
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
S3_BUCKET = "image-bucket-a3"
my_config = Config(
    region_name = 'us-east-1',
    #signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

s3=boto3.client('s3', config=my_config, aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])
dynamodb = boto3.resource('dynamodb', aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])
image_store = dynamodb.Table('image_store')

def upload_image(request, key):
    img_url = request.form.get('img_url')
    if img_url == "":
        file = request.files['file']
        _, extension = os.path.splitext(file.filename)
        if extension.lower() in ALLOWED_EXTENSIONS:
            try:
                print("trying")
                base64_image = base64.b64encode(file.read())

                s3.put_object(Body=base64_image,Key=key,Bucket="image-bucket-a3",ContentType='image')
                print("uploaded")
                return "OK"
            except:
                return "INVALID"
            # return "SAVED"
        return "INVALID"

    response = requests.get(img_url)
    if response.status_code == 200:
        _, extension = os.path.splitext(img_url)
        if extension.lower() in ALLOWED_EXTENSIONS:
            filename = key + extension
            base64_image = base64.b64encode(response.content)
            s3.put_object(Body=base64_image,Key=key,Bucket=S3_BUCKET,ContentType='image')
            return "OK"
    return "INVALID"

def download_image(key):
    try:
        return s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read().decode('utf-8')
    except:
        return None


def write_dynamo(key, classification=None):
    response = image_store.put_item(
       Item={
            'image_key': key,
            'label': None,
            'predicted_label': classification,
        }
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return "OK"
    return "FAILURE"


def read_dynamo(key):
    try:
        if not key == "":
            response = image_store.get_item(
            Key={
                    'image_key' : key,
                }
            )

            if 'Item' in response:
                return response['Item']
        return None
    except:
        return None