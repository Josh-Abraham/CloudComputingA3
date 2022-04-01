from flask import Blueprint, render_template, request
from image_utils import upload_image

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
        return render_template("add_image.html")
    return render_template("add_image.html")