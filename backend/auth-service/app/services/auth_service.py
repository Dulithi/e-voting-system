"""
Business logic helpers for auth service
"""
from sqlalchemy.orm import Session
from app.models.user import User
from datetime import datetime


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def mark_user_login(db: Session, user: User):
    user.last_login_at = datetime.utcnow()
    db.commit()
