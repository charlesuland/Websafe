# This file was revised or written by Gemini AI

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.dependencies import get_db, get_current_user
from app.models import Vendor, VendorAdress, User
from app.schemas import VendorCreate, VendorOut

vendors_router = APIRouter(prefix="/vendors", tags=["Vendors"])


@vendors_router.post("/", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a vendor and their associated address in one transaction.
    """
    # 1. Check if the user already has a vendor (if you only allow 1 per user)
    existing_vendor = (
        db.execute(select(Vendor).where(Vendor.owner == current_user.id))
        .scalars()
        .first()
    )

    if existing_vendor:
        raise HTTPException(status_code=400, detail="User already has a vendor account")

    try:
        # 2. Create Vendor
        new_vendor = Vendor(
            business_name=vendor_data.business_name,
            email=vendor_data.email,
            owner=current_user.id,  # Tied to the authenticated user
            phone=vendor_data.phone,
            stripe_connect_id=vendor_data.stripe_connect_id,
            requirements_due_for_payment=vendor_data.requirements_due_for_payment,
        )
        db.add(new_vendor)
        db.flush()  # Get the new_vendor.id

        # 3. Create Address
        new_address = VendorAdress(
            vendor=new_vendor.id,
            house_number=vendor_data.address.house_number,
            street_name=vendor_data.address.street_name,
            city=vendor_data.address.city,
            state=vendor_data.address.state,
            postal_code=vendor_data.address.postal_code,
        )
        db.add(new_address)

        db.commit()
        db.refresh(new_vendor)
        return new_vendor

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not create vendor")


@vendors_router.get("/me", response_model=VendorOut)
async def get_my_vendor(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Retrieves the vendor profile for the logged-in user."""
    stmt = select(Vendor).where(Vendor.owner == current_user.id)
    vendor = db.execute(stmt).scalars().first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor profile not found")
    return vendor


@vendors_router.patch("/me", response_model=VendorOut)
async def update_vendor(
    update_data: dict,  # Or a specific Update Schema
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Updates vendor details for the logged-in user."""
    stmt = select(Vendor).where(Vendor.owner == current_user.id)
    vendor = db.execute(stmt).scalars().first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    for key, value in update_data.items():
        setattr(vendor, key, value)

    db.commit()
    db.refresh(vendor)
    return vendor
