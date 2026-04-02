from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from app.dependencies import get_db, get_current_active_user, get_s3_client, s3_base_url
from app.models import ProjectProduct, ProductImage, MediaObjectMetadata, Project
from fastapi import Depends
import os
import uuid as UUID
from pydantic import BaseModel
from sqlalchemy import update, select

products_router = APIRouter(prefix="/products", tags=["products"])


class ProductIn(BaseModel):
    project_id: int
    name: str
    description: str
    sale_price: int
    shipping_price: int
    product_image: int | None = None
    stock: int


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
    db.refresh(new_product)

    return new_product


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
        .values(stock=ProjectProduct.stock - 1)
    )
    db.execute(stmt)
    db.commit()


# return the product stock
@products_router.get("/get-product-stock")
async def get_product_stock(product_id: int = Query(...), db=Depends(get_db)):
    stmt = select(ProjectProduct).where(ProjectProduct.id == product_id)
    result_product = db.execute(stmt).scalars().first()
    return result_product.stock


# make the product inactive
@products_router.delete("/delete-product")
async def delete_product(product_id: int = Query(...), db=Depends(get_db)):
    stmt = (
        update(ProjectProduct)
        .where(ProjectProduct.id == product_id)
        .values(is_active=False)
    )
    db.execute(stmt)
    db.commit()


# get a product
@products_router.get("/get-product")
async def get_product(product_id: int = Query(...), db=Depends(get_db)):
    stmt = select(ProjectProduct).where(ProjectProduct.id == product_id)

    return db.execute(stmt).scalars().first()


# get all the products that are associated with the project
@products_router.get("/get-all-products")
async def get_all_products(project_id: int = Query(...), db=Depends(get_db)):
    stmt = (
        select(ProjectProduct)
        .where(ProjectProduct.project_id == project_id)
        .where(ProjectProduct.is_active)
    )

    products = db.execute(stmt).scalars().all()

    result = []
    for p in products:
        image_url = None

        if p.product_image:
            metadata = db.get(MediaObjectMetadata, p.product_image)
            if metadata:
                image_url = f"{s3_base_url}/{metadata.file_key}"

        result.append(
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "sale_price": p.sale_price,
                "image_url": image_url,
            }
        )
    return result


# get all the published prodcuts
@products_router.get("/get-all-published-products")
async def get_all_published_products(project_id: int = Query(...), db=Depends(get_db)):
    stmt = (
        select(ProjectProduct)
        .where(ProjectProduct.project_id == project_id)
        .where(ProjectProduct.is_active)
        .where(ProjectProduct.is_published)
    )
    return db.execute(stmt).scalars().all()


# change a product
@products_router.post("/update-product")
async def update_product(
    product_id: ProductID, product_in: ProductIn, db=Depends(get_db)
):
    stmt = (
        update(ProjectProduct)
        .where(ProjectProduct.id == product_id.val)
        .values(
            name=product_in.name,
            description=product_in.description,
            sale_price=product_in.sale_price,
            shipping_price=product_in.shipping_price,
            product_image=product_in.product_image,
            stock=product_in.stock,
        )
    )
    db.execute(stmt)
    db.commit()


# put a picture into the S3 object server
@products_router.post("/add-product-picture")
# this is where the api to s3 will be used
async def add_product_picture(
    product_id: int,
    file: UploadFile = File(...),
    db=Depends(get_db),
    s3=Depends(get_s3_client),
):
    product = db.get(ProjectProduct, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    ext = os.path.splitext(file.filename)[1]
    file_key = f"products/{product_id}/{UUID.uuid4()}{ext}"

    file_bytes = await file.read()

    file_size = len(file_bytes)

    obj = s3.Object("websafe", file_key)
    obj.put(Body=file_bytes, ContentType=file.content_type)

    metadata = MediaObjectMetadata(
        project_id=product.project_id,
        file_key=file_key,
        file_type=file.content_type,
        file_size_bytes=file_size,
    )
    db.add(metadata)
    db.flush()
    product.product_image = metadata.id
    db.commit()

    return {"status": "success", "url": f"{s3_base_url}{file_key}"}


# return the image for a project
@products_router.get("/get-product-image")
async def get_product_image(product_id: int, db=Depends(get_db)):
    product = db.get(ProjectProduct, product_id)
    if not product or not product.product_image:
        raise HTTPException(404, "Product not found")

    metadata = db.get(MediaObjectMetadata, product.product_image)

    return {"url": f"{s3_base_url}{metadata.file_key}"}
