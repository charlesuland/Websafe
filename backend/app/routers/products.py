from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends, Body, Form, Request
from app.dependencies import get_db, get_current_active_user, get_s3_client, s3_base_url, upload_image_to_s3
from app.activity_log import queue_security_event, describe_activity
from app.models import ProjectProduct, MediaObjectMetadata, Project, DraftProjectPage, Vendor
from sqlalchemy import update, select
from pydantic import BaseModel
import os
import uuid as UUID
from urllib.parse import quote

products_router = APIRouter(prefix="/products", tags=["products"])


# =========================
# MODELS
# =========================

class ProductIn(BaseModel):
    project_id: int
    name: str
    description: str
    sale_price: int
    shipping_price: int
    alt_text: str = ""
    stock: int


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sale_price: int | None = None
    shipping_price: int | None = None
    stock: int | None = None
    alt_text: str | None = None


class ToggleActive(BaseModel):
    is_active: bool


# =========================
# CREATE
# =========================

@products_router.post("/create-product")
async def create_product(
    product_in: ProductIn,
    request: Request,
    db=Depends(get_db),
    user=Depends(get_current_active_user),
):
    require_project_owner(product_in.project_id, user.id, db)

    new_product = ProjectProduct(**product_in.model_dump())
    db.add(new_product)
    queue_security_event(
        db,
        user_id=user.id,
        action="product_created",
        request=request,
        details=describe_activity("product", product_in.name, "created"),
    )
    db.commit()
    db.refresh(new_product)

    await ensure_ecommerce_page(new_product.project_id, db)

    return format_product(new_product, db)


@products_router.get("/get-product")
async def get_product(product_id: int, db=Depends(get_db), user=Depends(get_current_active_user)):
    product = require_product_owner(product_id, user.id, db)
    return format_product(product, db)


# =========================
# GET ALL PRODUCTS
# =========================

@products_router.get("/get-all-products")
async def get_all_products(project_id: int, db=Depends(get_db), user=Depends(get_current_active_user)):
    require_project_owner(project_id, user.id, db)
    products = db.execute(
        select(ProjectProduct)
        .where(ProjectProduct.project_id == project_id)
        .order_by(ProjectProduct.is_active.desc(), ProjectProduct.id.desc())
    ).scalars().all()

    return [format_product(p, db) for p in products]


@products_router.get("/get-all-published-products")
async def get_all_published_products(project_id: int, db=Depends(get_db), user=Depends(get_current_active_user)):
    require_project_owner(project_id, user.id, db)
    products = db.execute(
        select(ProjectProduct)
        .where(ProjectProduct.project_id == project_id)
        .where(ProjectProduct.is_published == True)
        .order_by(ProjectProduct.id.desc())
    ).scalars().all()

    return [format_product(p, db) for p in products]


# =========================
# UPDATE PRODUCT
# =========================

@products_router.put("/update-product/{product_id}")
async def update_product(product_id: int, product_in: ProductUpdate, request: Request, db=Depends(get_db), user=Depends(get_current_active_user)):
    product = require_product_owner(product_id, user.id, db)

    update_data = {k: v for k, v in product_in.model_dump().items() if v is not None}

    if update_data:
        product_name = update_data.get("name", product.name)
        db.execute(
            update(ProjectProduct)
            .where(ProjectProduct.id == product_id)
            .values(**update_data)
        )
        queue_security_event(
            db,
            user_id=user.id,
            action="product_updated",
            request=request,
            details=describe_activity("product", product_name, "saved"),
        )
        db.commit()

    await ensure_ecommerce_page(product.project_id, db)
    product = db.get(ProjectProduct, product_id)
    return format_product(product, db)


# =========================
# DELETE
# =========================

@products_router.delete("/delete-product/{product_id}")
async def delete_product(product_id: int, request: Request, db=Depends(get_db), user=Depends(get_current_active_user)):
    product = require_product_owner(product_id, user.id, db)

    product.is_active = False
    queue_security_event(
        db,
        user_id=user.id,
        action="product_deleted",
        request=request,
        details=describe_activity("product", product.name, "deleted"),
    )
    db.commit()
    await ensure_ecommerce_page(product.project_id, db)

    return {"status": "deleted"}


# =========================
# TOGGLE ACTIVE
# =========================

@products_router.post("/{product_id}/toggle-active")
async def toggle_product_active(product_id: int, payload: ToggleActive, request: Request, db=Depends(get_db), user=Depends(get_current_active_user)):
    product = require_product_owner(product_id, user.id, db)

    product.is_active = payload.is_active
    queue_security_event(
        db,
        user_id=user.id,
        action="product_updated",
        request=request,
        details=describe_activity(
            "product",
            product.name,
            "saved",
            extra=f"status changed to {'active' if payload.is_active else 'inactive'}",
        ),
    )
    db.commit()

    await ensure_ecommerce_page(product.project_id, db)

    return {"status": "updated", "is_active": product.is_active}


# =========================
# IMAGE UPLOAD
# =========================

