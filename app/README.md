# Flask Folder & Files Structure

```commandline
backend/               # Flask Backend
│── app/               # Main Application Folder
│   ├── models/        # Database Models
│   │   ├── user.py
│   │   ├── __init__.py
│   ├── routes/        # Routes
│   │   ├── user_routes.py
│   │   ├── __init__.py
│   ├── services/      # Business Logic (Handlers)
│   │   ├── user_service.py
│   │   ├── __init__.py
│   ├── config.py      # Configuration File
│   ├── extensions.py  # Extensions (DB, CORS, etc.)
│   ├── __init__.py    # App Initialization
│── migrations/        # Flask-Migrate folder
│── .venv/              # Virtual Environment
│── .env               # Environment Variables
│── requirements.txt   # Dependencies
│── run.py             # Entry point for the app
│
```

## Install Dependencies

Run the following command inside the backend/ directory:

```commandline
pip install flask flask_cors flask_sqlalchemy flask_mysqldb flask-migrate python-dotenv PYJWT
```

### 1. models/ (Database Models)

`
models/user.py
`

```python
from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}
```

`
models/auth.py
`

```python
from app.extensions import db


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
```

### 2. routes/ (API Routes)

`routes/user_routes.py`

```python
from flask import Blueprint, request, jsonify
from app.services.user_service import get_all_users, create_user

user_bp = Blueprint("user", __name__)


@user_bp.route("/users", methods=["GET"])
def get_users():
    return jsonify(get_all_users())


@user_bp.route("/users", methods=["POST"])
def add_user():
    data = request.json
    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and Email are required"}), 400
    user = create_user(data["name"], data["email"])
    return jsonify(user), 201
```

`routes/auth_routes.py`

```python
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    return register_user(data)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    return login_user(data)
```

### services/ (Business Logic - Handlers)

`services/user_service.py`

```python
from app.models.user import User
from app.extensions import db


def get_all_users():
    return [user.to_dict() for user in User.query.all()]


def create_user(name, email):
    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()
    return user.to_dict()
```

`services/auth_service.py`

```python
from flask import jsonify
from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


def register_user(data):
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and Password required"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(name=data["name"], email=data["email"], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201


def login_user(data):
    user = User.query.filter_by(email=data["email"]).first()
    if user and check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"error": "Invalid credentials"}), 401
```

### 4. config.py (Configuration File)

`config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
```

### 5. extensions.py (Flask Extensions)
`extensions.py`

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
```

### 6. __init__.py (App Initialization)
`__init__.py`

```python
from flask import Flask
from app.config import Config
from app.extensions import db, migrate, cors
from app.routes.user_routes import user_bp
from app.routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app
```

### Initialize Migration (use only one time for each flask app.)
```commandline
flask db init
```

### Create Migration Script
```commandline
flask db migrate -m "Initial migration"
```

### Apply Migrations (Create Tables)
```commandline
flask db upgrade
```

### Add More Models (Future Changes)
```commandline
flask db migrate -m "Added new table/columns"
flask db upgrade
```

### run flask app with debug mode.

```commandline
flask run --debug
```