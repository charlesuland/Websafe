from fastapi import APIRouter, HTTPException
from app.dependencies import get_db, get_current_active_user
from app.models import Vendor, ProjectProduct
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import update, select

products_router = APIRouter(prefix="/products", tags=["products"])


class ProductIn(BaseModel):
    project_id: int
    name: str
    description: str
    sale_price: int
    shipping_price: int


class ProductID(BaseModel):
    val: int


class ProjectID(BaseModel):
    val: int


# create the incoming product
@products_router.post("/create-product")
async def create_product(product_in: ProductIn, db=Depends(get_db)):
    product_data = product_in.model_dump()
    new_product = ProjectProduct(**product_data)
    db.add(new_product)
    db.commit()


# increase the product stock by 1
@products_router.post("/increment-product")
async def increment_product(product_id: ProductID, db=Depends(get_db)):
    stmt = (
        update(ProjectProduct)
        .where(ProjectProduct.id == product_id.val)
        .values(stock=ProjectProduct.stock + 1)
    )
    db.execute(stmt)
    db.commit()


# decrease the product stock by 1
@products_router.post("/decrement-product")
async def decrement_product(product_id: ProductID, db=Depends(get_db)):
    stmt = (
        update(ProjectProduct)
        .where(ProjectProduct.id == product_id.val)
        .values(stock=ProjectProduct.stock + 1)
    )
    db.execute(stmt)
    db.commit()


# return the product stock
@products_router.get("/get-product-stock")
async def get_product_stock():
    pass


# make the product inactive
@products_router.delete("/delete-product")
async def delete_product(product_id: ProductID, db=Depends(get_db)):
    stmt = (
        update(ProjectProduct)
        .where(ProjectProduct.id == product_id.val)
        .values(is_active=False)
    )
    db.execute(stmt)
    db.commit()


# get a product
@products_router.get("/get-product")
async def get_product(product_id: ProductID, db=Depends(get_db)):
    stmt = select(ProjectProduct).where(ProjectProduct.id == product_id.val)

    return db.execute(stmt).scalars().first()


# get all the products that are associated with the project
@products_router.get("/get-all-products")
async def get_all_products(project_id: ProjectID, db=Depends(get_db)):
    # return all
    stmt = (
        select(ProjectProduct)
        .where(ProjectProduct.project_id == project_id.val)
        .where(ProjectProduct.is_active)
    )
    return db.execute(stmt).scalars().all()


# get all the published prodcuts
@products_router.get("/get-all-published-products")
async def get_all_published_products(project_id: ProjectID, db=Depends(get_db)):
    stmt = (
        select(ProjectProduct)
        .where(ProjectProduct.project_id == project_id.val)
        .where(ProjectProduct.is_active)
        .where(ProjectProduct.is_published)
    )
    return db.execute(stmt).scalars().all()


# change a product
@products_router.post("/update-product")
async def update_product():
    pass


# put a picture into the S3 object server
@products_router.post("/add-product-picture")
async def add_product_image():
    # this is where the api to s3 will be used
    pass


# return the image for a project
@products_router.get("/get-product-image")
async def get_product_image():
    pass
