from fastapi import APIRouter, Depends
from app.models import Vendor, VendorAdress
from pydantic import BaseModel
from app.dependencies import get_db, get_current_user
from sqlalchemy import select, update


class VendorID(BaseModel):
    val: int


class VendorIn(BaseModel):
    business_name: str
    email: str
    phone: str
    owner: int


class VendorAddressIn(BaseModel):
    vendor: int
    house_number: int
    street_name: str
    city: str
    state: str
    postal_code: str


vendor_router = APIRouter(prefix="vendors", tags=["vendors"])


@vendor_router.get("/get-vendor")
async def get_vendor(vendor_id: VendorID, db=Depends(get_db)):
    stmt = select(Vendor).where(Vendor.id == vendor_id.val)
    result_vendor = db.execute(stmt).scalars().first()
    return result_vendor


@vendor_router.get("/get-vendor-address")
async def get_vendor_address(vendor_id: VendorID, db=Depends(get_db)):
    stmt = select(VendorAdress).where(VendorAdress.vendor == vendor_id.val)
    result_vendor_address = db.execute(stmt).scalars().first()
    return result_vendor_address


@vendor_router.get("/create-vendor")
async def create_vendor(
    vendor_in: VendorIn, vendor_address_in: VendorAddressIn, db=Depends(get_db)
):
    stmt = ()
