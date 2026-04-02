# Part of this file was revised or written by Gemini AI


from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict
from typing import List, Optional
from datetime import datetime


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    """Shared properties used for both input and output."""

    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    is_active: bool = True


class UserCreate(UserBase):
    """Schema for user registration - requires a raw password."""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile - all fields optional."""

    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None


class User(UserBase):
    """
    The 'Public' User schema.
    This is what you return in API responses (No password here!).
    """

    id: int
    created_at: datetime

    # Allows Pydantic to convert SQLAlchemy models to this schema
    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    """Internal schema that includes the hashed password from the DB."""

    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# --- Customer Schemas ---
class CustomerBase(BaseModel):
    email: EmailStr
    name: str


class CustomerCreate(CustomerBase):
    pass


# --- Order Item Schemas ---
class OrderItemRead(BaseModel):
    product_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Order Schemas ---
class OrderBase(BaseModel):
    project_id: int


class OrderCreate(OrderBase):
    product_ids: List[int]
    project_id: int
    customer_info: CustomerCreate


class OrderOut(OrderBase):
    id: int
    # You can nest related data here
    items: List[OrderItemRead] = []
    project: int

    model_config = ConfigDict(from_attributes=True)


class VendorAddressBase(BaseModel):
    house_number: int
    street_name: str
    city: str
    state: str
    postal_code: str


class VendorCreate(BaseModel):
    business_name: str
    email: EmailStr
    phone: str
    stripe_connect_id: str
    requirements_due_for_payment: str
    address: VendorAddressBase  # Nested address info


class VendorOut(BaseModel):
    id: int
    business_name: str
    email: EmailStr
    payouts_enabled: bool

    class Config:
        from_attributes = True
