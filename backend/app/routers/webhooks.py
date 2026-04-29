from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.stripe import construct_webhook_event, get_stripe_client
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.models import Subscription, User
from sqlmodel import select
from datetime import datetime
import json

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe_client = get_stripe_client()

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = construct_webhook_event(payload, sig_header)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe_client.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'customer.subscription.created':
        subscription_data = event['data']['object'].to_dict()
        await handle_subscription_created(subscription_data, db)
    elif event['type'] == 'customer.subscription.updated':
        subscription_data = event['data']['object']
        await handle_subscription_updated(subscription_data, db)
    elif event['type'] == 'customer.subscription.deleted':
        subscription_data = event['data']['object']
        await handle_subscription_deleted(subscription_data, db)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice_data = event['data']['object'].to_dict()
        await handle_invoice_payment_succeeded(invoice_data, db)
    elif event['type'] == 'invoice.payment_failed':
        invoice_data = event['data']['object']
        await handle_invoice_payment_failed(invoice_data, db)
    elif event['type'] == 'account.updated':
        account_data = event['data']['object']
        await handle_account_updated(account_data, db)
    else:
        # Unexpected event type
        pass
from app.models import Vendor
async def handle_account_updated(account_data, db: Session):
    # Stripe Connect account id
    stripe_connect_id = account_data['id']
    payouts_enabled = account_data.get('payouts_enabled', False)

    # Find the vendor with this Stripe Connect ID
    vendor = db.execute(select(Vendor).where(Vendor.stripe_connect_id == stripe_connect_id)).scalar_one_or_none()
    if vendor:
        # If payouts are enabled, allow vendor to accept products
        if payouts_enabled:
            vendor.payouts_enabled = True
            db.commit()
async def handle_subscription_created(subscription_data, db: Session):
    stripe_sub_id = subscription_data['id']
    user_stripe_id = subscription_data['customer']
    status = subscription_data.get('status', '').upper()
    
    current_period_start_ts = subscription_data["items"]["data"][0].get('current_period_start')
    current_period_end_ts = subscription_data["items"]["data"][0].get('current_period_end')
    #plan_id = subscription_data['plan']['id'] if subscription_data.get('plan') else None

    current_period_start = datetime.fromtimestamp(current_period_start_ts) if current_period_start_ts else None
    current_period_end = datetime.fromtimestamp(current_period_end_ts) if current_period_end_ts else None

    # Find the user by their Stripe customer ID
    user = db.execute(select(User).where(User.stripe_customer_id == user_stripe_id)).scalar_one_or_none()
    if not user:
        return  # Or log an error

    # Check if subscription already exists
    existing = db.execute(select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)).scalar_one_or_none()
    if not existing:
        subscription = Subscription(
            #plan_id=None,  # Optionally map Stripe plan_id to your local plan
            user_id=user.id,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            stripe_subscription_id=stripe_sub_id,
            status=status,
            meta={},
        )
        db.add(subscription)
        db.commit()

    return {"status": "success"}

async def handle_subscription_updated(subscription_data, db: Session):
    stripe_sub_id = subscription_data['id']
    status = subscription_data['status']
    current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
    current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
    canceled_at = datetime.fromtimestamp(subscription_data['canceled_at']) if subscription_data.get('canceled_at') else None

    subscription = db.execute(select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)).scalar_one_or_none()
    if subscription:
        subscription.status = status.upper()
        subscription.current_period_start = current_period_start
        subscription.current_period_end = current_period_end
        if canceled_at:
            subscription.canceled_at = canceled_at
        db.commit()

async def handle_subscription_deleted(subscription_data, db: Session):
    stripe_sub_id = subscription_data['id']
    subscription = db.execute(select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)).scalar_one_or_none()
    if subscription:
        subscription.status = 'CANCELED'
        subscription.canceled_at = datetime.utcnow()
        db.commit()

async def handle_invoice_payment_succeeded(invoice_data, db: Session):
    # Could update subscription status or send notifications
    pass

async def handle_invoice_payment_failed(invoice_data, db: Session):
    # Handle failed payments, e.g., mark subscription as past_due
    subscription_id = invoice_data.get('subscription')
    if subscription_id:
        subscription = db.execute(select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)).scalar_one_or_none()
        if subscription:
            subscription.status = 'PAST_DUE'
            db.commit()