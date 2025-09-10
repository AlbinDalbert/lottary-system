from flask import Flask, request, jsonify, Blueprint
from models import db, Registration, Winner, Log
from utils import log_action, is_duplicate_email_this_month
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__, instance_relative_config=False, instance_path='/data')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

main_bp = Blueprint('main', __name__)

db.init_app(app)

@main_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok", "message": "App is running"}), 200

@main_bp.route('/registrations', methods=['GET'])
def get_registrations():
    """Returns a JSON list of all registrations in the database."""
    registrations = Registration.query.all()
    
    output = []
    for reg in registrations:
        reg_data = {
            'id': reg.id,
            'name': reg.name,
            'email': reg.email,
            'timestamp': reg.timestamp.isoformat()  # .isoformat() is a standard way to format dates in APIs
        }
        output.append(reg_data)
        
    return jsonify(output)

@main_bp.route('/winners', methods=['GET'])
def get_winners():
    """Returns a JSON list of all winners in the database."""

    query = db.session.query(
        Winner.id,
        Winner.selected_at,
        Registration.name,
        Registration.email
    ).join(Registration, Winner.registration_id == Registration.id).order_by(Winner.selected_at.desc())

    winners = query.all()

    output = []
    for win in winners:
        win_data = {
            'winner_id': win.id,
            'name': win.name,
            'email': win.email,
            'selected_at': win.selected_at.isoformat()
        }
        output.append(win_data)
        
    return jsonify(output)

@main_bp.route('/logs', methods=['GET'])
def get_logs():
    """Return logs in the database."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    if per_page == 0:
        logs = Log.query.order_by(Log.timestamp.desc()).all()
    else:
        offset = (page - 1) * per_page
        logs = Log.query.order_by(Log.timestamp.desc()).limit(per_page).offset(offset).all()
    
    output = []
    for log in logs:
        log_data = {
            'id': log.id,
            'action': log.action,
            'details': log.details,
            'timestamp': log.timestamp.isoformat()
        }
        output.append(log_data)
        
    return jsonify(output)


@main_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    error, normalized_email = validate_input(name, email)

    if error:
        return error

    registration = Registration(name=name, email=normalized_email)
    db.session.add(registration)
    db.session.commit()
    log_action("register_success", f"{name} <{email}>")
    return jsonify({"message": "Registration successful"}), 201


def validate_input(name, email):
    if not name or not email:
        log_action("register_failed", "Missing name or email")
        error = jsonify({"error": "Name and email are required"}), 400
        return error, None

    try:
        valid = validate_email(email, check_deliverability=False) # disabled DNS check
        normalized_email = valid.normalized.lower()
    except EmailNotValidError as e:
        log_action("register_failed", f"Invalid email format: {email}")
        error = jsonify({"error": str(e)}), 400
        return error, None

    if is_duplicate_email_this_month(normalized_email):
        log_action("register_failed", f"Duplicate email: {email}")
        error = jsonify({"error": "Email already registered this month"}), 400
        return error, None

    return None, normalized_email

def create_app(config_override=None):
    """The application factory."""
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_override:
        app.config.update(config_override)

    db.init_app(app)

    app.register_blueprint(main_bp)

    return app

app = create_app()
