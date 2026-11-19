from flask import Flask
from app.routes.activities import activities_bp

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Registramos el blueprint
    app.register_blueprint(activities_bp)
    
    return app