from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost:5432/drone_database"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ajoutez d'autres configurations si nécessaire

    db.init_app(app)

    # Importez les routes et les modèles ici

    return app