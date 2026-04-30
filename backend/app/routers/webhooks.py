from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.stripe import construct_webhook_event, get_stripe_client
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.models import ProjectCustomer, ProjectCustomerAddress, ProjectOrder, ProjectOrderItem, ProjectProduct, Subscription, User
from sqlmodel import select
from datetime import datetime
import json
from app.models import Vendor

webhooks_router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe_client = get_stripe_client()

@webhooks_router.post("/stripe")
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
        subscription_data = event['data']['object'].to_dict()
        await handle_subscription_updated(subscription_data, db)
    elif event['type'] == 'customer.subscription.deleted':
        subscription_data = event['data']['object'].to_dict()
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
    elif event['type'] == 'checkout.session.completed':
        session_data = event['data']['object'].to_dict()
        await handle_checkout_session_completed(session_data, db)
    else:
        pass
    return {"status": "success"}

async def handle_account_updated(account_data, db: Session):
    # Stripe Connect account id
    stripe_connect_id = account_data['id']
    payouts_enabled = account_data.payouts_enabled if hasattr(account_data, 'payouts_enabled') else False

    # Find the vendor with this Stripe Connect ID
    vendor = db.execute(select(Vendor).where(Vendor.stripe_connect_id == stripe_connect_id)).scalar_one_or_none()
    if vendor:
        # If payouts are enabled, allow vendor to accept products
        if payouts_enabled:
            vendor.payouts_enabled = True
            db.commit()

            
async def handle_subscription_created(subscription_data, db: Session):

    print(subscription_data)

    stripe_sub_id = subscription_data['id']
    user_stripe_id = subscription_data['customer']
    status = subscription_data.get('status', '').upper()
    

    items = subscription_data.get('items', {}).get('data', [])
    first_item = items[0] if items else {}

    current_period_start_ts = (
        first_item.get('current_period_start') or 
        subscription_data.get('current_period_start') or 
        subscription_data.get('created')
    )

    current_period_end_ts = (
        first_item.get('current_period_end') or 
        subscription_data.get('current_period_end')
    )

    current_period_start = datetime.fromtimestamp(current_period_start_ts) if current_period_start_ts else None
    current_period_end = datetime.fromtimestamp(current_period_end_ts) if current_period_end_ts else None

    # Find the user by their Stripe customer ID
    user = db.execute(select(User).where(User.stripe_customer_id == user_stripe_id)).scalar_one_or_none()
    if not user:
        return  # Or log an error

    # Check if subscription already exists
    existing = db.execute(select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)).scalar_one_or_none()
    if not existing:
        print(f"Creating subscription for user {user.id} with Stripe subscription ID {stripe_sub_id}")
        subscription = Subscription(
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



async def handle_checkout_session_completed(session_data: dict, db: Session):
    if session_data.get('mode') == 'subscription':
        # For subscriptions, don't create an order - subscription is handled separately
        return {"status": "subscription handled"}
    
    session_id = session_data.get('id')
    meta = session_data.get('metadata', {})
    project_id = meta.get('project_id')

    # 1. Create the parent Order record
    order = ProjectOrder(
        project=project_id,
        stripe_id=session_id,
        amount_total=session_data['amount_total'],
        payment_status=True,
        platform_fee_cents=round(session_data['amount_total'] * 0.07),
        vendor_amount_cents=session_data['amount_total'] - round(session_data['amount_total'] * 0.07),
        shipping_price_cents=meta.get('shipping_price_cents', 0)
    )
    db.add(order)
    # Flush ensures the order gets an ID from the DB before we create items
    db.flush() 

    # 2. Retrieve the full list of items from Stripe
    # This includes the products and the "Shipping" line item
    items = meta.get("product_ids", "").split(",")
    quantities = meta.get("quantities", "").split(",")
    # 3. Create OrderItems for each product
    
    for i, item in enumerate(items):
        # We skip the "Shipping" line item for the OrderItems table 
        # since shipping is already tracked in the parent order amount
        product = db.execute(select(ProjectProduct).where(ProjectProduct.id == int(item))).scalar_one_or_none()
            
        # Retrieve the internal product ID from the price metadata
        # (Assuming you passed it in 'price_data' during session creation)
        

        new_order_item = ProjectOrderItem(
            order=order.id,
            item=int(product.id),
            quantity=int(quantities[i]),
            price_at_purchase=product.sale_price,
            shipping_status="PENDING" # Using string if Enum isn't imported
        )
        db.add(new_order_item)

    # 4. Commit all changes at once
    db.flush()
    db.refresh(order)
    

    customer = json.loads(meta.get("customer", "{}"))
    db_customer = ProjectCustomer(
        order=order.id,
        first_name=customer.get("first_name", ""),
        last_name=customer.get("last_name", ""),
        email=customer.get("email", ""),
        phone=customer.get("phone", "")
    )
    db.add(db_customer)
    db.flush()
    db.refresh(db_customer)

    address = json.loads(meta.get("customer", "{}"))
    db_address = ProjectCustomerAddress(
        customer=db_customer.id,
        house_number=address.get("house_number", ""),
        street_name=address.get("street_name", ""),
        city=address.get("city", ""),
        state=address.get("state", ""),
        postal_code=address.get("postal_code", "")
    )
    db.add(db_address)
    db.commit()

    pass