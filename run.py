from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from apps.config import Config
from apps.auth import blueprint as auth_blueprint
from apps.home import blueprint as home_blueprint

# Initialize the app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize MongoDB
mongo = PyMongo(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(home_blueprint)

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
