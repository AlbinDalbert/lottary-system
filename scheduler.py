# scheduler.py

import random
from datetime import datetime
from sqlalchemy import extract
from app import app, db
from models import Registration, Winner

def select_winner(app):
    """
    Selects a random winner from the registrations of the current month.
    """
    with app.app_context():
        now = datetime.now()
        current_month = now.month
        current_year = now.year

        participants = Registration.query.filter(
            extract('month', Registration.timestamp) == current_month,
            extract('year', Registration.timestamp) == current_year
        ).all()

        if not participants:
            print("No valid participants found for this month.")
            return

        winner_registration = random.choice(participants)

        winner = Winner(registration_id=winner_registration.id)
        db.session.add(winner)
        db.session.commit()

        print(f"🎉 Winner selected! Congratulations to {winner_registration.name} ({winner_registration.email})!")

if __name__ == '__main__':
    select_winner()
