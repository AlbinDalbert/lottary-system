from datetime import datetime
from sqlalchemy import extract
from models import db, Log, Registration

def log_action(action, details=None):
    log = Log(action=action, details=details)
    db.session.add(log)
    db.session.commit()

def iiis_duplicate_email_this_month(email):
    now = datetime.now()
    return db.session.query(Registration).filter(
        Registration.email == email,
        extract('month', Registration.timestamp) == now.month,
        extract('year', Registration.timestamp) == now.year
    ).first() is not None



def is_duplicate_email_this_month(email):
    now = datetime.now()
    print(f"Checking for email: {email}")
    print(f"Current month/year: {now.month}/{now.year}")
    
    all_regs = db.session.query(Registration).all()
    print(f"All registrations in DB: {[(r.email, r.timestamp) for r in all_regs]}")
    
    result = db.session.query(Registration).filter(
        Registration.email == email,
        extract('month', Registration.timestamp) == now.month,
        extract('year', Registration.timestamp) == now.year
    ).first()
    
    print(f"Filtered result: {result}")
    return result is not None


def iis_duplicate_email_this_month(email):
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    if now.month == 12:
        start_of_next_month = datetime(now.year + 1, 1, 1)
    else:
        start_of_next_month = datetime(now.year, now.month + 1, 1)
    
    return db.session.query(Registration).filter(
        Registration.email == email,
        Registration.timestamp >= start_of_month,
        Registration.timestamp < start_of_next_month
    ).first() is not None
