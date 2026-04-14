# this file was revised or written in part by Copilot

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from app.dependencies import get_db, get_current_active_user, get_s3_client, s3_base_url, upload_image_to_s3
from app.models import ProjectProduct, ProductImage, MediaObjectMetadata, Project, ProjectPage, DraftProjectPage
from fastapi import Depends
import os
import json
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
    alt_text: str = ""
    stock: int


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sale_price: int | None = None
    shipping_price: int | None = None
    stock: int | None = None
    alt_text: str | None = None
    # product_image field is managed separately via upload endpoint


class ProductID(BaseModel):
    val: int


class ProjectID(BaseModel):
    val: int


# create the incoming product
@products_router.post("/create-product")
async def create_product(
    product_in: ProductIn,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    project = db.get(Project, product_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    product_data = product_in.model_dump()
    new_product = ProjectProduct(**product_data)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Check if we need to create an ecommerce page
    await ensure_ecommerce_page(new_product.project_id, db)

    return {
        "id": new_product.id,
        "project_id": new_product.project_id,
        "name": new_product.name,
        "description": new_product.description,
        "sale_price": new_product.sale_price,
        "shipping_price": new_product.shipping_price,
        "alt_text": new_product.alt_text,
        "stock": new_product.stock,
        "product_image": new_product.product_image,
        "is_active": new_product.is_active,
        "is_published": new_product.is_published,
    }

# increase the product stock by 1
@products_router.post("/increment-product")
async def increment_product(
    product_id: ProductID,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    product = db.get(ProjectProduct, product_id.val)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stmt = (
        update(ProjectProduct)
        .where(ProjectProduct.id == product_id.val)
        .values(stock=ProjectProduct.stock + 1)
    )
    db.execute(stmt)
    db.commit()
    return {"status": "success", "stock": product.stock + 1}



# decrease the product stock by 1
@products_router.post("/decrement-product")
async def decrement_product(
    product_id: ProductID,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    product = db.get(ProjectProduct, product_id.val)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock <= 0:
        raise HTTPException(status_code=400, detail="Product stock cannot be negative")

    stmt = (
        update(ProjectProduct)
        .where(ProjectProduct.id == product_id.val)
        .values(stock=ProjectProduct.stock - 1)
    )
    db.execute(stmt)
    db.commit()
    return {"status": "success", "stock": product.stock - 1}


# return the product stock
@products_router.get("/get-product-stock")
async def get_product_stock(product_id: int = Query(...), db=Depends(get_db)):
    stmt = select(ProjectProduct).where(ProjectProduct.id == product_id)
    result_product = db.execute(stmt).scalars().first()
    if not result_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"stock": result_product.stock}



# make the product inactive
@products_router.delete("/delete-product")
async def delete_product(
    product_id: int = Query(...),
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    product = db.get(ProjectProduct, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stmt = (
        update(ProjectProduct)
        .where(ProjectProduct.id == product_id)
        .values(is_active=False)
    )
    db.execute(stmt)
    db.commit()


# toggle product active status
@products_router.post("/{product_id}/toggle-active")
async def toggle_product_active(product_id: int, is_active: bool, db=Depends(get_db)):
    product = db.get(ProjectProduct, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    product.is_active = is_active
    db.commit()
    
    # Ensure ecommerce page exists/updated when activating products
    if is_active:
        await ensure_ecommerce_page(db, product.project_id)
    
    return {"status": "updated", "is_active": is_active}


# get a product
@products_router.get("/get-product")
async def get_product(product_id: int = Query(...), db=Depends(get_db)):
    stmt = select(ProjectProduct).where(ProjectProduct.id == product_id)
    product = db.execute(stmt).scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# get all the products that are associated with the project
@products_router.get("/get-all-products")
async def get_all_products(project_id: int = Query(...), db=Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    products = db.execute(
        select(ProjectProduct)
        .where(ProjectProduct.project_id == project_id)
        .where(ProjectProduct.is_active)
    ).scalars().all()

    result = []
    for p in products:
        image_url = None

        if p.product_image:
            metadata = db.get(MediaObjectMetadata, p.product_image)
            if metadata:
                image_url = f"{s3_base_url}/{metadata.file_key}"

        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "sale_price": p.sale_price,
            "image_url": image_url,
            "alt_text": p.alt_text,
        })
    return result


# get all the published prodcuts
@products_router.get("/get-all-published-products")
async def get_all_published_products(project_id: int = Query(...), db=Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

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
    product_id: ProductID, product_in: ProductUpdate, db=Depends(get_db)
):
    # Build update values dynamically, only including non-None fields
    update_values = {}
    if product_in.name is not None:
        update_values['name'] = product_in.name
    if product_in.description is not None:
        update_values['description'] = product_in.description
    if product_in.sale_price is not None:
        update_values['sale_price'] = product_in.sale_price
    if product_in.shipping_price is not None:
        update_values['shipping_price'] = product_in.shipping_price
    if product_in.stock is not None:
        update_values['stock'] = product_in.stock
    if product_in.alt_text is not None:
        update_values['alt_text'] = product_in.alt_text
    
    # product_image is managed separately via upload endpoint
    
    if update_values:
        stmt = (
            update(ProjectProduct)
            .where(ProjectProduct.id == product_id.val)
            .values(**update_values)
        )
        db.execute(stmt)
        db.commit()

    product = db.get(ProjectProduct, product_id.val)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": product.id,
        "project_id": product.project_id,
        "name": product.name,
        "description": product.description,
        "sale_price": product.sale_price,
        "shipping_price": product.shipping_price,
        "alt_text": product.alt_text,
        "stock": product.stock,
        "product_image": product.product_image,
        "is_active": product.is_active,
        "is_published": product.is_published,
    }


# put a picture into the S3 object server
@products_router.post("/add-product-picture")
# this is where the api to s3 will be used
async def add_product_picture(
    product_id: int,
    alt_text: str = Query(None),
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

    # Upload to S3 using the reusable function
    upload_url = await upload_image_to_s3(file_bytes, file_key, file.content_type, s3)

    metadata = MediaObjectMetadata(
        project_id=product.project_id,
        file_key=file_key,
        file_type=file.content_type,
        file_size_bytes=file_size,
        alt_text=alt_text
    )
    db.add(metadata)
    db.flush()
    product.product_image = metadata.id
    db.commit()

    return {"status": "success", "image_url": upload_url}


# return the image for a project
@products_router.get("/get-product-image")
async def get_product_image(product_id: int, db=Depends(get_db)):
    product = db.get(ProjectProduct, product_id)
    if not product or not product.product_image:
        raise HTTPException(404, "Product not found")

    metadata = db.get(MediaObjectMetadata, product.product_image)

    return {"image_url": f"{s3_base_url}{metadata.file_key}"}


async def ensure_ecommerce_page(project_id: int, db=Depends(get_db)):
    # Ensure a project has an ecommerce page if it has active products
    active_products = db.execute(
        select(ProjectProduct).where(
            ProjectProduct.project_id == project_id,
            ProjectProduct.is_active == True
        )
    ).scalars().all()
    
    if not active_products:
        return  # No active products, no need for ecommerce page
    
    # Check if ecommerce page already exists in draft pages
    existing_page = db.execute(
        select(DraftProjectPage).where(
            DraftProjectPage.project == project_id,
            DraftProjectPage.name == "Shop"
        )
    ).scalar_one_or_none()
    
    if existing_page:
        # If ecommerce page exists, update it with current products
        existing_page.layout = create_ecommerce_layout(active_products, db)
        db.commit()
        return
    
    # Create new ecommerce page
    ecommerce_layout = create_ecommerce_layout(active_products, db)
    
    ecommerce_page = DraftProjectPage(
        project=project_id,
        name="Shop",
        layout=ecommerce_layout
    )
    
    db.add(ecommerce_page)
    db.commit()


def create_ecommerce_layout(products: list[ProjectProduct], db=Depends(get_db)):
    """Create a grid layout for ecommerce products"""
    layout = []
    
    # Add shop header
    layout.append({
        "id": str(UUID.uuid4()),
        "type": "text",
        "col": 1,
        "row": 1,
        "colSpan": 12,
        "rowSpan": 2,
        "props": {
            "text": "Shop Our Products",
            "style": {
                "textAlign": "center",
                "fontSize": "30px",
                "color": "#333",
                "backgroundColor": "#ffffff"
            }
        },
        "children": []
    })
    
    # Add products in a grid (3 columns per row)
    for i, product in enumerate(products):
        # Get image URL if available
        image_url = None
        if product.product_image:
            metadata = db.get(MediaObjectMetadata, product.product_image)
            if metadata:
                image_url = f"{s3_base_url}/{metadata.file_key}"
        
        # Calculate grid position (3 products per row)
        col = 1 + (i % 3) * 4  # 12 columns / 3 products = 4 columns each
        row = 3 + (i // 3) * 3  # Start after header, 3 rows per product
        
        product_component = {
            "id": str(UUID.uuid4()),
            "type": "product",
            "col": col,
            "row": row,
            "colSpan": 4,
            "rowSpan": 6,
            "props": {
                "productId": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.sale_price,
                "imageUrl": image_url,
                "altText": product.alt_text or product.name,
                "inStock": product.stock > 0
            },
            "children": []
        }
        layout.append(product_component)
    
    return layout
