# this file was revised or written in part by Copilot


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.dependencies import get_db, get_current_user
from app.models import (
    Project,
    ProjectProduct,
    ProjectOrder,
    ProjectOrderItem,
    ProjectCustomer,
    Vendor,
)

checkout_router = APIRouter(prefix="/checkout", tags=["checkout"])


class CheckoutItem(BaseModel):
    product_id: int
    quantity: int = 1


class CheckoutCustomer(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = ""


class CheckoutCreateRequest(BaseModel):
    project_id: int
    items: List[CheckoutItem]
    customer: CheckoutCustomer
    payment_method: Optional[str] = "manual"


class CheckoutCreateResponse(BaseModel):
    order_id: int
    item_price_cents: int
    shipping_price_cents: int
    platform_fee_cents: int
    vendor_amount_cents: int
    payment_status: bool


@checkout_router.post(
    "/create",
    response_model=CheckoutCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_checkout(
    checkout: CheckoutCreateRequest,
    db: Session = Depends(get_db),
):
    project = db.get(Project, checkout.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not checkout.items:
        raise HTTPException(status_code=400, detail="No checkout items provided")

    # accumulation values
    item_price_cents = 0
    shipping_price_cents = 0
    currency = "USD"
    order_items = []

    for item in checkout.items:
        product = db.get(ProjectProduct, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        if product.project_id != checkout.project_id:
            raise HTTPException(
                status_code=400,
                detail=f"Product {item.product_id} does not belong to project {checkout.project_id}",
            )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Product {item.product_id} stock insufficient (available {product.stock})",
            )

        if item.quantity < 1:
            raise HTTPException(status_code=400, detail="Quantity must be >= 1")

        item_price_cents += product.sale_price * item.quantity
        shipping_price_cents += product.shipping_price * item.quantity
        currency = product.currency or currency

        order_items.append((product, item.quantity))

    platform_fee_cents = int(item_price_cents * 0.1)
    vendor_amount_cents = item_price_cents + shipping_price_cents - platform_fee_cents

    new_order = ProjectOrder(
        stripe_id="manual",
        item_price=item_price_cents,
        shipping_price=shipping_price_cents,
        currency=currency,
        payment_status=False,
        project=checkout.project_id,
        platform_fee_cents=platform_fee_cents,
        vendor_amount_cents=vendor_amount_cents,
        meta={
            "items": [
                {
                    "product_id": p.id,
                    "quantity": q,
                    "unit_price": p.sale_price,
                    "shipping_price": p.shipping_price,
                }
                for p, q in order_items
            ],
            "customer": checkout.customer.dict(),
            "payment_method": checkout.payment_method,
        },
    )

    db.add(new_order)
    db.flush()

    for product, qty in order_items:
        for _ in range(qty):
            db.add(
                ProjectOrderItem(
                    item=product.id,
                    order=new_order.id,
                    price_at_purchase=product.sale_price,
                    tracking_number="",
                )
            )
        product.stock -= qty

    # customer with name splitting
    fullname = checkout.customer.name.strip().split(" ", 1)
    first_name = fullname[0] if fullname else ""
    last_name = fullname[1] if len(fullname) > 1 else ""

    db.add(
        ProjectCustomer(
            order=new_order.id,
            first_name=first_name,
            last_name=last_name,
            phone=checkout.customer.phone or "",
            email=checkout.customer.email,
        )
    )

    db.commit()
    db.refresh(new_order)

    return CheckoutCreateResponse(
        order_id=new_order.id,
        item_price_cents=item_price_cents,
        shipping_price_cents=shipping_price_cents,
        platform_fee_cents=platform_fee_cents,
        vendor_amount_cents=vendor_amount_cents,
        payment_status=new_order.payment_status,
    )


@checkout_router.post("/{order_id}/confirm")
async def confirm_checkout(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = db.get(ProjectOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    project = db.get(Project, order.project)
    if not project:
        raise HTTPException(status_code=404, detail="Associated project not found")

    vendor = db.get(Vendor, project.vendor)
    if not vendor or vendor.owner != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to confirm this order")

    if order.payment_status:
        return {"status": "already_confirmed"}

    order.payment_status = True
    db.commit()

    return {"status": "confirmed", "order_id": order_id}
