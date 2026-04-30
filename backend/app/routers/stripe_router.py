
import json

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from app.dependencies import get_current_active_user, get_current_user, get_db
from app.models import DraftProjectPage, Project, ProjectProduct, User, Vendor
from app.stripe import get_stripe_client
import os

from app.utils import is_subscription_active
from app.schemas import CustomerIn

router = APIRouter(prefix="/stripe", tags=["stripe"])
stripe = get_stripe_client()


class CheckoutSessionRequest(BaseModel):
    plan_id: str  # Stripe price ID
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    url: str


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    
    if is_subscription_active(db, current_user.id):
        raise HTTPException(status_code=400, detail="User already has an active subscription")
    
    """Create a Stripe checkout session and return redirect URL"""
    stripe_customer_id = current_user.stripe_customer_id
    
    if not stripe_customer_id:
        # Create Stripe customer if not exists
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.username or current_user.email
        )
        stripe_customer_id = customer.id
        current_user.stripe_customer_id = stripe_customer_id
        db.add(current_user) # Ensures the object is tracked by this session
        db.commit()          # Flushes the changes to the database
        db.refresh(current_user)
    
    try:
        session = stripe.checkout.Session.create(
            
            customer=stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": request.plan_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                "user_id": current_user.id,
            }
        )
        return CheckoutSessionResponse(url=session.url)
    except Exception as e:
        
        raise HTTPException(status_code=400, detail=str(e))

class ConnectAccountRequest(BaseModel):
    email: str
    country: str = "US"

class ConnectAccountResponse(BaseModel):
    account_id: str
    onboarding_url: str


# Route to create a Stripe Connect account and onboarding link
@router.post("/create-connect-account", response_model=ConnectAccountResponse)
async def create_connect_account(
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):

    # Check for existing ID first
    stmt = select(Vendor).where(Vendor.owner == current_user.id)
    vendor = db.execute(stmt).scalar_one_or_none()

    if not vendor:
        # Handle the case where the user isn't a vendor yet
        raise HTTPException(status_code=404, detail="Vendor profile not found")

    # 2. Check for an existing Stripe ID to prevent duplicate account creation
    if not vendor.stripe_connect_id:
        account = stripe.Account.create(type="express")
        vendor.stripe_connect_id = account.id
        db.commit()
        account_id = account.id
    else:
        # Use the existing ID if they are just returning to finish onboarding
        account_id = vendor.stripe_connect_id



    # Always generate a link for the existing (or new) ID
    try:
        account_link = stripe.AccountLink.create(
            account=account_id,
            refresh_url="http://localhost:5173/dashboard",
            return_url="http://localhost:5173/dashboard",
            type="account_onboarding",
        )
        return ConnectAccountResponse(account_id=account_id, onboarding_url=account_link.url)
    except stripe.error.StripeError as e:
        # Handle error appropriately
        print(f"Stripe error: {e.user_message}")
        raise HTTPException(status_code=400, detail=str(e))
    
class CartItem(BaseModel):
    product_id: int  # or str, depending on your DB
    quantity: int


class CartCheckoutRequest(BaseModel):
    #project_id: int
    items: list[CartItem]
    customer: CustomerIn
@router.post("/create-cart-checkout")
async def create_cart_checkout(cart_data: CartCheckoutRequest, db = Depends(get_db)):
    # 1. Await the execution to get the result object
    first_product_id = cart_data.items[0].product_id
    result = db.execute(
        select(Project)
        .join(ProjectProduct, Project.id == ProjectProduct.project_id)
        .where(ProjectProduct.id == first_product_id)
    )

    # 2. Extract the Project object from the result
    project_obj = result.scalar_one_or_none()

    # 3. Safety check: Ensure the project exists before accessing .id
    if project_obj:
        project_id = project_obj.id
    else:
        raise HTTPException(status_code=404, detail="Project not found for this product")
    customer = cart_data.customer
    stripe_connect_id = db.execute(
        select(Vendor.stripe_connect_id)
        .join(Project, Vendor.id == Project.vendor).
        where(Project.id == project_id)).scalar_one_or_none()
    shipping_price = db.execute(
        select(Vendor.shipping_price)
        .join(Project, Vendor.id == Project.vendor)
        .where(Project.id == project_id)).scalar_one_or_none() or 0
    # this also needs to send a customer
    
    if not stripe_connect_id:
        raise HTTPException(status_code=400, detail="Vendor does not have a Stripe Connect account")
    line_items = []
    internal_ids = []
    quanties = []
    total_amount = 0 

    for item in cart_data.items:
        product_id = item.product_id

        product = db.execute(select(ProjectProduct).where(ProjectProduct.id == product_id)).scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found") 
        quantity = item.quantity
        price = product.sale_price
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.name,
                    'description': product.description,
                },
                'unit_amount': price,
            },
            'quantity': quantity,
        })
        # Keep track of IDs to store in metadata
        internal_ids.append(product_id)
        quanties.append(quantity)
        total_amount += price * quantity

    if shipping_price > 0:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'Shipping'},
                'unit_amount': shipping_price,
            },
            'quantity': 1,
        })
        total_amount += shipping_price

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            # Stripe metadata has a 50-key limit and 500-character value limit.
            # For a cart, it's often best to pass a comma-separated string or a Cart ID.
            metadata={
                "project_id": project_id,
                "product_ids": ",".join(str(pid) for pid in internal_ids),
                "quantities": ",".join(str(q) for q in quanties),
                "customer": json.dumps(customer.model_dump()),
                "shipping_price_cents": shipping_price,
            },
            # If splitting payment for the whole cart to ONE vendor:
            payment_intent_data={
                "application_fee_amount": round(total_amount*.07), # your total platform fee
                "transfer_data": {"destination": stripe_connect_id},
            },
            success_url="https://localhost:5173",
            cancel_url="https://localhost:5173",
        )
        print("Stripe checkout session created:")
        return CheckoutSessionResponse(url=session.url)
    except Exception as e:
        return {"error": str(e)}