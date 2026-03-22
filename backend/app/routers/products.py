from fastapi import APIRouter, HTTPException
from app.dependencies import get_db, get_current_active_user
from app.models import Vendor, ProjectProduct
from fastapi import Depends
from pydantic import BaseModel

products_router = APIRouter(prefix="/products", tags=["projects"])


# create the incoming product
@products_router.post("/create-product")
async def create_product():

    pass


# increase the product stock by 1
@products_router.post("/increment-product")
async def increment_product():
    pass


# decrease the product stock by 1
@products_router.post("/decrement-product")
async def decrement_product():
    pass


# return the product stock
@products_router.get("/get-product-stock")
async def get_product_stock():
    pass


# make the product inactive
@products_router.delete("/delete-product")
async def delete_product():
    pass


# get a product
@products_router.get("/get-product")
async def get_product():
    pass


# get all the products that are associated with the project
@products_router.get("/get-all-products")
async def get_all_products():
    # return all
    pass


# get all the published prodcuts
@products_router.get("/get-all-published-products")
async def get_all_published_products():
    pass


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
