from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)

    hash_password: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_modified: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default.now())


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))

    class SubscriptionStatus(enum.Enum):
        ACTIVE = "active"
        CANCELED = "canceled"
        TRIALING = "trialing"
        PAST_DUE = "past_due"

    # when you are going to be searching by something, make its index true
    status: Mapped[SubscriptionStatus] = mapped_column(index=True, default=SubscriptionStatus.ACTIVE)
    current_period_start: Mapped[datetime]
    current_period_end: Mapped[datetime] mapped_column(index=True)
    is_active: Mapped[boolean] = mapped_column(default=True)
    stripe_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    canceled_at: Mapped[datetime]
    trial_start: Mapped[datetime]
    trial_end: Mapped[datetime]

    #user.id for database and actual sql purposes
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # user for python purposes
    user: Mapped["User"] = relationship("User", back_populates="subscription")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_modified: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default.now())




    
    


