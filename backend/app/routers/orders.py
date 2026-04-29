# Part of this file was revised or written by Gemini AI


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.dependencies import get_db, get_current_user
from app.models import ProjectOrder, ProjectCustomer, ProjectOrderItem, Project, Vendor
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


@orders_router.post("/make-order", status_code=status.HTTP_201_CREATED)
async def make_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """
    Public endpoint. Anyone can place an order.
    We just need to verify the project_id exists.
    """
    # Check if the project exists before allowing an order
    project = db.get(Project, order_data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        new_order = ProjectOrder(project=order_data.project_id)
        db.add(new_order)
        db.flush()

        for p_id in order_data.product_ids:
            db.add(ProjectOrderItem(order_id=new_order.id, product_id=p_id))

        db.add(
            ProjectCustomer(
                order=new_order.id,
                email=order_data.customer_info.email,
                name=order_data.customer_info.name,
            )
        )

        db.commit()
        return {"status": "success", "order_id": new_order.id}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Order processing failed")
