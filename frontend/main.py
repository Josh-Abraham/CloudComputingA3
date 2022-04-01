from flask import Flask, render_template
from classify_image import image_routes

# Flask Blueprint Setup
webapp = Flask(__name__)
webapp.register_blueprint(image_routes)

@webapp.route('/')
@webapp.route('/home')
def home():
    """ Main route, as well as default location for 404s
    """
    return render_template("home.html")