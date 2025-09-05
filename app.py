from flask import Flask, request, jsonify
from models import db, Registration, Winner
from utils import log_action, is_duplicate_email_this_month
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok", "message": "App is running"}), 200

@app.route('/registrations', methods=['GET'])
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

@app.route('/register', methods=['POST'])
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


if __name__ == '__main__':
    app.run(debug=True)
