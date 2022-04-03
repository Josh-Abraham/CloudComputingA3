from flask import Blueprint, render_template, request
from utils import *

image_routes = Blueprint("image_routes", __name__)

@image_routes.route('/add_image', methods = ['GET','POST'])
def add_key():
    """Add an image
    GET: Simply render the add_key page
    POST: Pass in key from form to add to DB and file system
    """
    if request.method == 'POST':
        key = request.form.get('key')
        status = upload_image(request, key)
        if status == "OK":
            # Call classification EC2 instance
            classification = None
            status = write_dynamo(key, classification)
        return render_template("add_image.html", save_status=status)
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
                if not prediction == None:
                    # Image and Prediction Found
                    return render_template("show_image.html", image=image, prediction=prediction)
                # Image Found
                return render_template("show_image.html", image=image)
        # No Key -> Returns Not Found 
        return render_template("show_image.html", status=404)
    return render_template("show_image.html")