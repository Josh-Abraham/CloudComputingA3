from flask import Blueprint, render_template, request
from utils import *
import json, time

image_routes = Blueprint("image_routes", __name__)


@image_routes.route('/add_image', methods = ['GET','POST'])
def add_key():
    """Add an image
    GET: Simply render the add_key page
    POST: Pass in key from form to add to DB and file system
    """
    global EC2_RUN_IP
    EC2_RUN_IP = get_ec2_ip()
    if request.method == 'POST':
        key = request.form.get('key')
        status = upload_image(request, key)
        classification = None
        if status == "OK":
            # Call classification EC2 instance
            if not EC2_RUN_IP == None:
                jsonReq = {'key': key}
                try:
                    classification_resp = requests.get('http://' + EC2_RUN_IP + ':5000/get_classification', json=jsonReq)
                    classification = json.loads(classification_resp.content.decode('utf-8'))
                    print(classification)
                except:
                    print("Flask not running")
            status = write_dynamo(key, classification)
        return render_template("add_image.html", save_status=status, classification=classification)
    return render_template("add_image.html")


@image_routes.route('/show_image', methods = ['GET', 'POST'])
def show_image():
    """Show an image
    GET: Simply render the show_image page
    POST: Search for a given key
    """
    if request.method == 'POST':
        key = request.form.get('key')
        resp = read_dynamo(key)
        if not resp == None:
            image = download_image(key)
            if not image == None:
                prediction = resp['predicted_label']
                if not prediction == "None":
                    # Image and Prediction Found
                    return render_template("show_image.html", image=image, prediction=prediction)
                # Image Found
                return render_template("show_image.html", image=image)
        # No Key -> Returns Not Found 
        return render_template("show_image.html", status=404)
    return render_template("show_image.html")

@image_routes.route('/show_category', methods = ['GET', 'POST'])
def show_category():
    """Show all images
    GET: Simply render the show_image page
    POST: Search for a given key
    """
    if request.method == 'POST':
        category = request.form.get("submit")
        images = read_category(category)
        if len(images[0]) == 0:
             return render_template("show_category.html", status=404)
        return render_template("show_category.html", images=images)
    return render_template("show_category.html")


@image_routes.route('/list_images')
def list_images():
    """ Get list of all keys currently in the database
    """
    image_list = read_all()
    total=len(image_list)

    if not image_list == None:
        return render_template('list_images.html', image_list=image_list, total=total)
    else:
        return render_template('list_images.html')

EC2_RUN_IP = get_ec2_ip()