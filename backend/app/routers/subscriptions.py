from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import Subscription, Plan, User
from app.schemas import SubscriptionCreate, SubscriptionOut, PlanOut
from app.stripe import create_customer, create_subscription as stripe_create_subscription
from sqlmodel import select
from datetime import datetime, timedelta
from typing import List

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


@router.get("/", response_model=List[SubscriptionOut])
async def get_all_subscriptions(db: Session = Depends(get_db)):
    subscriptions = db.execute(select(Subscription)).scalars().all()
    return subscriptions


@router.put("/{subscription_id}", response_model=SubscriptionOut)
async def update_subscription(subscription_id: int, status: str, db: Session = Depends(get_db)):
    subscription = db.execute(select(Subscription).where(Subscription.id == subscription_id)).scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Update status
    subscription.status = status
    if status == "CANCELED":
        subscription.canceled_at = datetime.utcnow()

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

