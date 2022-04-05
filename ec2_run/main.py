from flask import Flask, render_template
import json

webapp = Flask(__name__)

# TODO:
# Create a model and store on S3
# Load model from S3 on startup
# Create an endpoint to load new model (will be called from ec2_train)

@webapp.route('/', methods = ['GET'])
def main():
    return get_response(True)

@webapp.route('/get_classification', methods = ['GET'])
def get_classification():
    response = webapp.response_class(
            response=json.dumps("Dog"),
            status=200,
            mimetype='application/json'
        )
    
    return response

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