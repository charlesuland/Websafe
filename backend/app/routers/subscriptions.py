from fastapi import APIRouter, HTTPException, status, Depends
from app.utils import is_subscription_active
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models import Subscription, Plan, User
from app.schemas import SubscriptionCreate, SubscriptionOut, PlanOut
from app.stripe import create_customer, create_subscription as stripe_create_subscription, get_stripe_client
from sqlmodel import select
from datetime import datetime, timedelta
from typing import List

stripe_client = get_stripe_client()

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/", response_model=SubscriptionOut)
async def create_subscription(subscription_in: SubscriptionCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.execute(select(User).where(User.id == subscription_in.user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if plan exists
    plan = db.execute(select(Plan).where(Plan.id == subscription_in.plan_id)).scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if not plan.stripe_plan_id:
        raise HTTPException(status_code=400, detail="Plan not configured with Stripe")

    # Create Stripe customer if user doesn't have one
    if not user.stripe_customer_id:
        stripe_customer = create_customer(user.email, user.username or user.email)
        user.stripe_customer_id = stripe_customer.id
        db.commit()

    # Create Stripe subscription
    stripe_sub = stripe_create_subscription(user.stripe_customer_id, plan.stripe_plan_id)

    # Create local subscription
    current_time = datetime.utcnow()
    if plan.duration == "MONTHLY":
        period_end = current_time + timedelta(days=30)
    else:  # YEARLY
        period_end = current_time + timedelta(days=365)

    subscription = Subscription(
        plan_id=subscription_in.plan_id,
        user_id=subscription_in.user_id,
        current_period_start=current_time,
        current_period_end=period_end,
        stripe_subscription_id=stripe_sub.id,
        meta={}
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


@router.get("/plans", response_model=List[PlanOut])
async def get_plans(db: Session = Depends(get_db)):
    plans = db.execute(select(Plan)).scalars().all()
    return plans


@router.get("/user/{user_id}", response_model=List[SubscriptionOut])
async def get_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    subscriptions = db.execute(select(Subscription).where(Subscription.user_id == user_id)).scalars().all()
    return subscriptions

@router.get("/me")
async def get_my_subscriptions(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return is_subscription_active(db, user.id)

@router.put("/{subscription_id}", response_model=SubscriptionOut)
async def update_subscription(subscription_id: int, status: str, db: Session = Depends(get_db)):
    subscription = db.execute(select(Subscription).where(Subscription.id == subscription_id)).scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if status.upper() == "CANCELED" and subscription.stripe_subscription_id:
        # Cancel in Stripe
        stripe_client.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        subscription.status = "CANCELED"
        subscription.canceled_at = datetime.utcnow()
    else:
        subscription.status = status.upper()

    db.commit()
    db.refresh(subscription)
    return subscription


@router.delete("/{subscription_id}")
async def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.execute(select(Subscription).where(Subscription.id == subscription_id)).scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    db.delete(subscription)
    db.commit()
    return {"message": "Subscription deleted"}


