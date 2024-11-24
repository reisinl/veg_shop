from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    # Set up database URI - Configures the database URL for SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root2024@localhost/vegetable_shop'
    
    # Disable SQLALCHEMY_TRACK_MODIFICATIONS to save resources and avoid warnings
    # This setting is used to disable the event notifications feature, which is not needed here
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Generate a secret key for the app, which is necessary for session management
    # The key is generated randomly each time the application runs
    app.secret_key = os.urandom(24)

    return app