@products_router.post("/add-product-picture")
async def add_product_picture(
    product_id: int,
    request: Request,
    file: UploadFile = File(...),
    alt_text: str | None = Form(default=None),
    db=Depends(get_db),
    s3=Depends(get_s3_client),
    user=Depends(get_current_active_user),
):
    product = require_product_owner(product_id, user.id, db)

    ext = os.path.splitext(file.filename)[1]
    file_key = f"products/{product_id}/{UUID.uuid4()}{ext}"

    file_bytes = await file.read()
    upload_url = await upload_image_to_s3(file_bytes, file_key, file.content_type, s3)

    metadata = MediaObjectMetadata(
        project_id=product.project_id,
        file_key=file_key,
        file_type=file.content_type,
        file_size_bytes=len(file_bytes),
        alt_text=alt_text,
    )

    db.add(metadata)
    db.flush()

    product.product_image = metadata.id
    if alt_text is not None:
        product.alt_text = alt_text
    queue_security_event(
        db,
        user_id=user.id,
        action="product_updated",
        request=request,
        details=describe_activity(
            "product",
            product.name,
            "saved",
            extra="image uploaded",
        ),
    )
    db.commit()
    await ensure_ecommerce_page(product.project_id, db)

    return format_product(product, db)


# =========================
# HELPERS
# =========================

def format_product(p: ProjectProduct, db):
    image_url = None

    if p.product_image:
        metadata = db.get(MediaObjectMetadata, p.product_image)
        if metadata:
            image_url = build_media_proxy_url(metadata.file_key)

    return {
        "id": p.id,
        "project_id": p.project_id,
        "name": p.name,
        "description": p.description,
        "sale_price": p.sale_price,
        "shipping_price": p.shipping_price,
        "image_url": image_url,
        "alt_text": p.alt_text,
        "stock": p.stock,
        "is_active": p.is_active,
        "is_published": p.is_published,
    }


def build_media_proxy_url(file_key: str) -> str:
    return f"/api/site/_media?file_key={quote(file_key, safe='')}"


def require_project_owner(project_id: int, user_id: int, db):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    vendor = db.get(Vendor, project.vendor)
    if not vendor or vendor.owner != user_id:
        raise HTTPException(403, "Not authorized")

    return project


def require_product_owner(product_id: int, user_id: int, db):
    product = db.get(ProjectProduct, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    require_project_owner(product.project_id, user_id, db)
    return product


# =========================
# ECOMMERCE PAGE
# =========================

async def ensure_ecommerce_page(project_id: int, db):
    existing = db.execute(
        select(DraftProjectPage).where(
            DraftProjectPage.project == project_id,
            DraftProjectPage.name == "Shop"
        )
    ).scalar_one_or_none()

    products = db.execute(
        select(ProjectProduct).where(
            ProjectProduct.project_id == project_id,
            ProjectProduct.is_active == True
        )
    ).scalars().all()

    if not products:
        if existing:
            db.delete(existing)
            db.commit()
        return

    layout = create_ecommerce_layout(products, db, project_id, existing)

    if existing:
        existing.layout = layout
    else:
        db.add(DraftProjectPage(
            project=project_id,
            name="Shop",
            layout=layout
        ))

    db.commit()


def create_ecommerce_layout(products, db, project_id=None, existing_shop_page=None):
    layout = []
    columns = [1, 5, 9]
    card_col_span = 4
    card_row_span = 5
    navbar = get_shop_navbar_component(project_id, db, existing_shop_page)

    if navbar:
        layout.append(navbar)

    for index, p in enumerate(products):
        image_url = None
        if p.product_image:
            metadata = db.get(MediaObjectMetadata, p.product_image)
            if metadata:
                image_url = build_media_proxy_url(metadata.file_key)

        column_index = index % len(columns)
        row_index = index // len(columns)

        layout.append({
            "id": str(UUID.uuid4()),
            "type": "product",
            "col": columns[column_index],
            "row": 2 + (row_index * card_row_span),
            "colSpan": card_col_span,
            "rowSpan": card_row_span,
            "props": {
                "productId": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.sale_price,
                "imageUrl": image_url,
                "altText": p.alt_text,
                "inStock": p.stock > 0
            }
        })

    return layout


def get_shop_navbar_component(project_id, db, existing_shop_page=None):
    existing_layout = existing_shop_page.layout if existing_shop_page else []
    navbar_component = find_navbar_component(existing_layout)
    if navbar_component:
        return normalize_navbar_component(navbar_component)

    if project_id is not None:
        pages = db.execute(
            select(DraftProjectPage).where(DraftProjectPage.project == project_id)
        ).scalars().all()
        for page in pages:
            navbar_component = find_navbar_component(page.layout)
            if navbar_component:
                return normalize_navbar_component(navbar_component)

    return {
        "id": str(UUID.uuid4()),
        "type": "navbar",
        "col": 1,
        "row": 1,
        "colSpan": 12,
        "rowSpan": 1,
        "props": {
            "links": ["Home"],
            "style": {
                "fontSize": 18,
                "textAlign": "center",
                "backgroundColor": "#ffffff",
                "backgroundOpacity": 1,
                "color": "#000000",
            },
        },
    }


def find_navbar_component(layout):
    for component in layout or []:
        if component.get("type") == "navbar":
            return component
    return None


def normalize_navbar_component(component):
    props = dict(component.get("props") or {})
    style = {
        "fontSize": 18,
        "textAlign": "center",
        "backgroundColor": "#ffffff",
        "backgroundOpacity": 1,
        "color": "#000000",
    }
    style.update(props.get("style") or {})

    return {
        "id": str(UUID.uuid4()),
        "type": "navbar",
        "col": 1,
        "row": 1,
        "colSpan": 12,
        "rowSpan": 1,
        "props": {
            "links": list(props.get("links") or ["Home"]),
            "style": style,
        }
    }
