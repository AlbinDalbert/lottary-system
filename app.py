from flask import Flask, request, jsonify
from models import db, Registration, Winner
from utils import log_action, is_duplicate_email_this_month
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        log_action("register_failed", "Missing name or email")
        return jsonify({"error": "Name and email are required"}), 400

    if is_duplicate_email_this_month(email):
        log_action("register_failed", f"Duplicate email: {email}")
        return jsonify({"error": "Email already registered this month"}), 400

    registration = Registration(name=name, email=email)
    db.session.add(registration)
    db.session.commit()
    log_action("register_success", f"{name} <{email}>")
    return jsonify({"message": "Registration successful"}), 201

if __name__ == '__main__':
    app.run(debug=True)