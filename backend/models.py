from sqlalchemy import JSON, ForeignKey, func, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
import enum
from datetime import datetime


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(Boolean)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    phone: Mapped[str]
    hash_password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str]
    last_name: Mapped[str]


class Subscription(Base):
    __tablename__ = "subscriptions"
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))

    class SubscriptionStatus(enum.Enum):
        ACTIVE = "active"
        CANCELED = "canceled"
        TRIALING = "trialing"
        PAST_DUE = "past_due"

    # when you are going to be searching by something, make its index true
    status: Mapped[SubscriptionStatus] = mapped_column(
        index=True, default=SubscriptionStatus.ACTIVE
    )
    current_period_start: Mapped[datetime]
    current_period_end: Mapped[datetime] = mapped_column(index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    stripe_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    canceled_at: Mapped[datetime]
    trial_start: Mapped[datetime]
    trial_end: Mapped[datetime]

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


# need to give everything an is_active and update_at and created_at
# How to keep bank information


class Vendor(Base):
    __tablename__ = "vendors"
    business_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)

    phone: Mapped[int]
    stripe_id: Mapped[str]


class VendorAdress(Base):
    __tablename__ = "vendor_addresses"
    vendor: Mapped[int] = mapped_column(ForeignKey("vendors.id"))
    house_number: Mapped[int]
    street_name: Mapped[str]
    city: Mapped[str]
    state: Mapped[str]
    postal_code: Mapped[int]


class Project(Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(index=True)
    owner: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_live: Mapped[bool] = mapped_column(default=False)
    last_published: Mapped[datetime]


class ProjectPage(Base):
    __tablename__ = "projects_pages"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(index=True)
    layout: Mapped[dict] = mapped_column(JSON)


#class PageComponent(Base):
#    __tablename__ = "page_components"
#
#    page_id: Mapped[int] = mapped_column(ForeignKey("project_pages.id"), index=True)
#    layout: Mapped[dict] = mapped_column(JSON)


class ProjectProduct(Base):
    __tablename__ = "project_products"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str]
    description: Mapped[str]
    sale_price: Mapped[int]
    shipping_price: Mapped[int]


class ProjectProductVariation(Base):
    __tablename__ = "project_product_variations"

    product_id: Mapped[int] = mapped_column(ForeignKey("project_products.id"))
    name: Mapped[str]
    description: Mapped[str]
    stock: Mapped[int]

    image_file_name: Mapped[str]


class ProjectOrder(Base):
    __tablename__ = "project_orders"
    stripe_id: Mapped[str]
    total_price: Mapped[int]
    payment_status: Mapped[bool]


class ProjectOrderItem(Base):
    __tablename__ = "project_order_items"

    item: Mapped[int] = mapped_column(ForeignKey("project_product_variations.id"))
    order: Mapped[int] = mapped_column(ForeignKey("project_orders.id"))


class ProjectCustomer(Base):
    __tablename__ = "project_customers"

    order: Mapped[int] = mapped_column(ForeignKey("project_orders.id"))

    first_name: Mapped[str]
    last_name: Mapped[str]
    phone: Mapped[int]
    email: Mapped[str]


class ProjectCustomerAdress(Base):
    __tablename__ = "project_customer_addresses"
    vendor: Mapped[int] = mapped_column(ForeignKey("project_customers.id"))
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
#class DraftProjectComponents(Base):
#    __tablename__ = "draft_project_components"
#    page_id: Mapped[int] = mapped_column(ForeignKey("project_pages.id"), index=True)
#    layout: Mapped[dict] = mapped_column(JSON)
