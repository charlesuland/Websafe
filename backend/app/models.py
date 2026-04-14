from sqlalchemy import JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from datetime import datetime
from typing import Optional
from app.database import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    phone: Mapped[str]
    email_verified: Mapped[bool] = mapped_column(default=False)
    hash_password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str]
    last_name: Mapped[str]
    stripe_customer_id: Mapped[str]

    # Added these two fields becaues they're referenced in schemes.py
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    TRIALING = "trialing"
    PAST_DUE = "past_due"


class Subscription(Base):
    __tablename__ = "subscriptions"
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    # when you are going to be searching by something, make its index true
    status: Mapped[SubscriptionStatus] = mapped_column(
        index=True, default=SubscriptionStatus.ACTIVE
    )
    current_period_start: Mapped[datetime]
    current_period_end: Mapped[datetime] = mapped_column(index=True)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    trial_start: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    trial_end: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    meta: Mapped[dict] = mapped_column(JSON)

    # user.id for database and actual sql purposes
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # user for python purposes
    # user: Mapped["User"] = relationship("User", back_populates="subscription")


class Duration(enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Plan(Base):
    __tablename__ = "plans"

    name: Mapped[str]
    price_in_cents: Mapped[int]
    duration: Mapped[Duration]
    description: Mapped[str]
    stripe_plan_id: Mapped[str]
    currency: Mapped[str] = mapped_column(default="USD")


# How to keep bank information


class Vendor(Base):
    __tablename__ = "vendors"
    business_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    owner: Mapped[int] = mapped_column(ForeignKey("users.id"))
    phone: Mapped[str]
    # stripe_id: Mapped[str]
    stripe_connect_id: Mapped[str]
    payouts_enabled: Mapped[bool] = mapped_column(default=False)
    requirements_due_for_payment: Mapped[str]


class VendorAdress(Base):
    __tablename__ = "vendor_addresses"
    vendor: Mapped[int] = mapped_column(ForeignKey("vendors.id"))
    house_number: Mapped[int]
    street_name: Mapped[str]
    city: Mapped[str]
    state: Mapped[str]
    postal_code: Mapped[str]


class Project(Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(index=True)
    vendor: Mapped[int] = mapped_column(ForeignKey("vendors.id"), nullable=False)
    is_live: Mapped[bool] = mapped_column(default=False)
    last_published: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    preview_image: Mapped[int] = mapped_column(ForeignKey("media_object_metadata.id"), nullable=True)

    preview = relationship(
        "MediaObjectMetadata",
        foreign_keys=[preview_image],
        lazy="joined"
    )


class ProjectPage(Base):
    __tablename__ = "project_pages"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(index=True)
    layout: Mapped[dict] = mapped_column(JSON)



# --- Security Log and Report Models ---
class SecurityLog(Base):
    __tablename__ = "security_logs"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column()
    details: Mapped[str] = mapped_column(nullable=True)
    ip_address: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class SecurityReport(Base):
    __tablename__ = "security_reports"
    report_id: Mapped[str] = mapped_column(unique=True, index=True)
    generated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=True)
    db_actions: Mapped[str] = mapped_column(nullable=True)  # JSON string or summary
    website_actions: Mapped[str] = mapped_column(nullable=True)  # JSON string or summary
    user_logins: Mapped[str] = mapped_column(nullable=True)  # JSON string or summary
    role_modifications: Mapped[str] = mapped_column(nullable=True)  # JSON string or summary
    xss_test_passed: Mapped[bool] = mapped_column(default=True)
    sqli_test_passed: Mapped[bool] = mapped_column(default=True)
    csrf_test_passed: Mapped[bool] = mapped_column(default=True)
    urgent: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(default="pass")  # pass/fail
    notes: Mapped[str] = mapped_column(nullable=True)
  

class ProjectProduct(Base):
    __tablename__ = "project_products"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)

    name: Mapped[str]
    description: Mapped[str]
    sale_price: Mapped[int]
    shipping_price: Mapped[int]
    currency: Mapped[str] = mapped_column(default="USD")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    stock: Mapped[int]
    product_image: Mapped[int] = mapped_column(ForeignKey("media_object_metadata.id"), nullable=True)
    alt_text: Mapped[str] = mapped_column(default="")

# Might not use this, not implemented yet
class ProductImage(Base):
    __tablename__ = "product_images"

    product_id: Mapped[int] = mapped_column(ForeignKey("project_products.id"), index=True)
    file_key: Mapped[str]
    position: Mapped[int]


class ProjectOrder(Base):
    __tablename__ = "project_orders"
    stripe_id: Mapped[str]
    item_price: Mapped[int]
    shipping_price: Mapped[int]
    currency: Mapped[str] = mapped_column(default="USD")
    payment_status: Mapped[bool]
    project: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    platform_fee_cents: Mapped[int]
    vendor_amount_cents: Mapped[int]
    meta: Mapped[dict] = mapped_column(JSON)


class ShippingStatus(enum.Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


class ProjectOrderItem(Base):
    __tablename__ = "project_order_items"

    item: Mapped[int] = mapped_column(ForeignKey("project_products.id"))
    order: Mapped[int] = mapped_column(ForeignKey("project_orders.id"))
    price_at_purchase: Mapped[int]
    tracking_number: Mapped[str]
    shipping_status: Mapped[ShippingStatus] = mapped_column(
        default=ShippingStatus.PENDING
    )


class ProjectCustomer(Base):
    __tablename__ = "project_customers"

    order: Mapped[int] = mapped_column(ForeignKey("project_orders.id"))

    first_name: Mapped[str]
    last_name: Mapped[str]
    phone: Mapped[str]
    email: Mapped[str]


class ProjectCustomerAdress(Base):
    __tablename__ = "project_customer_addresses"
    customer: Mapped[int] = mapped_column(ForeignKey("project_customers.id"))
    house_number: Mapped[int]
    street_name: Mapped[str]
    city: Mapped[str]
    state: Mapped[str]
    postal_code: Mapped[int]


class DraftProjectPage(Base):
    __tablename__ = "draft_project_pages"
    project: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str]
    layout: Mapped[dict] = mapped_column(JSON)


class MediaObjectMetadata(Base):
    __tablename__ = "media_object_metadata"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    file_key: Mapped[str]
    file_type: Mapped[str]
    file_size_bytes: Mapped[int]
    alt_text: Mapped[Optional[str]] = mapped_column(nullable=True)

    project = relationship(Project, foreign_keys=[project_id])
