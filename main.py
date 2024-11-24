from models import db  # Import the SQLAlchemy database instance
from controllers import setup_routes  # Import the setup_routes function to register all the routes
from app import create_app

# Function to create and configure the Flask app
def Initialize_app():
    # Instantiate a Flask application object
    app = create_app()
        
    db.init_app(app)

    # Register database tables by creating all models
    with app.app_context():
        db.create_all()  # Creates tables for all defined models in the database if they do not already exist

    # Register the routes defined in the controllers module
    # The `setup_routes` function is responsible for registering all necessary routes with the app instance
    setup_routes(app, db)

    # Return the configured Flask app object
    return app

# Main entry point of the application
if __name__ == "__main__":
    # Create the app by calling `create_app` and run it with debugging enabled
    app = Initialize_app()
    app.run(debug=True)
