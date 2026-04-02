from fastapi import APIRouter, Depends
from app.models import ProjectOrder, ProjectOrderItem, ProjectCustomer
from app.dependencies import get_db, get_current_user
from sqlalchemy import select, update
from pydantic import BaseModel, EmailStr


order_router = APIRouter(prefix="/order", tags=["orders"])


class ProjectID(BaseModel):
    val: int


class OrderID(BaseModel):
    val: int


@order_router.get("/")
async def get_order(order_id: OrderID, db=Depends(get_db)):
    stmt = select(ProjectOrder).where(ProjectOrder.id == order_id.val)
    result_order = db.execute(stmt).scalars().first()
    return result_order


@order_router.get("/get-project-orders")
async def get_project_orders(project_id: ProjectID, db=Depends(get_db)):
    stmt = select(ProjectOrder).where(ProjectOrder.project == project_id.val)
    result_orders = db.execute(stmt).scalars().all()
    return result_orders


@order_router.get("/get-customer-orders")
async def get_customer_orders(
    customer_email: EmailStr, project_id: ProjectID, db=Depends(get_db)
):
    stmt = (
        select(ProjectOrder)
        .join(ProjectCustomer)
        .where(ProjectOrder.project == project_id.val)
        .where(ProjectOrder.id == ProjectCustomer.order)
        .where(ProjectCustomer.email == customer_email)
    )
    result_orders = db.execute(stmt).scalars().all()
    return result_orders


@order_router.post("/make-order")
async def make_order(project_id, product_ids, customer_info, db=Depends(get_db)):
    pass
