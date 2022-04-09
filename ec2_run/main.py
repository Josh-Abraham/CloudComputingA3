from flask import Flask, request
import tensorflow as tf
import boto3, time, base64, json, threading
from botocore.config import Config
from tensorflow.python.keras.models import load_model
from PIL import Image
from numpy import asarray


S3_BUCKET = "image-bucket-a3"
webapp = Flask(__name__)

my_config = Config(
    region_name = 'us-east-1',
    #signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

s3=boto3.client('s3', config=my_config, aws_access_key_id='AKIA3U4U6D42PLQZVFOX', aws_secret_access_key='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')


@webapp.route('/', methods = ['GET'])
def main():
    return get_response(True)

@webapp.route('/get_classification', methods = ['GET'])
def get_classification():
    global model
    data = request.get_json(force = True)
    key = data['key']
    base64_image = download_image(key)
    with open("image.png", "wb") as fh:
        fh.write(base64.decodebytes(base64_image))
    image = Image.open('image.png')
    image.load() # required for png.split()

    # For RGBA
    if len(image.split()) == 4:
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3]) # 3 is the alpha channel
        image = background

    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_tf = tf.image.resize_with_pad(image_array, 200, 200) / 255
    
    image_tf = tf.reshape(image_tf, [1, 200, 200, 3])
    pred = model(image_tf)    
    pred = asarray(pred)[0][0]
    value = "Cat"
    if pred > 0.5:
        value = "Dog"

    response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
    
    return response

def download_image(key):
    try:
        return s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read()
    except:
        return None


def get_response(input=False):
    if input:
        response = webapp.response_class(
            response=json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Bad Request"),
            status=400,
            mimetype='application/json'
        )

    return response

def load_s3_model():
    # TODO: Get most recent model
    s3.download_file('ece1779model', 'vgg_new.h5', 'vgg_new.h5')

    vgg_loaded = load_model('vgg_new.h5')
    return vgg_loaded


def read_model_metrics():
    s3.download_file('ece1779model', 'vgg_stats.json', 'vgg_stats.json')
    with open('vgg_stats.json') as json_file:
        data = json.load(json_file)
    
    return data

#### Thread BG Call
def thread_model_check():
    global MODEL_METRICS, model
    old_key = MODEL_METRICS['key']
    while True:
        print('Check Model State')
        data = read_model_metrics()
        new_key = data['key']
        if not new_key == old_key:
            print('New Model')
            model = load_s3_model()
            MODEL_METRICS = data
            
        time.sleep(60)


MODEL_METRICS = read_model_metrics()
model = load_s3_model()
th = threading.Thread(target=thread_model_check)
th.start()