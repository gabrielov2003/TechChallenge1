from flask import Flask
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from infrastructure import Infrastructure
from web import api
import os


def create_app():
    app = Flask(__name__)
    app.config['SWAGGER'] = {
        'title': 'API Oficina',
        'uiversion': 3
    }
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fiap-soat-key')

    JWTManager(app)
    Swagger(app)

    Infrastructure.init_db()

    app.register_blueprint(api, url_prefix='/api')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)