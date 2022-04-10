import os, requests, base64
from access_key import aws_config
import boto3
from botocore.config import Config
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
S3_BUCKET = "image-bucket-a3"
EC2_RUN_ID = "i-0a69fa48a7f17be89"

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
ec2 = boto3.client('ec2', config=my_config, aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])

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


def write_dynamo(key, classification):
    response = image_store.put_item(
       Item={
            'image_key': key,
            'label': None,
            'predicted_label': classification,
            'trained': False
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

def read_category(category):
    try:
        response = image_store.scan()
        images = [[]]
        i = 0
        j = 0
        for item in response['Items']:
            if item['predicted_label'] == category:
                images[i].append(download_image(item['image_key']))
                j += 1
                if j % 3 == 0:
                    images.append([])
                    i += 1
                    j = 0
        return images
    except:
        return None

def read_all():
    try:
        response = image_store.scan()
        image_list = []
        i = 1
        for item in response['Items']:
            image_list.append(
                {
                    'index': i,
                    'key': item['image_key'],
                    'label': item['label'],
                    'predicted_label': item['predicted_label']
                })
            i += 1
           
        return image_list
    except:
        return None

def get_ec2_ip():
    global EC2_RUN_ID
    
    response = ec2.describe_instances(InstanceIds=[EC2_RUN_ID], DryRun=False)
    print(response)
    inst_name = response['Reservations'][0]['Instances'][0]['State']['Name']
    ec2_ip = None       
    if (inst_name == 'running'):
        ec2_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(ec2_ip)
    return ec2_ip