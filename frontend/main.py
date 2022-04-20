from flask import Flask, render_template, redirect
from routes import image_routes

# Flask Blueprint Setup
webapp = Flask(__name__)
webapp.register_blueprint(image_routes)

@webapp.route('/')
@webapp.route('/home')
def home():
    """ Main route, as well as default location for 404s
    """
    return render_template("home.html")

@webapp.route('/manager_app')
def manager_app():
    return redirect("https://test-signup.auth.us-east-1.amazoncognito.com/login?response_type=code&client_id=270vq2m5ni8n4rrn4isp8tdl34&redirect_uri=https://jqifn5vnq8.execute-api.us-east-1.amazonaws.com/dev")
