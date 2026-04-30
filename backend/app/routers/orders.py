# Part of this file was revised or written by Gemini AI


from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.dependencies import get_db, get_current_user
from app.models import ProjectCustomerAddress, ProjectOrder, ProjectCustomer, ProjectOrderItem, Project, ProjectProduct, Vendor
from app.schemas import OrderOut, OrderCreate, User

orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch a single order, strictly validating ownership through
    the Vendor -> Project -> Order chain.
    """
    # Build the query with joins to verify the owner
    stmt = (
        select(ProjectOrder)
        .join(Project, ProjectOrder.project == Project.id)
        .join(Vendor, Project.vendor == Vendor.id)
        .where(ProjectOrder.id == order_id)
        .where(Vendor.owner == current_user.id)
    )

    result = db.execute(stmt).scalars().first()

    # Security note: Use 404 instead of 403 to avoid confirming
    # the existence of an ID the user doesn't own.
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    return result


@orders_router.get("/project/{project_id}", response_model=List[OrderOut])
async def get_project_orders(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(ProjectOrder)
        .join(Project, ProjectOrder.project == Project.id)
        .join(Vendor, Project.vendor == Vendor.id)
        .where(Project.id == project_id)
        .where(Vendor.owner == current_user.id)
    )
    return db.execute(stmt).scalars().all()


class CustomerOut(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    line: str
    city: str
    state: str
    postal_code: str
class ItemOut(BaseModel):
    id: int
    name: str
    price_at_purchase: int
    shipping_status: str
    quantity: int
class OrderOut(BaseModel):
    id: int
    amount_total: int

    vendor_amount_cents: int
    shipping_price_cents: int
    items: List[ItemOut]
    customer: CustomerOut


class AllOrderOut(BaseModel):
    orders: List[OrderOut]



@orders_router.get("/", response_model=AllOrderOut, status_code=status.HTTP_200_OK)
async def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership of the project before creating the order
    stmt = (
        select(ProjectOrder)
        .join(Project, ProjectOrder.project == Project.id)
        .join(Vendor, Project.vendor == Vendor.id)
        .where(Vendor.owner == current_user.id)
    )
    projectOrder = db.execute(stmt).scalars().all()
    all_orders = []
    for order in projectOrder:
        items = db.execute(select(ProjectOrderItem).where(ProjectOrderItem.order == order.id)).scalars().all()
        customer = db.execute(select(ProjectCustomer).where(ProjectCustomer.order == order.id)).scalars().first()
        customer_address = db.execute(select(ProjectCustomerAddress).where(ProjectCustomerAddress.customer == customer.id)).scalars().first()
        items_out = []
        for item in items:
            item_name = db.execute(select(ProjectProduct.name).where(ProjectProduct.id == item.id)).scalar_one_or_none() or "Unknown Product"
            items_out.append(ItemOut(name=item_name, id=item.id, price_at_purchase=item.price_at_purchase, shipping_status=item.shipping_status, quantity=item.quantity))
        customer_out = CustomerOut(first_name=customer.first_name, last_name=customer.last_name, phone=customer.phone, email=customer.email, line=str(customer_address.house_number) + " " + customer_address.street_name, city=customer_address.city, state=customer_address.state, postal_code=str(customer_address.postal_code))
        order_out = OrderOut(id=order.id, amount_total=order.amount_total, vendor_amount_cents=order.vendor_amount_cents, shipping_price_cents=order.shipping_price_cents, items=items_out, customer=customer_out)
        all_orders.append(order_out)
    print(all_orders)
    if not all_orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found for this user")
    return AllOrderOut(orders=all_orders)
