from datetime import datetime
from sqlalchemy import extract
from models import db, Log, Registration

def log_action(action, details=None):
    log = Log(action=action, details=details)
    db.session.add(log)
    db.session.commit()

def is_duplicate_email_this_month(email):
    now = datetime.utcnow()
    return db.session.query(Registration).filter(
        Registration.email == email,
        extract('month', Registration.timestamp) == now.month,
        extract('year', Registration.timestamp) == now.year
    ).first() is not None