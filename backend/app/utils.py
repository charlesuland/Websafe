# crud.py or utils.py
from sqlalchemy.orm import Session
from app.models import Subscription

def is_subscription_active(db: Session, user_id: int) -> bool:
    """
    Queries the database for at least one active subscription record for the user.
    """
    active_sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "ACTIVE"
    ).first()
    
    return active_sub is not None